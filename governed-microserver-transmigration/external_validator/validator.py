"""Independently coded semantic audit, invoked as a separate process.

No imports from microtrans/ or authority/. Shares pinned manifest schema only.
The checker is an executable candidate audit, NOT an external trust anchor.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / 'contracts' / 'manifest_v0_2.schema.json'
REQUIRED = {'protocol_version', 'request_id', 'manifest', 'authority_receipt', 'composition_receipt'}


def unique(pairs):
    d = {}
    for key, value in pairs:
        if key in d:
            raise ValueError('DUPLICATE_JSON_KEY')
        d[key] = value
    return d


def constant(_):
    raise ValueError('NON_STANDARD_NUMBER')


def refuse_null(obj):
    pending = [obj]
    while pending:
        item = pending.pop()
        if item is None or isinstance(item, float) and not math.isfinite(item):
            raise ValueError('NULL_OR_NONFINITE')
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def fingerprint(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def independently_valid(manifest):
    """Independent graph walk and invariants; uses shared declarative schema."""
    if not isinstance(manifest, dict):
        return False
    schema = json.loads(SCHEMA.read_text('utf-8'))
    if not Draft202012Validator(schema).is_valid(manifest):
        return False
    try:
        servers = {}
        for server in manifest['microservers']:
            sid = server['server_id']
            if sid in servers:
                return False
            ops = {}
            for operation in server['operations']:
                name = operation['name']
                if name in ops:
                    return False
                ops[name] = operation
            servers[sid] = ops
        links = set()
        adjacency = {sid: [] for sid in servers}
        for edge in manifest['glue']:
            key = edge['edge_id']
            if key in links:
                return False
            links.add(key)
            frm = edge['from']
            to = edge['to']
            a = servers[frm['server_id']][frm['operation']]
            b = servers[to['server_id']][to['operation']]
            if edge['input_schema_ref'] != a['output_schema_ref']:
                return False
            if edge['output_schema_ref'] != b['input_schema_ref']:
                return False
            if edge['transformation'] == 'IDENTITY_ONLY' and edge['input_schema_ref'] != edge['output_schema_ref']:
                return False
            if edge['kind'] == 'CRETE' and edge['join_rule'] != 'BREAK_BEFORE_MUTATION':
                return False
            if edge['kind'] == 'ORDINARY_GLUE' and edge['join_rule'] != 'NO_MUTATION':
                return False
            adjacency[frm['server_id']].append(to['server_id'])
        # Independently written iterative color DFS, not the v0.3 Kahn method.
        visited = set()
        for start in adjacency:
            if start in visited:
                continue
            active = set()
            stack = [(start, False)]
            while stack:
                node, exiting = stack.pop()
                if exiting:
                    active.remove(node)
                    visited.add(node)
                    continue
                if node in active:
                    return False
                if node in visited:
                    continue
                active.add(node)
                stack.append((node, True))
                for adjacent in reversed(adjacency[node]):
                    if adjacent in active:
                        return False
                    if adjacent not in visited:
                        stack.append((adjacent, False))
        return True
    except (KeyError, TypeError, ValueError):
        return False


def audit(req):
    if not isinstance(req, dict) or set(req) != REQUIRED or req['protocol_version'] != '0.4.0':
        raise ValueError('AUDIT_REQUEST_SHAPE')
    rid = req['request_id']
    if not isinstance(rid, str) or not 1 <= len(rid) <= 180:
        raise ValueError('AUDIT_REQUEST_ID')
    m = req['manifest']
    ar = req['authority_receipt']
    cr = req['composition_receipt']
    if not isinstance(ar, dict) or not isinstance(cr, dict):
        raise ValueError('AUDIT_RECEIPT_SHAPE')
    identity = fingerprint(m)
    if ar.get('decision') != 'POLICY_PASSED_CANDIDATE' or ar.get('request_id') != rid or ar.get('manifest_sha256') != identity or ar.get('authority_ceiling') != 'READ_ONLY_CANDIDATE':
        raise ValueError('AUTHORITY_WITNESS_MISMATCH')
    if ar.get('allowed_stages') != ['schema-gate', 'graph-gate'] or ar.get('admission') != 'NOT_ADMITTED' or ar.get('publication') != 'NOT_PUBLISHED' or ar.get('faults') != []:
        raise ValueError('AUTHORITY_CEILING_MISMATCH')
    if cr.get('request_id') != rid or cr.get('manifest_sha256') != identity or cr.get('protocol_version') != '0.3.0':
        raise ValueError('COMPOSITION_IDENTITY_MISMATCH')
    if cr.get('admission') != 'NOT_ADMITTED' or cr.get('publication') != 'NOT_PUBLISHED' or cr.get('disposition') != 'CANDIDATE_ONLY':
        raise ValueError('COMPOSITION_AUTHORITY_MISMATCH')
    expected = independently_valid(m)
    expected_decision = 'STATIC_PASSED' if expected else 'REFUSED'
    if cr.get('decision') != expected_decision:
        raise ValueError('SEMANTIC_DECISION_MISMATCH')
    if expected:
        if cr.get('faults') != []:
            raise ValueError('CONTRADICTORY_FAULTS')
        if [t.get('service') for t in cr.get('transcript', [])] != ['schema-gate', 'graph-gate'] or any(t.get('decision') != 'ACCEPTED' or t.get('faults') for t in cr['transcript']):
            raise ValueError('INCOMPLETE_EXECUTION_TRACE')
    else:
        if not isinstance(cr.get('faults'), list) or not cr['faults']:
            raise ValueError('MISSING_REFUSAL_EVIDENCE')
    return {'protocol_version': '0.4.0', 'request_id': rid,
            'decision': 'INDEPENDENTLY_CHECKED_CANDIDATE',
            'semantic_result': expected_decision,
            'manifest_sha256': identity, 'admission': 'NOT_ADMITTED',
            'publication': 'NOT_PUBLISHED', 'faults': [],
            'validator_basis': 'SEPARATE_IMPLEMENTATION_SHARED_SCHEMA'}


def main():
    rid = 'SENTINEL_UNRESOLVED'
    try:
        raw = sys.stdin.buffer.read(8 * 1024 * 1024 + 1)
        if not raw or len(raw) > 8 * 1024 * 1024:
            raise ValueError('INPUT_LIMIT')
        req = json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=constant)
        refuse_null(req)
        if isinstance(req, dict) and isinstance(req.get('request_id'), str):
            rid = req['request_id'][:180]
        result = audit(req)
    except (ValueError, TypeError, KeyError, OSError, UnicodeError, RecursionError, OverflowError) as exc:
        code = str(exc) if isinstance(exc, ValueError) and len(str(exc)) <= 64 else 'VALIDATOR_FAILURE'
        result = {'protocol_version': '0.4.0', 'request_id': rid,
                  'decision': 'REFUSED', 'semantic_result': 'SENTINEL_UNRESOLVED',
                  'manifest_sha256': 'SENTINEL_UNRESOLVED',
                  'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED',
                  'faults': [{'code': code}],
                  'validator_basis': 'SEPARATE_IMPLEMENTATION_SHARED_SCHEMA'}
    sys.stdout.buffer.write(canonical(result) + b'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
