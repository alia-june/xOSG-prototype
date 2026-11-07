"""New v0.4 negative and independent audit checks; no admission tests."""
import copy
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from authority.gate import decide, canonical as gate_canonical
from external_validator.validator import audit, independently_valid
from microtrans.glue import compose
from microtrans.governed import run_governed, _run
from microtrans.protocol import ContractRefusal, digest

ROOT = Path(__file__).resolve().parent.parent


def fixture(name='source_manifest_v0_2.json'):
    return json.loads((ROOT / 'examples' / name).read_text())


def policy_request(manifest, request_id='test-004'):
    return {'protocol_version': '0.4.0', 'request_id': request_id,
            'actor': 'EXPLICIT_LOCAL_INVOKER_UNAUTHENTICATED',
            'capability': 'VALIDATE_MANIFEST_CANDIDATE',
            'authority_ceiling': 'READ_ONLY_CANDIDATE',
            'manifest_sha256': digest(manifest), 'manifest': manifest}


class PolicyTests(unittest.TestCase):
    def test_policy_valid_is_candidate_only(self):
        r = decide(policy_request(fixture()))
        self.assertEqual(r['decision'], 'POLICY_PASSED_CANDIDATE')
        self.assertEqual(r['allowed_stages'], ['schema-gate','graph-gate'])
        self.assertEqual(r['admission'], 'NOT_ADMITTED')

    def test_policy_refuses_authority_escalation(self):
        for key, value in [('authority_ceiling','FULL_CONTROL'),
                           ('actor','ANONYMOUS_REMOTE'),
                           ('capability','RUN_COMMAND')]:
            with self.subTest(key=key):
                q = policy_request(fixture())
                q[key] = value
                with self.assertRaises(ValueError):
                    decide(q)

    def test_policy_digest_binding(self):
        q = policy_request(fixture())
        q['manifest_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'DIGEST_MISMATCH'):
            decide(q)

    def test_policy_rejects_extra_operation(self):
        q = policy_request(fixture())
        q['execute'] = True
        with self.assertRaises(ValueError):
            decide(q)

    def test_policy_json_refuses_duplicate_and_null(self):
        for data in [b'{"x":null}', b'{"a":1,"a":2}']:
            p = subprocess.run([sys.executable, '-m', 'authority.gate'],
                               cwd=ROOT, input=data, capture_output=True, timeout=8)
            r = json.loads(p.stdout)
            self.assertEqual(r['decision'], 'REFUSED')
            self.assertEqual(r['admission'], 'NOT_ADMITTED')


class IndependentAuditTests(unittest.TestCase):
    def valid_triplet(self):
        m = fixture()
        a = decide(policy_request(m))
        c = compose(m, request_id='test-004')
        return m, a, c

    def test_independent_checker_matches_source_corpus(self):
        # Same 19 historical inputs, independently traversed graph semantics.
        from tests.test_transmigration import cases, witness, SCHEMA
        for name, manifest in cases():
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as tempdir:
                    reference_path = Path(tempdir) / 'manifest.json'
                    reference_path.write_text(json.dumps(manifest), encoding='utf-8')
                    source_accepted = not witness.check(SCHEMA, reference_path)
                self.assertEqual(independently_valid(manifest), source_accepted)

    def test_external_checker_independent_graph_path(self):
        m = fixture()
        self.assertTrue(independently_valid(m))
        m['glue'][0]['to']['server_id'] = 'not-present'
        self.assertFalse(independently_valid(m))

    def test_external_audit_accepts_correct_candidate_evidence(self):
        m, a, c = self.valid_triplet()
        self.assertEqual(audit({'protocol_version':'0.4.0', 'request_id':'test-004',
                                'manifest':m, 'authority_receipt':a,
                                'composition_receipt':c})['decision'], 'INDEPENDENTLY_CHECKED_CANDIDATE')

    def test_external_audit_refuses_forged_success_on_bad_manifest(self):
        m, a, c = self.valid_triplet()
        m['glue'][0]['to']['server_id'] = 'missing'
        a = decide(policy_request(m))
        c['manifest_sha256'] = digest(m)
        with self.assertRaisesRegex(ValueError, 'SEMANTIC_DECISION_MISMATCH'):
            audit({'protocol_version':'0.4.0','request_id':'test-004',
                   'manifest':m,'authority_receipt':a,'composition_receipt':c})

    def test_external_audit_refuses_wrong_authority(self):
        m, a, c = self.valid_triplet()
        a['authority_ceiling'] = 'FULL_CONTROL'
        with self.assertRaises(ValueError):
            audit({'protocol_version':'0.4.0','request_id':'test-004',
                   'manifest':m,'authority_receipt':a,'composition_receipt':c})

    def test_external_audit_refuses_publication(self):
        m, a, c = self.valid_triplet()
        c['publication'] = 'PUBLISHED'
        with self.assertRaisesRegex(ValueError, 'COMPOSITION_AUTHORITY_MISMATCH'):
            audit({'protocol_version':'0.4.0','request_id':'test-004',
                   'manifest':m,'authority_receipt':a,'composition_receipt':c})


class StrictKernelTests(unittest.TestCase):
    def supported(self):
        if sys.platform != 'linux' or platform.machine() not in ('x86_64', 'amd64'):
            self.skipTest('Linux x86_64-only strict boundary')
        test = subprocess.run(['unshare','-Urn','true'], timeout=4, capture_output=True)
        if test.returncode:
            self.skipTest('Linux user/network namespaces unavailable')

    def test_kernel_denies_writes_remount_and_separates_network(self):
        self.supported()
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'protected-source.bin'
            file.write_bytes(b'READ_ONLY_WITNESS')
            env = os.environ.copy()
            env.update({'MICROTRANS_NETWORK_NAMESPACE':'REQUIRED',
                        'MICROTRANS_PROBE_PATH':str(file),
                        'PYTHONDONTWRITEBYTECODE':'1'})
            result = subprocess.run(['unshare','--user','--map-root-user','--mount',
                                     '--net','--propagation','private','--',
                                     sys.executable,'-m','runtime.mount_entry','probe'],
                                    cwd=ROOT, capture_output=True, env=env, timeout=12)
            self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
            outcome = json.loads(result.stdout)
            for prop in ('write_denied','shm_write_denied','remount_denied'):
                self.assertTrue(outcome[prop], prop)
            self.assertEqual(file.read_bytes(), b'READ_ONLY_WITNESS')
            self.assertNotEqual(outcome['net_namespace'], os.readlink('/proc/self/ns/net'))

    def test_worker_without_bootstrap_is_denied(self):
        x = subprocess.run([sys.executable,'-m','runtime.worker_entry','schema-gate'],
                           cwd=ROOT, capture_output=True, timeout=5)
        self.assertNotEqual(x.returncode, 0)

    def test_linux_governed_valid_chain(self):
        self.supported()
        r = run_governed(fixture('implementation_manifest_v0_3.json'))
        self.assertEqual(r['decision'], 'STATIC_PASSED')
        self.assertEqual(r['external_audit'],'INDEPENDENTLY_CHECKED_CANDIDATE')
        self.assertEqual(r['admission'],'NOT_ADMITTED')
        self.assertEqual(r['publication'],'NOT_PUBLISHED')

    def test_linux_governed_refuses_bad_graph(self):
        self.supported()
        m = fixture()
        m['glue'][0]['to']['server_id'] = 'unknown'
        r = run_governed(m)
        self.assertEqual(r['decision'], 'REFUSED')
        self.assertEqual(r['composition_result'], 'REFUSED')
        self.assertEqual(r['admission'], 'NOT_ADMITTED')

    def test_fail_closed_on_unsupported_os(self):
        with patch('microtrans.governed.enforce_os_available', side_effect=ContractRefusal('OS_BOUNDARY_UNAVAILABLE','unsupported')):
            r = run_governed(fixture())
        self.assertEqual(r['decision'], 'REFUSED')
        self.assertEqual(r['faults'][0]['code'], 'OS_BOUNDARY_UNAVAILABLE')

    def test_forged_authority_before_dispatch_stops_workers(self):
        called = []
        def malicious_authority(request):
            out = decide(request)
            out['authority_ceiling'] = 'FULL_CONTROL'
            return out
        def worker(*args):
            called.append('worker')
            raise AssertionError('worker must not execute')
        r = run_governed(fixture(), authority_runner=malicious_authority, worker_runner=worker)
        self.assertEqual(r['decision'], 'REFUSED')
        self.assertEqual(r['faults'][0]['code'], 'POLICY_REFUSED')
        self.assertEqual(called, [])

    def test_forged_validator_cannot_admit(self):
        m = fixture()
        def wrong_audit(_):
            return {'decision':'INDEPENDENTLY_CHECKED_CANDIDATE', 'request_id':'governed-candidate-001',
                    'manifest_sha256':digest(m), 'semantic_result':'STATIC_PASSED',
                    'admission':'ADMITTED','publication':'PUBLISHED','faults':[]}
        r = run_governed(m, validator_runner=wrong_audit)
        self.assertEqual(r['decision'],'REFUSED')
        self.assertEqual(r['faults'][0]['code'],'EXTERNAL_AUDIT_REFUSED')


if __name__ == '__main__':
    unittest.main()
