"""Linux x86-64 kernel-enforced filesystem write denial via Landlock ABI >= 3.

This is an explicit narrow boundary, not a complete sandbox: it does not
prevent all read, IPC, ptrace, /proc, or device interactions. Do not call it
when the code path has already imported/executed untrusted worker modules.
"""
import ctypes
import os
import platform
import sys

# Linux x86_64 syscall numbers, as defined by asm-generic and x86_64 tables.
LANDLOCK_CREATE_RULESET = 444
LANDLOCK_RESTRICT_SELF = 446
LANDLOCK_CREATE_RULESET_VERSION = 1
PR_SET_NO_NEW_PRIVS = 38

# No allow rules: all handled write/mutation filesystem actions are denied.
WRITE_FILE = 1 << 1
REMOVE_DIR = 1 << 4
REMOVE_FILE = 1 << 5
MAKE_CHAR = 1 << 6
MAKE_DIR = 1 << 7
MAKE_REG = 1 << 8
MAKE_SOCK = 1 << 9
MAKE_FIFO = 1 << 10
MAKE_BLOCK = 1 << 11
MAKE_SYM = 1 << 12
REFER = 1 << 13    # ABI >= 2
TRUNCATE = 1 << 14 # ABI >= 3
HANDLED_FS = (WRITE_FILE | REMOVE_DIR | REMOVE_FILE | MAKE_CHAR | MAKE_DIR |
              MAKE_REG | MAKE_SOCK | MAKE_FIFO | MAKE_BLOCK | MAKE_SYM |
              REFER | TRUNCATE)

class Ruleset(ctypes.Structure):
    _fields_ = [("handled_access_fs", ctypes.c_uint64)]


class BoundaryFailure(RuntimeError):
    pass


def apply_write_deny():
    if sys.platform != 'linux' or platform.machine().lower() not in ('x86_64', 'amd64'):
        raise BoundaryFailure('LANDLOCK_PLATFORM_UNSUPPORTED')
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    abi = libc.syscall(ctypes.c_long(LANDLOCK_CREATE_RULESET),
                       ctypes.c_void_p(), ctypes.c_size_t(0),
                       ctypes.c_uint(LANDLOCK_CREATE_RULESET_VERSION))
    if abi < 3:
        raise BoundaryFailure('LANDLOCK_ABI_3_REQUIRED')
    attr = Ruleset(HANDLED_FS)
    fd = libc.syscall(ctypes.c_long(LANDLOCK_CREATE_RULESET),
                      ctypes.byref(attr), ctypes.sizeof(attr), ctypes.c_uint(0))
    if fd < 0:
        raise BoundaryFailure('LANDLOCK_RULESET_REFUSED')
    try:
        if libc.prctl(ctypes.c_int(PR_SET_NO_NEW_PRIVS), ctypes.c_ulong(1),
                      ctypes.c_ulong(0), ctypes.c_ulong(0), ctypes.c_ulong(0)) != 0:
            raise BoundaryFailure('NO_NEW_PRIVS_REFUSED')
        if libc.syscall(ctypes.c_long(LANDLOCK_RESTRICT_SELF), ctypes.c_int(fd),
                        ctypes.c_uint(0)) < 0:
            raise BoundaryFailure('LANDLOCK_ENFORCEMENT_REFUSED')
    finally:
        os.close(fd)
    return {'landlock_abi': int(abi), 'filesystem_write': 'KERNEL_DENIED',
            'filesystem_read': 'NOT_RESTRICTED'}
