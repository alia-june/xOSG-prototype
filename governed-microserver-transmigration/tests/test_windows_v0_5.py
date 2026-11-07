"""Cross-platform static/contract checks; NOT proof of Win32 runtime behavior."""
import sys
import unittest
from unittest.mock import patch

from microtrans.governed import enforce_os_available, run_governed
from microtrans.protocol import ContractRefusal
from windows.policy import PROFILE_BY_SERVICE, select_profile, preflight, MAX_PROCESS_COUNT, MAX_WORKER_MEMORY
from windows import launcher, native


class WindowsContractTests(unittest.TestCase):
    def test_two_distinct_static_profile_names(self):
        self.assertEqual(set(PROFILE_BY_SERVICE), {'schema-gate', 'graph-gate', 'boundary-probe'})
        self.assertEqual(len(set(PROFILE_BY_SERVICE.values())), 3)
        self.assertTrue(all(len(x) <= 64 for x in PROFILE_BY_SERVICE.values()))

    def test_reject_unknown_services(self):
        for name in ('cmd', '', 'graph-gate/../../', 'probe', 'schema-gate '):
            with self.subTest(name=name):
                with self.assertRaises(ContractRefusal):
                    select_profile(name)
        for bad in (None, 3, [], {}):
            with self.assertRaises(ContractRefusal):
                select_profile(bad)

    def test_windows_not_silently_emulated_on_linux(self):
        if sys.platform == 'win32':
            self.skipTest('non-Windows refusal test')
        with self.assertRaises(ContractRefusal) as c:
            preflight('schema-gate')
        self.assertEqual(c.exception.code, 'OS_BOUNDARY_UNAVAILABLE')
        with self.assertRaises(ContractRefusal):
            native.verify_current('Microtrans.SchemaGate.v05')

    def test_resource_ceiling_static(self):
        self.assertEqual(MAX_PROCESS_COUNT, 1)
        self.assertGreater(MAX_WORKER_MEMORY, 0)
        self.assertLessEqual(MAX_WORKER_MEMORY, 512 * 1024 * 1024)

    def test_parent_governed_unsupported_os_refuses(self):
        with patch('microtrans.governed.enforce_os_available', side_effect=ContractRefusal('OS_BOUNDARY_UNAVAILABLE', 'no boundary')):
            response = run_governed({}, request_id='win-test')
        self.assertEqual(response['decision'], 'REFUSED')
        self.assertEqual(response['admission'], 'NOT_ADMITTED')
        self.assertEqual(response['publication'], 'NOT_PUBLISHED')
        self.assertEqual(response['boundary'], 'SENTINEL_UNRESOLVED')

    def test_manual_profile_provision_no_implicit_use(self):
        from windows import profiles
        self.assertTrue(callable(profiles.provision))
        self.assertTrue(callable(launcher.invoke))
        self.assertNotIn('CreateProfile', launcher.invoke.__code__.co_names)


if __name__ == '__main__':
    unittest.main()
