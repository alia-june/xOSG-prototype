"""Explicit local profile provisioning; never called from validation launch."""
import argparse
import sys

from .policy import PROFILE_BY_SERVICE
from . import native as n


def provision():
    if sys.platform != 'win32':
        raise RuntimeError('WINDOWS_REQUIRED')
    for profile in PROFILE_BY_SERVICE.values():
        sid = n.P()
        result = n.CreateProfile(profile, profile, 'Candidate-only microtrans worker', None, 0, n.ctypes.byref(sid))
        try:
            # HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS) == 0x800700B7.
            if result not in (0, -2147024713):
                raise RuntimeError('PROFILE_CREATION_REFUSED: ' + profile + ': ' + hex(result & 0xFFFFFFFF))
            print(profile + ': ' + ('CREATED' if result == 0 else 'ALREADY_PRESENT'))
        finally:
            if sid.value:
                n.FreeSid(sid)


def main():
    parser = argparse.ArgumentParser(description='Explicit provisioning only: creates two per-user AppContainer profiles')
    parser.add_argument('--i-approve-profile-creation', action='store_true')
    args = parser.parse_args()
    if not args.i_approve_profile_creation:
        print('REFUSED: no profiles modified; supply --i-approve-profile-creation explicitly')
        return 1
    try:
        provision()
    except Exception as exc:
        print('REFUSED: ' + str(exc))
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
