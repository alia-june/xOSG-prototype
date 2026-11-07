"""Strict boundary negative probes; used only in tests."""
import json
import os
import subprocess


def main():
    path = os.environ.get('MICROTRANS_PROBE_PATH', '')
    if not path or not os.path.isabs(path):
        return 73
    write_denied = False
    shm_write_denied = False
    remount_denied = False
    try:
        with open(path, 'wb') as stream:
            stream.write(b'MODIFIED')
    except OSError:
        write_denied = True
    try:
        with open('/dev/shm/microtrans-probe-will-not-create', 'wb') as stream:
            stream.write(b'CREATED')
    except OSError:
        shm_write_denied = True
    try:
        result = subprocess.run(['/usr/bin/mount', '-o', 'remount,bind,rw', '/'],
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, timeout=2, check=False)
        remount_denied = result.returncode != 0
    except (OSError, subprocess.TimeoutExpired):
        remount_denied = True
    try:
        net_ns = os.readlink('/proc/self/ns/net')
    except OSError:
        net_ns = 'SENTINEL_UNRESOLVED'
    result = {'write_denied': write_denied,
              'shm_write_denied': shm_write_denied,
              'remount_denied': remount_denied,
              'net_namespace': net_ns,
              'disposition': 'CANDIDATE_ONLY'}
    print(json.dumps(result, sort_keys=True))
    return 0 if all((write_denied, shm_write_denied, remount_denied)) and net_ns != 'SENTINEL_UNRESOLVED' else 74
