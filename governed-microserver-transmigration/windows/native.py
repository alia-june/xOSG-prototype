"""Windows AppContainer+JobObject broker primitives (unverified on Windows).

Win32 declarations are deliberately unavailable on non-Windows platforms.
Every failed kernel API call fails closed; there is no unrestricted retry.
"""
import ctypes
import os
import sys

from microtrans.protocol import ContractRefusal

if sys.platform == 'win32':
    import ctypes.wintypes as W

    K = ctypes.WinDLL('kernel32', use_last_error=True)
    A = ctypes.WinDLL('advapi32', use_last_error=True)
    U = ctypes.WinDLL('userenv', use_last_error=True)

    def api(lib, name, ret, *args):
        f = getattr(lib, name)
        f.restype = ret
        f.argtypes = list(args)
        return f

    P = ctypes.c_void_p
    DWORD = W.DWORD
    BOOL = W.BOOL
    SIZE_T = ctypes.c_size_t
    HANDLE = W.HANDLE
    HRESULT = ctypes.c_long

    GetWindowsDirectoryW = api(K, 'GetWindowsDirectoryW', W.UINT, W.LPWSTR, W.UINT)
    GetCurrentProcess = api(K, 'GetCurrentProcess', HANDLE)
    CreateJobObjectW = api(K, 'CreateJobObjectW', HANDLE, P, W.LPCWSTR)
    SetInformationJobObject = api(K, 'SetInformationJobObject', BOOL, HANDLE, ctypes.c_int, P, DWORD)
    AssignProcessToJobObject = api(K, 'AssignProcessToJobObject', BOOL, HANDLE, HANDLE)
    IsProcessInJob = api(K, 'IsProcessInJob', BOOL, HANDLE, HANDLE, ctypes.POINTER(BOOL))
    CloseHandle = api(K, 'CloseHandle', BOOL, HANDLE)
    TerminateProcess = api(K, 'TerminateProcess', BOOL, HANDLE, DWORD)
    ResumeThread = api(K, 'ResumeThread', DWORD, HANDLE)
    GetExitCodeProcess = api(K, 'GetExitCodeProcess', BOOL, HANDLE, ctypes.POINTER(DWORD))
    WaitForSingleObject = api(K, 'WaitForSingleObject', DWORD, HANDLE, DWORD)
    CreatePipe = api(K, 'CreatePipe', BOOL, ctypes.POINTER(HANDLE), ctypes.POINTER(HANDLE), P, DWORD)
    SetHandleInformation = api(K, 'SetHandleInformation', BOOL, HANDLE, DWORD, DWORD)
    CreateFileW = api(K, 'CreateFileW', HANDLE, W.LPCWSTR, DWORD, DWORD, P, DWORD, DWORD, HANDLE)
    InitializeProcThreadAttributeList = api(K, 'InitializeProcThreadAttributeList', BOOL, P, DWORD, DWORD, ctypes.POINTER(SIZE_T))
    UpdateProcThreadAttribute = api(K, 'UpdateProcThreadAttribute', BOOL, P, DWORD, SIZE_T, P, SIZE_T, P, P)
    DeleteProcThreadAttributeList = api(K, 'DeleteProcThreadAttributeList', None, P)
    CreateProcessW = api(K, 'CreateProcessW', BOOL, W.LPCWSTR, W.LPWSTR, P, P, BOOL, DWORD, P, W.LPCWSTR, P, P)
    OpenProcessToken = api(A, 'OpenProcessToken', BOOL, HANDLE, DWORD, ctypes.POINTER(HANDLE))
    GetTokenInformation = api(A, 'GetTokenInformation', BOOL, HANDLE, ctypes.c_int, P, DWORD, ctypes.POINTER(DWORD))
    EqualSid = api(A, 'EqualSid', BOOL, P, P)
    FreeSid = api(A, 'FreeSid', P, P)
    DeriveSid = api(U, 'DeriveAppContainerSidFromAppContainerName', HRESULT, W.LPCWSTR, ctypes.POINTER(P))
    CreateProfile = api(U, 'CreateAppContainerProfile', HRESULT, W.LPCWSTR, W.LPCWSTR, W.LPCWSTR, P, DWORD, ctypes.POINTER(P))

    class SECURITY_ATTRIBUTES(ctypes.Structure):
        _fields_ = [('nLength', DWORD), ('lpSecurityDescriptor', P), ('bInheritHandle', BOOL)]

    class SECURITY_CAPABILITIES(ctypes.Structure):
        _fields_ = [('AppContainerSid', P), ('Capabilities', P), ('CapabilityCount', DWORD), ('Reserved', DWORD)]

    class STARTUPINFOW(ctypes.Structure):
        _fields_ = [('cb', DWORD), ('lpReserved', W.LPWSTR), ('lpDesktop', W.LPWSTR),
                    ('lpTitle', W.LPWSTR), ('dwX', DWORD), ('dwY', DWORD),
                    ('dwXSize', DWORD), ('dwYSize', DWORD), ('dwXCountChars', DWORD),
                    ('dwYCountChars', DWORD), ('dwFillAttribute', DWORD), ('dwFlags', DWORD),
                    ('wShowWindow', W.WORD), ('cbReserved2', W.WORD),
                    ('lpReserved2', P), ('hStdInput', HANDLE), ('hStdOutput', HANDLE), ('hStdError', HANDLE)]

    class STARTUPINFOEXW(ctypes.Structure):
        _fields_ = [('StartupInfo', STARTUPINFOW), ('lpAttributeList', P)]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [('hProcess', HANDLE), ('hThread', HANDLE), ('dwProcessId', DWORD), ('dwThreadId', DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [(field, ctypes.c_uint64) for field in (
            'ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
            'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]

    class BASIC_LIMIT(ctypes.Structure):
        _fields_ = [('PerProcessUserTimeLimit', ctypes.c_int64), ('PerJobUserTimeLimit', ctypes.c_int64),
                    ('LimitFlags', DWORD), ('MinimumWorkingSetSize', SIZE_T),
                    ('MaximumWorkingSetSize', SIZE_T), ('ActiveProcessLimit', DWORD),
                    ('Affinity', SIZE_T), ('PriorityClass', DWORD), ('SchedulingClass', DWORD)]

    class EXTENDED_LIMIT(ctypes.Structure):
        _fields_ = [('BasicLimitInformation', BASIC_LIMIT), ('IoInfo', IO_COUNTERS),
                    ('ProcessMemoryLimit', SIZE_T), ('JobMemoryLimit', SIZE_T),
                    ('PeakProcessMemoryUsed', SIZE_T), ('PeakJobMemoryUsed', SIZE_T)]

    INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x8
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x200
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
    PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
    PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES = 0x00020009
    CREATE_SUSPENDED = 0x00000004
    CREATE_NO_WINDOW = 0x08000000
    CREATE_UNICODE_ENVIRONMENT = 0x00000400
    EXTENDED_STARTUPINFO_PRESENT = 0x00080000
    STARTF_USESTDHANDLES = 0x100
    HANDLE_FLAG_INHERIT = 1
    TOKEN_QUERY = 0x0008
    TOKEN_IS_APP_CONTAINER = 29
    TOKEN_CAPABILITIES = 30
    TOKEN_APP_CONTAINER_SID = 31
    STILL_ACTIVE = 259
    WAIT_OBJECT_0 = 0
    WAIT_TIMEOUT = 258


def refuse(code):
    raise ContractRefusal(code, 'Windows platform security boundary unavailable or refused')


def check(ok, code):
    if not ok:
        refuse(code)
    return ok


def get_profile_sid(name):
    if sys.platform != 'win32':
        refuse('OS_BOUNDARY_UNAVAILABLE')
    sid = P()
    # Derive is not provisioning: the broker never creates a profile as a side effect.
    check(DeriveSid(name, ctypes.byref(sid)) == 0 and sid.value, 'PROFILE_SID_UNAVAILABLE')
    return sid


def token_information(token, kind):
    length = DWORD()
    GetTokenInformation(token, kind, None, 0, ctypes.byref(length))
    check(0 < length.value <= 65536, 'TOKEN_QUERY_FAILED')
    buf = ctypes.create_string_buffer(length.value)
    check(GetTokenInformation(token, kind, buf, length, ctypes.byref(length)), 'TOKEN_QUERY_FAILED')
    return buf


def verify_process(process, sid, job):
    """Query kernel evidence *while process is suspended*. No JSON self-attestation."""
    if sys.platform != 'win32':
        refuse('OS_BOUNDARY_UNAVAILABLE')
    token = HANDLE()
    check(OpenProcessToken(process, TOKEN_QUERY, ctypes.byref(token)), 'PROCESS_TOKEN_OPEN_FAILED')
    try:
        is_container = token_information(token, TOKEN_IS_APP_CONTAINER)
        check(ctypes.cast(is_container, ctypes.POINTER(DWORD)).contents.value == 1, 'NOT_APPCONTAINER')
        caps = token_information(token, TOKEN_CAPABILITIES)
        check(ctypes.cast(caps, ctypes.POINTER(DWORD)).contents.value == 0, 'UNEXPECTED_CAPABILITIES')
        app_sid_buf = token_information(token, TOKEN_APP_CONTAINER_SID)
        app_sid = ctypes.cast(app_sid_buf, ctypes.POINTER(P)).contents.value
        check(app_sid and EqualSid(P(app_sid), sid), 'APPCONTAINER_SID_MISMATCH')
    finally:
        CloseHandle(token)
    member = BOOL()
    check(IsProcessInJob(process, job, ctypes.byref(member)) and member.value, 'JOB_MEMBERSHIP_FAILED')
    return True


def verify_current(profile):
    """Worker-side check is supplemental; parent verifies before ResumeThread."""
    if sys.platform != 'win32':
        refuse('OS_BOUNDARY_UNAVAILABLE')
    sid = get_profile_sid(profile)
    token = HANDLE()
    try:
        check(OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)), 'TOKEN_QUERY_FAILED')
        check(ctypes.cast(token_information(token, TOKEN_IS_APP_CONTAINER), ctypes.POINTER(DWORD)).contents.value == 1,
              'NOT_APPCONTAINER')
        check(ctypes.cast(token_information(token, TOKEN_CAPABILITIES), ctypes.POINTER(DWORD)).contents.value == 0,
              'UNEXPECTED_CAPABILITIES')
        b = token_information(token, TOKEN_APP_CONTAINER_SID)
        app_sid = ctypes.cast(b, ctypes.POINTER(P)).contents.value
        check(app_sid and EqualSid(P(app_sid), sid), 'APPCONTAINER_SID_MISMATCH')
        in_job = BOOL()
        check(IsProcessInJob(GetCurrentProcess(), None, ctypes.byref(in_job)) and in_job.value,
              'NOT_IN_JOB')
    finally:
        if token.value:
            CloseHandle(token)
        FreeSid(sid)
    return True
