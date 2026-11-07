"""Independent policy evaluation process: no imports from candidate microservers.

This is pre-dispatch policy enforcement when used by the trusted launcher.
It does not authenticate the local invoker and does not sandbox the worker.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

POLICY = Path(__file__).resolve().parent / 'policy_v0_4.json'
REQUIRED = {'protocol_version', 'request_id', 'actor', 'capability', 'authority_ceiling', 'manifest_sha256', 'manifest'}


def unique(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError('DUPLICATE_KEY')
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError('NON_FINITE')


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def reject_unresolved(obj):
    nodes = [obj]
    while nodes:
        item = nodes.pop()
        if item is None or isinstance(item, float) and not math.isfinite(item):
            raise ValueError('NULL_OR_NONFINITE')
        if isinstance(item, dict):
            nodes.extend(item.values())
        elif isinstance(item, list):
            nodes.extend(item)


def decide(req):
    policy = json.loads(POLICY.read_text(encoding='utf-8'), object_pairs_hook=unique,
                        parse_constant=reject_constant)
    if not isinstance(req, dict) or set(req) != REQUIRED:
        raise ValueError('REQUEST_SHAPE')
    if req['protocol_version'] != '0.4.0':
        raise ValueError('PROTOCOL_VERSION')
    if not isinstance(req['request_id'], str) or not 1 <= len(req['request_id']) <= 180:
        raise ValueError('REQUEST_ID')
    for name, value in [('actor', policy['allowed_actor']),
                        ('capability', policy['allowed_capability']),
                        ('authority_ceiling', policy['authority_ceiling'])]:
        if req[name] != value:
            raise ValueError('POLICY_REFUSED_' + name.upper())
    if not isinstance(req['manifest'], dict):
        raise ValueError('MANIFEST_SHAPE')
    if len(canonical(req['manifest'])) > policy['max_manifest_bytes']:
        raise ValueError('MANIFEST_LIMIT')
    if req['manifest_sha256'] != hashlib.sha256(canonical(req['manifest'])).hexdigest():
        raise ValueError('DIGEST_MISMATCH')
    if set(policy['allowed_stages']) != {'schema-gate', 'graph-gate'} or policy['side_effects'] != 'FORBIDDEN' or policy['admission'] != 'NOT_ADMITTED' or policy['publication'] != 'NOT_PUBLISHED':
        raise ValueError('POLICY_UNSAFE')
    return {
        'protocol_version': '0.4.0', 'request_id': req['request_id'],
        'decision': 'POLICY_PASSED_CANDIDATE', 'manifest_sha256': req['manifest_sha256'],
        'authority_ceiling': 'READ_ONLY_CANDIDATE', 'allowed_stages': list(policy['allowed_stages']),
        'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED',
        'policy_sha256': hashlib.sha256(POLICY.read_bytes()).hexdigest(),
        'faults': []
    }


def main():
    request_id = 'SENTINEL_UNRESOLVED'
    try:
        raw = sys.stdin.buffer.read(2097153)
        if not raw or len(raw) > 2097152:
            raise ValueError('INPUT_LIMIT')
        req = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                         parse_constant=reject_constant)
        reject_unresolved(req)
        if isinstance(req, dict) and isinstance(req.get('request_id'), str):
            request_id = req['request_id'][:180]
        reply = decide(req)
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError, OverflowError) as exc:
        reason = str(exc) if isinstance(exc, ValueError) and len(str(exc)) <= 64 else 'INVALID_REQUEST'
        reply = {'protocol_version': '0.4.0', 'request_id': request_id,
                 'decision': 'REFUSED', 'manifest_sha256': 'SENTINEL_UNRESOLVED',
                 'authority_ceiling': 'NONE', 'allowed_stages': [],
                 'admission': 'NOT_ADMITTED', 'publication': 'NOT_PUBLISHED',
                 'policy_sha256': 'SENTINEL_UNRESOLVED',
                 'faults': [{'code': reason}]}
    sys.stdout.buffer.write(canonical(reply) + b'\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
