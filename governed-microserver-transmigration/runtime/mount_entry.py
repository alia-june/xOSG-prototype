"""Trusted OS bootstrap for Linux x86_64 strict workers.

Launch *only inside* user, mount, and network namespaces. Mark existing
mounts read-only, then exec setpriv to irreversibly discard capabilities
and set no_new_privs before loading candidate microserver code.

This is not a fully contained general-purpose sandbox: reads and non-FS
IPC remain accessible; no assertion is made about untrusted native code.
"""
import subprocess
import os
import shutil
import sys


def mounts():
    records = []
    for line in open('/proc/self/mountinfo', encoding='utf-8'):
        parts = line.split(' ')
        if len(parts) < 7:
            raise RuntimeError('BAD_MOUNT_INFO')
        # mountinfo uses octal escape codes for whitespace and backslashes.
        target = parts[4]
        for a, b in ((r'\040', ' '), (r'\011', '\t'), (r'\012', '\n'), (r'\134', '\\')):
            target = target.replace(a, b)
        records.append((target, parts[5].split(',')))
    return records


def main():
    if sys.platform != 'linux' or len(sys.argv) != 2 or sys.argv[1] not in ('schema-gate','graph-gate','probe'):
        return 75
    # A caller-provided environment value is not a security assertion. The
    # actual remount and capability drop operations below must succeed.
    if os.environ.get('MICROTRANS_NETWORK_NAMESPACE') != 'REQUIRED':
        return 76
    for target, options in sorted(mounts(), key=lambda p: len(p[0]), reverse=True):
        if 'rw' not in options:
            continue
        p = subprocess.run(['/usr/bin/mount', '-o', 'remount,bind,ro', target],
                           stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=2, check=False)
        if p.returncode != 0:
            return 77
    if any('rw' in opts for _, opts in mounts()):
        return 78
    setpriv = shutil.which('setpriv')
    if not setpriv:
        return 79
    os.execv(setpriv, [setpriv, '--bounding-set=-all', '--inh-caps=-all',
                       '--ambient-caps=-all', '--no-new-privs', '--',
                       sys.executable, '-m', 'runtime.worker_entry', sys.argv[1]])
    return 80


if __name__ == '__main__':
    raise SystemExit(main())
