"""Explicit Windows negative probe. Never auto-provisions or modifies project files."""
import argparse
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading

from .launcher import invoke


def probe():
    if sys.platform != 'win32':
        raise RuntimeError('OS_BOUNDARY_UNAVAILABLE')
    with tempfile.TemporaryDirectory(prefix='microtrans-protected-witness-') as tmp:
        path = Path(tmp) / 'protected.bin'
        path.write_bytes(b'IMMUTABLE_WITNESS')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(('127.0.0.1', 0))
            listener.listen(1)
            listener.settimeout(8)
            got_connection = threading.Event()
            def accept_one():
                try:
                    conn, _ = listener.accept()
                    got_connection.set()
                    conn.close()
                except OSError:
                    pass
            thread = threading.Thread(target=accept_one, daemon=True)
            thread.start()
            result = invoke('boundary-probe', {'disposable_path': str(path),
                                               'loopback_port': listener.getsockname()[1]})
            expected = {'file_write_denied': True, 'network_connect_denied': True,
                        'descendant_spawn_denied': True}
            witness_unchanged = path.read_bytes() == b'IMMUTABLE_WITNESS'
            is_pass = result == expected and witness_unchanged and not got_connection.is_set()
            return {'status': 'NEGATIVE_PROBES_PASSED_CANDIDATE' if is_pass else 'REFUSED',
                    'probe_result': result, 'witness_unchanged': witness_unchanged,
                    'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED'}
        finally:
            listener.close()


def main():
    parser = argparse.ArgumentParser(description='Explicit Windows AppContainer negative smoke probes')
    parser.add_argument('--i-approve-local-probes', action='store_true')
    args = parser.parse_args()
    if not args.i_approve_local_probes:
        print('REFUSED: no probes executed; approval switch missing')
        return 1
    try:
        result = probe()
    except Exception as ex:
        result = {'status': 'REFUSED', 'fault': type(ex).__name__,
                  'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED'}
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'NEGATIVE_PROBES_PASSED_CANDIDATE' else 1


if __name__ == '__main__':
    raise SystemExit(main())
