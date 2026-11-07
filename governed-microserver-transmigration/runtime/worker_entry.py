"""Microserver entry: fail closed unless namespace mount and caps checks pass."""
import os
import sys


def secured():
    try:
        status = {}
        for line in open('/proc/self/status', encoding='utf-8'):
            if ':' in line:
                name, value = line.split(':', 1)
                status[name] = value.strip()
        for item in ('CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb'):
            if int(status[item], 16) != 0:
                return False
        if status.get('NoNewPrivs') != '1':
            return False
        with open('/proc/self/mountinfo', encoding='utf-8') as f:
            for line in f:
                if 'rw' in line.split(' ')[5].split(','):
                    return False
        return True
    except (OSError, ValueError, KeyError, IndexError):
        return False


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('schema-gate', 'graph-gate', 'probe'):
        return 70
    if not secured():
        return 72
    name = sys.argv[1]
    if name == 'probe':
        from .probe import main as probe_main
        return probe_main()
    # Only import worker implementations after kernel restrictions verified.
    if name == 'schema-gate':
        from microtrans.schema_gate import check_schema
        from microtrans.protocol import serve
        serve('schema-gate', check_schema)
    elif name == 'graph-gate':
        from microtrans.graph_gate import check_graph
        from microtrans.protocol import serve
        serve('graph-gate', check_graph)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
