"""Static v0.5 Windows candidate-only launch policy. No speculative permissions."""
from pathlib import Path
import sys
from microtrans.protocol import ContractRefusal

PROFILE_BY_SERVICE = {
    'schema-gate': 'Microtrans.SchemaGate.v05',
    'graph-gate': 'Microtrans.GraphGate.v05',
    'boundary-probe': 'Microtrans.BoundaryProbe.v05',
}
# OS sandbox distinguishes children; authority gate/independent auditor remain
# trusted broker subprocesses. This is not a claim of independent custody.
BOUNDARY = 'WINDOWS_APPCONTAINER_ZERO_CAPS_JOB_CANDIDATE'
MAX_WORKER_MEMORY = 512 * 1024 * 1024
MAX_PROCESS_COUNT = 1
MAX_WORKER_SECONDS = 7


def select_profile(service):
    if type(service) is not str or service not in PROFILE_BY_SERVICE:
        raise ContractRefusal('SERVICE_NOT_ALLOWLISTED', 'unknown Windows worker service')
    return PROFILE_BY_SERVICE[service]


def preflight(service, *, platform=None):
    if (platform or sys.platform) != 'win32':
        raise ContractRefusal('OS_BOUNDARY_UNAVAILABLE', 'Windows AppContainer requires a real Windows host')
    select_profile(service)
    # Windows 11 LTSC 2024 is build 26100; this checks API generation, not edition.
    version = sys.getwindowsversion()
    if version.major != 10 or version.build < 26100:
        raise ContractRefusal('WINDOWS_BUILD_UNSUPPORTED', 'Windows 11 24H2 / LTSC 2024 or newer required')
    if not Path(sys.executable).is_absolute() or not Path(sys.executable).is_file():
        raise ContractRefusal('PYTHON_BINARY_UNAVAILABLE', 'verified absolute Python runtime required')
    return True
