"""Transmigrated graph checks from the v0.2 source witness. Static only."""
from .protocol import digest, MAX_FAULTS, serve


def check_graph(manifest):
    # Direct invocations must be safe: refuse if prerequisite schema was not met.
    from .schema_validation import schema_faults
    if schema_faults(manifest):
        return {"faults": [{"code": "SCHEMA_PRECONDITION", "detail": "manifest did not satisfy the prerequisite schema"}],
                "data": {"kind": "sentinel", "code": "SENTINEL_ABSENT"}, "input_sha256": digest(manifest)}

    errors = []
    ids = set()
    operations = {}
    for server in manifest["microservers"]:
        sid = server["server_id"]
        if sid in ids:
            errors.append("duplicate server_id " + sid)
        ids.add(sid)
        names = set()
        for op in server["operations"]:
            name = op["name"]
            if name in names:
                errors.append("duplicate operation " + sid + "/" + name)
            names.add(name)
            operations[(sid, name)] = op
    edge_ids = set()
    graph = {sid: set() for sid in ids}
    for edge in manifest["glue"]:
        eid = edge["edge_id"]
        if eid in edge_ids:
            errors.append("duplicate edge_id " + eid)
        edge_ids.add(eid)
        src = (edge["from"]["server_id"], edge["from"]["operation"])
        dst = (edge["to"]["server_id"], edge["to"]["operation"])
        if src not in operations:
            errors.append(eid + ": missing from endpoint " + str(src))
        if dst not in operations:
            errors.append(eid + ": missing to endpoint " + str(dst))
        if src in operations and edge["input_schema_ref"] != operations[src]["output_schema_ref"]:
            errors.append(eid + ": producer output schema mismatch")
        if dst in operations and edge["output_schema_ref"] != operations[dst]["input_schema_ref"]:
            errors.append(eid + ": consumer input schema mismatch")
        if edge["transformation"] == "IDENTITY_ONLY" and edge["input_schema_ref"] != edge["output_schema_ref"]:
            errors.append(eid + ": identity edge changes schema")
        if edge["kind"] == "CRETE" and edge["join_rule"] != "BREAK_BEFORE_MUTATION":
            errors.append(eid + ": CRETE requires break-before-mutation")
        if edge["kind"] == "ORDINARY_GLUE" and edge["join_rule"] != "NO_MUTATION":
            errors.append(eid + ": ordinary glue cannot claim Crete break semantics")
        if src in operations and dst in operations:
            graph[src[0]].add(dst[0])

    # Iterative Kahn traversal replaces recursive v0.2 DFS (bounded by input bytes).
    from collections import deque
    indegree = {sid: 0 for sid in graph}
    for src, neighbours in graph.items():
        for dst in neighbours:
            indegree[dst] += 1
    queue = deque(sid for sid, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        sid = queue.popleft()
        visited += 1
        for dst in graph[sid]:
            indegree[dst] -= 1
            if indegree[dst] == 0:
                queue.append(dst)
    if visited != len(graph):
        errors.append("composition cycle (not admitted by minimal reference contract)")

    faults = [{"code": "GRAPH_VIOLATION", "detail": detail[:800]} for detail in errors[:MAX_FAULTS]]
    return {"faults": faults, "input_sha256": digest(manifest), "data": {
        "manifest_sha256": digest(manifest),
        "microserver_count": len(manifest["microservers"]),
        "glue_edge_count": len(manifest["glue"]),
        "graph_check": "STATIC_PASSED_NOT_ADMITTED"
    }} if not faults else {"faults": faults, "data": {"kind": "sentinel", "code": "SENTINEL_ABSENT"}, "input_sha256": digest(manifest)}


if __name__ == "__main__":
    serve("graph-gate", check_graph)
