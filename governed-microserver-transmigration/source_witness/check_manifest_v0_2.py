#!/usr/bin/env python3
"""Static check of candidate-only microserver/glue manifests. Not runtime or security attestation."""
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator


def check(schema_path, manifest_path):
    schema = json.loads(Path(schema_path).read_text(encoding='utf-8'))
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    issues = []
    issues.extend('schema: ' + e.message for e in Draft202012Validator(schema).iter_errors(manifest))
    if issues:
        return issues
    ids = set()
    operations = {}
    for server in manifest['microservers']:
        sid = server['server_id']
        if sid in ids:
            issues.append('duplicate server_id ' + sid)
        ids.add(sid)
        names = set()
        for op in server['operations']:
            name = op['name']
            if name in names:
                issues.append('duplicate operation ' + sid + '/' + name)
            names.add(name)
            operations[(sid,name)] = op
    edge_ids = set()
    graph = {sid:set() for sid in ids}
    for edge in manifest['glue']:
        eid = edge['edge_id']
        if eid in edge_ids:
            issues.append('duplicate edge_id ' + eid)
        edge_ids.add(eid)
        frm = (edge['from']['server_id'], edge['from']['operation'])
        to = (edge['to']['server_id'], edge['to']['operation'])
        if frm not in operations:
            issues.append(eid + ': missing from endpoint ' + str(frm))
        if to not in operations:
            issues.append(eid + ': missing to endpoint ' + str(to))
        if frm in operations and edge['input_schema_ref'] != operations[frm]['output_schema_ref']:
            issues.append(eid + ': producer output schema mismatch')
        if to in operations and edge['output_schema_ref'] != operations[to]['input_schema_ref']:
            issues.append(eid + ': consumer input schema mismatch')
        if edge['transformation'] == 'IDENTITY_ONLY' and edge['input_schema_ref'] != edge['output_schema_ref']:
            issues.append(eid + ': identity edge changes schema')
        if edge['kind']=='CRETE' and edge['join_rule'] != 'BREAK_BEFORE_MUTATION':
            issues.append(eid + ': CRETE requires break-before-mutation')
        if edge['kind']=='ORDINARY_GLUE' and edge['join_rule'] != 'NO_MUTATION':
            issues.append(eid + ': ordinary glue cannot claim Crete break semantics')
        if frm in operations and to in operations:
            graph[frm[0]].add(to[0])
    # This minimal candidate reference model forbids feedback edges; a later
    # explicitly scoped protocol may define bounded feedback without relaxing safety.
    state={}
    def walk(v):
        if state.get(v)==1:
            return True
        if state.get(v)==2:
            return False
        state[v]=1
        cyclic=any(walk(n) for n in graph.get(v, ()))
        state[v]=2
        return cyclic
    if any(walk(v) for v in graph if v not in state):
        issues.append('composition cycle (not admitted by minimal reference contract)')
    return issues

if __name__=='__main__':
    if len(sys.argv)!=3:
        raise SystemExit('usage: python check_manifest.py SCHEMA.json MANIFEST.json')
    errors=check(sys.argv[1],sys.argv[2])
    if errors:
        for error in errors:
            print('REJECT:',error)
        raise SystemExit(1)
    print('STATIC_CHECK_PASSED: schema, cross-references, type alignment, join rules, and acyclicity')
    print('NOT_PROVEN: runtime isolation, authority enforcement, source equivalence, Crete integrity, admission')
