"""Isolated diagnostic worker, not part of the manifest validation graph.

Only attempts harmless operations against a caller-created disposable test file,
a caller-owned listening TCP port, and a child-process creation. A successful
unauthorized operation reports failure rather than being hidden.
"""
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def main():
    try:
        raw = sys.stdin.buffer.read(2048)
        request = json.loads(raw)
        if (set(request) != {'disposable_path', 'loopback_port'} or
            not isinstance(request['disposable_path'], str) or
            not isinstance(request['loopback_port'], int) or
            not 1 <= request['loopback_port'] <= 65535):
            return 91
        # Refuse arbitrary target paths and any witness that doesn't match
        # the exact expected disposable test-file shape and bytes.
        witness = Path(request['disposable_path'])
        if (witness.name != 'protected.bin' or
            not witness.parent.name.startswith('microtrans-protected-witness-')):
            return 93
        denied_file = False
        try:
            with open(request['disposable_path'], 'ab') as f:
                f.write(b'UNEXPECTED_WRITE')
        except (OSError, PermissionError):
            denied_file = True
        denied_network = False
        try:
            with socket.create_connection(('127.0.0.1', request['loopback_port']), timeout=1):
                denied_network = False
        except OSError:
            denied_network = True
        denied_child = False
        try:
            p = subprocess.run([os.environ.get('ComSpec', r'C:\Windows\System32\cmd.exe'), '/c', 'exit', '0'],
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=2)
            denied_child = p.returncode != 0
        except (OSError, subprocess.TimeoutExpired):
            denied_child = True
        result = {'file_write_denied': denied_file, 'network_connect_denied': denied_network,
                  'descendant_spawn_denied': denied_child}
        sys.stdout.write(json.dumps(result, sort_keys=True, separators=(',', ':')) + '\n')
        return 0
    except Exception:
        return 92
