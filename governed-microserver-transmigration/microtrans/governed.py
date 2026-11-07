"""v0.5 governed launcher: Linux v0.4 or Windows AppContainer candidate.

All other OSes refuse; neither implementation may silently downgrade.
Windows backend is code-only until independently tested on Windows LTSC.
"""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys

from .glue import compose, ROOT
from .protocol import ContractRefusal, canonical_bytes, digest, strict_json, MAX_INPUT_BYTES, MAX_RESPONSE_BYTES

PROTOCOL = '0.4.0'
ALLOWED_MODULES = {
    'schema-gate': 'microtrans.schema_gate',
    'graph-gate': 'microtrans.graph_gate',
}


def enforce_os_available():
    if sys.platform == 'win32':
        from windows.policy import preflight
        for service in ALLOWED_MODULES:
            preflight(service)
        return 'WINDOWS_APPCONTAINER_CANDIDATE'
    if sys.platform != 'linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise ContractRefusal('OS_BOUNDARY_UNAVAILABLE', 'strict containment not available on this OS')
    unshare = shutil.which('unshare')
    if not unshare:
        raise ContractRefusal('OS_BOUNDARY_UNAVAILABLE', 'unshare executable unavailable')
    return unshare


def _child_env():
    # Python dependency execution still receives inherited user filesystem read
    # access; avoids PYTHONPATH, user-site injection and bytecode writes.
    env = {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONNOUSERSITE': '1',
           'PYTHONIOENCODING': 'utf-8'}
    for key in ('SYSTEMROOT', 'WINDIR'):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def _run(cmd, payload, *, timeout=6, max_reply=MAX_RESPONSE_BYTES, env=None):
    data = canonical_bytes(payload) + b'\n'
    if len(data) > MAX_INPUT_BYTES:
        raise ContractRefusal('REQUEST_TOO_LARGE', 'IPC request exceeds source envelope limit')
    popen_kwargs = {
        'stdin': subprocess.PIPE, 'stdout': subprocess.PIPE, 'stderr': subprocess.DEVNULL,
        'cwd': ROOT, 'env': _child_env() if env is None else env,
    }
    if os.name == 'posix':
        popen_kwargs['start_new_session'] = True
    try:
        p = subprocess.Popen(cmd, **popen_kwargs)
    except OSError:
        raise ContractRefusal('CHILD_LAUNCH_FAILED', 'could not start bounded child process') from None
    try:
        # communicate() buffers output: maximum is checked after capture. For
        # untrusted worker this is not a true memory bound; see gap ledger.
        out, _ = p.communicate(data, timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == 'posix':
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            p.kill()
        p.communicate()
        raise ContractRefusal('CHILD_TIMEOUT', 'bounded child timed out') from None
    if p.returncode != 0:
        raise ContractRefusal('CHILD_FAILURE', 'child rejected request or containment failed')
    if not out or len(out) > max_reply:
        raise ContractRefusal('REPLY_SIZE', 'child response missing or too large')
    try:
        response = strict_json(out)
    except ContractRefusal:
        raise ContractRefusal('MALFORMED_CHILD_REPLY', 'child did not produce strict JSON') from None
    if not isinstance(response, dict):
        raise ContractRefusal('BAD_CHILD_REPLY', 'child response must be object')
    return response


def _invoke_bounded(service, manifest, request_id):
    if service not in ALLOWED_MODULES:
        raise ContractRefusal('SERVICE_NOT_ALLOWLISTED', 'no such permitted service')
    runtime_boundary = enforce_os_available()
    envelope = {
        'protocol_version': '0.3.0', 'request_id': request_id,
        'operation': {'schema-gate': 'validate_manifest_schema',
                      'graph-gate': 'validate_manifest_graph'}[service],
        'authority': {'mode': 'READ_ONLY_CANDIDATE', 'basis': 'EXPLICIT_LOCAL_INVOKER'},
        'payload': {'manifest': manifest}
    }
    if sys.platform == 'win32':
        from windows.launcher import invoke
        reply = invoke(service, envelope)
    else:
        env = _child_env()
        env['MICROTRANS_NETWORK_NAMESPACE'] = 'REQUIRED'
        # Namespace created before Python interpreter loads worker_entry.
        cmd = [runtime_boundary, '--user', '--map-root-user', '--mount', '--net',
               '--propagation', 'private', '--',
               sys.executable, '-m', 'runtime.mount_entry', service]
        reply = _run(cmd, envelope, timeout=7, env=env)
    expected = {'protocol_version', 'request_id', 'service_id', 'operation',
                'decision', 'disposition', 'admission', 'input_sha256', 'data', 'faults'}
    if set(reply) != expected:
        raise ContractRefusal('WORKER_REPLY_SHAPE', 'unexpected service response fields')
    for key, expected_value in {
        'protocol_version': '0.3.0', 'request_id': request_id, 'service_id': service,
        'operation': envelope['operation'], 'disposition': 'CANDIDATE_ONLY',
        'admission': 'NOT_ADMITTED'
    }.items():
        if reply.get(key) != expected_value:
            raise ContractRefusal('WORKER_REPLY_IDENTITY', 'worker identity/authority mismatch')
    if reply.get('decision') not in ('ACCEPTED', 'REFUSED') or not isinstance(reply.get('faults'), list):
        raise ContractRefusal('WORKER_REPLY_DECISION', 'invalid decision or faults')
    if reply['decision'] == 'ACCEPTED' and reply['faults'] or reply['decision'] == 'REFUSED' and not reply['faults']:
        raise ContractRefusal('WORKER_REPLY_DECISION', 'faults disagree with result')
    return reply


def _refusal(request_id, manifest, code):
    return {'protocol_version': PROTOCOL, 'request_id': request_id,
            'decision': 'REFUSED', 'disposition': 'CANDIDATE_ONLY',
            'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED',
            'manifest_sha256': digest(manifest) if isinstance(manifest, dict) else 'SENTINEL_UNRESOLVED',
            'boundary': 'SENTINEL_UNRESOLVED',
            'authority_result': 'SENTINEL_UNRESOLVED',
            'composition_result': 'SENTINEL_UNRESOLVED',
            'external_audit': 'SENTINEL_UNRESOLVED',
            'faults': [{'code': code}]}


def run_governed(manifest, request_id='governed-candidate-001',
                 authority_runner=None, worker_runner=None, validator_runner=None):
    """Wiring overrides solely for unit negative-injection; no dynamic service commands."""
    try:
        if not isinstance(manifest, dict):
            raise ContractRefusal('MANIFEST_SHAPE', 'manifest must be JSON object')
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 120:
            raise ContractRefusal('REQUEST_ID', 'request identifier invalid')
        # Strict mode can only operate where actual kernel restrictions exist.
        enforce_os_available()
        authority_runner = authority_runner or (lambda x: _run([sys.executable, '-m', 'authority.gate'], x))
        worker_runner = worker_runner or _invoke_bounded
        validator_runner = validator_runner or (lambda x: _run([sys.executable, '-m', 'external_validator.validator'], x, timeout=7))
        auth = authority_runner({
            'protocol_version': PROTOCOL, 'request_id': request_id,
            'actor': 'EXPLICIT_LOCAL_INVOKER_UNAUTHENTICATED',
            'capability': 'VALIDATE_MANIFEST_CANDIDATE',
            'authority_ceiling': 'READ_ONLY_CANDIDATE',
            'manifest_sha256': digest(manifest), 'manifest': manifest
        })
        if (auth.get('decision') != 'POLICY_PASSED_CANDIDATE' or
            auth.get('request_id') != request_id or auth.get('manifest_sha256') != digest(manifest) or
            auth.get('authority_ceiling') != 'READ_ONLY_CANDIDATE' or
            auth.get('allowed_stages') != ['schema-gate', 'graph-gate'] or
            auth.get('admission') != 'NOT_ADMITTED' or auth.get('publication') != 'NOT_PUBLISHED' or
            auth.get('faults') != []):
            raise ContractRefusal('POLICY_REFUSED', 'authority preflight refused candidate')
        original = compose(manifest, request_id=request_id, runner=worker_runner)
        result = validator_runner({
            'protocol_version': PROTOCOL, 'request_id': request_id,
            'manifest': manifest, 'authority_receipt': auth,
            'composition_receipt': original
        })
        if (result.get('decision') != 'INDEPENDENTLY_CHECKED_CANDIDATE' or
            result.get('request_id') != request_id or
            result.get('manifest_sha256') != digest(manifest) or
            result.get('semantic_result') != original['decision'] or
            result.get('admission') != 'NOT_ADMITTED' or
            result.get('publication') != 'NOT_PUBLISHED' or result.get('faults') != []):
            raise ContractRefusal('EXTERNAL_AUDIT_REFUSED', 'candidate audit failed or mismatched')
        return {'protocol_version': PROTOCOL, 'request_id': request_id,
                'decision': 'STATIC_PASSED' if original['decision'] == 'STATIC_PASSED' else 'REFUSED',
                'disposition': 'CANDIDATE_ONLY', 'admission': 'NOT_ADMITTED',
                'publication': 'NOT_PUBLISHED', 'manifest_sha256': digest(manifest),
                'boundary': ('WINDOWS_APPCONTAINER_ZERO_CAPS_JOB_CANDIDATE'
                             if sys.platform == 'win32' else 'STRICT_LINUX_READONLY_MOUNT_NETNS_CAPDROP'),
                'authority_result': auth['decision'], 'composition_result': original['decision'],
                'external_audit': result['decision'],
                'faults': original['faults']}
    except (ContractRefusal, TypeError, KeyError, ValueError) as exc:
        return _refusal(request_id, manifest, exc.code if isinstance(exc, ContractRefusal) else 'INVALID_GOVERNED_REQUEST')


def main():
    parser = argparse.ArgumentParser(description='Strict candidate-only governed microserver chain')
    parser.add_argument('manifest', help='read-only manifest path')
    parser.add_argument('--request-id', default='governed-candidate-001')
    args = parser.parse_args()
    try:
        manifest = strict_json(Path(args.manifest).read_bytes())
        receipt = run_governed(manifest, args.request_id)
    except (OSError, ContractRefusal):
        receipt = _refusal(args.request_id, 'SENTINEL_UNRESOLVED', 'SOURCE_INPUT_REFUSED')
    sys.stdout.buffer.write(canonical_bytes(receipt) + b'\n')
    return 0 if receipt['decision'] == 'STATIC_PASSED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
