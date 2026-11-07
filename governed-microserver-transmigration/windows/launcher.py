"""Strict Windows candidate worker launcher. No relaxed fallback.

This implementation is a Windows *candidate* until tested on Win11 LTSC.
CreateProcessW is suspended; kernel token/job evidence is checked before resume.
No arbitrary command or caller-provided AppContainer capabilities are accepted.
"""
import ctypes
import os
from pathlib import Path
import subprocess
import sys
import threading

from microtrans.protocol import (ContractRefusal, canonical_bytes, strict_json,
                                 MAX_INPUT_BYTES, MAX_RESPONSE_BYTES)
from .policy import (select_profile, preflight, MAX_PROCESS_COUNT,
                     MAX_WORKER_MEMORY, MAX_WORKER_SECONDS)
from . import native as n


def _fail(code):
    raise ContractRefusal(code, 'strict Windows worker could not satisfy boundary')


def _handle(h):
    value = getattr(h, 'value', h)
    return value is not None and value not in (0, n.INVALID_HANDLE_VALUE)


def _close(handle):
    if sys.platform == 'win32' and _handle(handle):
        n.CloseHandle(n.HANDLE(getattr(handle, 'value', handle)))


def _make_pipe():
    sa = n.SECURITY_ATTRIBUTES(ctypes.sizeof(n.SECURITY_ATTRIBUTES), None, True)
    rd, wr = n.HANDLE(), n.HANDLE()
    n.check(n.CreatePipe(ctypes.byref(rd), ctypes.byref(wr), ctypes.byref(sa), 0), 'PIPE_CREATE_FAILED')
    return rd, wr


def _profile_attr(profile_sid, inherited):
    count = n.SIZE_T(0)
    n.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(count))
    n.check(0 < count.value <= 65536, 'ATTRIBUTE_LIST_SIZE')
    raw = ctypes.create_string_buffer(count.value)
    attr = ctypes.cast(raw, n.P)
    n.check(n.InitializeProcThreadAttributeList(attr, 2, 0, ctypes.byref(count)), 'ATTRIBUTE_LIST_INIT_FAILED')
    sc = n.SECURITY_CAPABILITIES(profile_sid, None, 0, 0)
    handles = (n.HANDLE * len(inherited))(*inherited)
    try:
        n.check(n.UpdateProcThreadAttribute(attr, 0, n.PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES,
                                            ctypes.byref(sc), ctypes.sizeof(sc), None, None),
                'SECURITY_CAPABILITIES_FAILED')
        n.check(n.UpdateProcThreadAttribute(attr, 0, n.PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
                                            handles, ctypes.sizeof(handles), None, None),
                'HANDLE_ALLOWLIST_FAILED')
        return raw, attr, sc, handles
    except BaseException:
        n.DeleteProcThreadAttributeList(attr)
        raise


def _job():
    h = n.CreateJobObjectW(None, None)
    n.check(_handle(h), 'JOB_CREATE_FAILED')
    try:
        info = n.EXTENDED_LIMIT()
        info.BasicLimitInformation.LimitFlags = (n.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE |
            n.JOB_OBJECT_LIMIT_ACTIVE_PROCESS | n.JOB_OBJECT_LIMIT_PROCESS_MEMORY |
            n.JOB_OBJECT_LIMIT_JOB_MEMORY)
        info.BasicLimitInformation.ActiveProcessLimit = MAX_PROCESS_COUNT
        info.ProcessMemoryLimit = MAX_WORKER_MEMORY
        info.JobMemoryLimit = MAX_WORKER_MEMORY
        n.check(n.SetInformationJobObject(h, n.JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
                                          ctypes.byref(info), ctypes.sizeof(info)), 'JOB_LIMITS_FAILED')
        return h
    except BaseException:
        _close(h)
        raise


def _reader(handle, output, faults):
    import msvcrt
    try:
        fd = msvcrt.open_osfhandle(handle.value, os.O_RDONLY | os.O_BINARY)
        with os.fdopen(fd, 'rb', buffering=0) as stream:
            while True:
                chunk = stream.read(8192)
                if not chunk:
                    break
                output.extend(chunk)
                if len(output) > MAX_RESPONSE_BYTES:
                    faults.append('REPLY_SIZE')
                    break
    except (OSError, ValueError):
        faults.append('PIPE_READ_FAILED')


def _writer(handle, payload, faults):
    import msvcrt
    try:
        fd = msvcrt.open_osfhandle(handle.value, os.O_WRONLY | os.O_BINARY)
        with os.fdopen(fd, 'wb', buffering=0) as stream:
            stream.write(payload)
    except (OSError, ValueError):
        faults.append('PIPE_WRITE_FAILED')


def invoke(service, envelope):
    """One request/response over broker-owned pipes, bound by a Windows Job."""
    preflight(service)
    profile = select_profile(service)
    data = canonical_bytes(envelope) + b'\n'
    if len(data) > MAX_INPUT_BYTES:
        _fail('REQUEST_TOO_LARGE')

    sid = n.HANDLE()
    job = n.HANDLE()
    process = n.PROCESS_INFORMATION()
    attr = None
    inherited = []
    local = []
    owned = []
    output = bytearray()
    faults = []
    try:
        sid = n.get_profile_sid(profile)
        job = _job()
        # Each pipe is created inheritable, then the parent's ends have
        # HANDLE_FLAG_INHERIT cleared; STARTUPINFOEX allowlists exactly 3 ends.
        in_rd, in_wr = _make_pipe()
        inherited.append(in_rd)
        owned.append(in_wr)
        out_rd, out_wr = _make_pipe()
        owned.append(out_rd)
        inherited.append(out_wr)
        sa = n.SECURITY_ATTRIBUTES(ctypes.sizeof(n.SECURITY_ATTRIBUTES), None, True)
        nul = n.CreateFileW('NUL', 0x40000000, 3, ctypes.byref(sa), 3, 0x80, None)
        n.check(_handle(nul), 'NULL_DEVICE_FAILED')
        inherited.append(nul)
        for h in owned:
            n.check(n.SetHandleInformation(h, n.HANDLE_FLAG_INHERIT, 0), 'PIPE_INHERIT_FAILED')
        raw, attr, sc, harray = _profile_attr(sid, inherited)
        startup = n.STARTUPINFOEXW()
        startup.StartupInfo.cb = ctypes.sizeof(startup)
        startup.StartupInfo.dwFlags = n.STARTF_USESTDHANDLES
        startup.StartupInfo.hStdInput = in_rd
        startup.StartupInfo.hStdOutput = out_wr
        startup.StartupInfo.hStdError = nul
        startup.lpAttributeList = attr
        root = Path(__file__).resolve().parent.parent
        # -I disables Python environment/user-site injection. The path is
        # trusted release code and inserted explicitly, not read from a request.
        bootstrap = ("import sys;sys.path.insert(0," + repr(str(root)) + ");"
                     "from runtime.windows_entry import main;raise SystemExit(main())")
        argv = [sys.executable, '-I', '-B', '-c', bootstrap, service]
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        # No full inherited environment: block is broker-authored and bounded.
        winbuf = ctypes.create_unicode_buffer(32768)
        winlen = n.GetWindowsDirectoryW(winbuf, len(winbuf))
        n.check(winlen and winlen < len(winbuf), 'WINDOWS_DIRECTORY_UNAVAILABLE')
        environ = {'SystemRoot': winbuf.value,
                   'WINDIR': winbuf.value,
                   'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
                   'PYTHONIOENCODING': 'utf-8', 'PYTHONHASHSEED': '0'}
        env = ctypes.create_unicode_buffer(''.join(k + '=' + v + '\0' for k, v in sorted(environ.items())) + '\0')
        flags = (n.CREATE_SUSPENDED | n.CREATE_NO_WINDOW |
                 n.CREATE_UNICODE_ENVIRONMENT | n.EXTENDED_STARTUPINFO_PRESENT)
        n.check(n.CreateProcessW(str(Path(sys.executable).resolve()), command,
                                 None, None, True, flags, env, str(root),
                                 ctypes.byref(startup), ctypes.byref(process)),
                'WINDOWS_PROCESS_LAUNCH_FAILED')
        # No uncontained Python worker code has executed yet.
        n.check(n.AssignProcessToJobObject(job, process.hProcess), 'JOB_ASSIGNMENT_FAILED')
        n.verify_process(process.hProcess, sid, job)
        n.check(n.ResumeThread(process.hThread) != 0xFFFFFFFF, 'RESUME_FAILED')
        for h in inherited:
            _close(h)
        inherited.clear()
        # Readers and writers run concurrently to avoid pipe backpressure.
        writer = threading.Thread(target=_writer, args=(in_wr, data, faults), daemon=True)
        reader = threading.Thread(target=_reader, args=(out_rd, output, faults), daemon=True)
        # Ownership of these handles transfers to open_osfhandle worker threads.
        owned.clear()
        reader.start()
        writer.start()
        status = n.WaitForSingleObject(process.hProcess, MAX_WORKER_SECONDS * 1000)
        if status != n.WAIT_OBJECT_0:
            n.TerminateProcess(process.hProcess, 71)
            _fail('CHILD_TIMEOUT' if status == n.WAIT_TIMEOUT else 'CHILD_WAIT_FAILED')
        writer.join(timeout=1)
        reader.join(timeout=1)
        if writer.is_alive() or reader.is_alive():
            _fail('PIPE_NOT_DRAINED')
        if faults:
            _fail(faults[0])
        exit_code = n.DWORD()
        n.check(n.GetExitCodeProcess(process.hProcess, ctypes.byref(exit_code)), 'EXIT_QUERY_FAILED')
        if exit_code.value != 0:
            _fail('CHILD_FAILURE')
        if not output or len(output) > MAX_RESPONSE_BYTES:
            _fail('REPLY_SIZE')
        try:
            obj = strict_json(bytes(output))
        except ContractRefusal:
            _fail('MALFORMED_CHILD_REPLY')
        if not isinstance(obj, dict):
            _fail('BAD_CHILD_REPLY')
        return obj
    except ContractRefusal:
        raise
    except (OSError, ValueError, TypeError):
        _fail('WINDOWS_RUNTIME_FAILURE')
    finally:
        # Closing last job handle kills any still-running sandbox members.
        if _handle(job):
            _close(job)
        for h in owned + inherited:
            _close(h)
        if attr is not None:
            n.DeleteProcThreadAttributeList(attr)
        if _handle(process.hThread):
            _close(process.hThread)
        if _handle(process.hProcess):
            _close(process.hProcess)
        if _handle(sid):
            n.FreeSid(sid)
