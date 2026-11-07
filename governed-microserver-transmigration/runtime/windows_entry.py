"""Windows candidate worker. Refuse before importing service code if unsafe."""
import sys


def main():
    if sys.platform != 'win32' or len(sys.argv) != 2:
        return 81
    service = sys.argv[1]
    from windows.policy import select_profile
    from windows.native import verify_current
    try:
        profile = select_profile(service)
        verify_current(profile)
    except Exception:
        return 82
    if service == 'schema-gate':
        from microtrans.schema_gate import check_schema
        from microtrans.protocol import serve
        serve(service, check_schema)
    elif service == 'graph-gate':
        from microtrans.graph_gate import check_graph
        from microtrans.protocol import serve
        serve(service, check_graph)
    elif service == 'boundary-probe':
        from runtime.windows_probe import main as probe_main
        return probe_main()
    else:
        return 83
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
