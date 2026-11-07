"""Deterministic unit, process-boundary, glue, negative, and source-parity checks."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator
from microtrans.graph_gate import check_graph
from microtrans.schema_gate import check_schema
from microtrans.glue import compose, invoke
from microtrans.protocol import (ContractRefusal, canonical_bytes, digest, strict_json,
                                 PROTOCOL_VERSION, MAX_INPUT_BYTES)

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "examples" / "source_manifest_v0_2.json"
SELF = ROOT / "examples" / "implementation_manifest_v0_3.json"
WITNESS = ROOT / "source_witness" / "check_manifest_v0_2.py"
SCHEMA = ROOT / "contracts" / "manifest_v0_2.schema.json"

spec = importlib.util.spec_from_file_location("witness_v0_2", WITNESS)
witness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(witness)


def src_manifest():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


def cases():
    src = src_manifest()
    output = [("valid_source", src)]
    mutate = [
        ("authority_transfer", lambda x: x["glue"][0].update(authority_transfer="ALLOWED")),
        ("missing_to", lambda x: x["glue"][0]["to"].update(server_id="missing")),
        ("missing_from", lambda x: x["glue"][0]["from"].update(operation="missing")),
        ("output_mismatch", lambda x: x["glue"][0].update(output_schema_ref="bogus")),
        ("input_mismatch", lambda x: x["glue"][0].update(input_schema_ref="bogus")),
        ("crete_join", lambda x: x["glue"][0].update(join_rule="NO_MUTATION")),
        ("ordinary_claims_crete", lambda x: x["glue"][0].update(kind="ORDINARY_GLUE")),
        ("duplicate_server", lambda x: x["microservers"].append(copy.deepcopy(x["microservers"][0]))),
        ("duplicate_operation", lambda x: x["microservers"][0]["operations"].append(copy.deepcopy(x["microservers"][0]["operations"][0]))),
        ("duplicate_edge", lambda x: x["glue"].append(copy.deepcopy(x["glue"][0]))),
        ("cycle", lambda x: x["glue"].append({**copy.deepcopy(x["glue"][0]), "edge_id":"return", "from":{"server_id":"candidate.validate","operation":"validate_candidate"}, "to":{"server_id":"candidate.extract","operation":"extract_candidate"}, "input_schema_ref":"contract.validation.v1", "output_schema_ref":"contract.source.v1"})),
        ("false_admission", lambda x: x["admission"].update(decision="ADMITTED")),
        ("null_unknown", lambda x: x["intent"].update(goal=None)),
        ("missing_refusal", lambda x: x["microservers"][0].update(refusal_contract="OPTIONAL")),
        ("unknown_key", lambda x: x.update(no_such_key="illegal")),
        ("schema_version", lambda x: x.update(schema_version="999")),
        ("no_microservers", lambda x: x.update(microservers=[])),
        ("self_loop", lambda x: x["glue"][0].update(to=copy.deepcopy(x["glue"][0]["from"]))),
    ]
    for name, mutate_one in mutate:
        variant = copy.deepcopy(src)
        mutate_one(variant)
        output.append((name, variant))
    return output


class SourceParityTests(unittest.TestCase):
    def test_parity_with_source_for_all_manifest_cases(self):
        for name, manifest in cases():
            with self.subTest(case=name):
                with tempfile.TemporaryDirectory() as tempdir:
                    baseline_path = Path(tempdir) / "manifest.json"
                    # The v0.2 checker takes paths, not in-memory structures.
                    baseline_path.write_text(json.dumps(manifest), encoding="utf-8")
                    expected = not witness.check(SCHEMA, baseline_path)
                actual_schema = not check_schema(manifest)["faults"]
                actual_graph = not check_graph(manifest)["faults"]
                self.assertEqual(expected, actual_schema and actual_graph, name)

    def test_self_manifest_is_declared_candidate(self):
        m = json.loads(SELF.read_text(encoding="utf-8"))
        self.assertEqual(m["admission"]["decision"], "NOT_ADMITTED")
        self.assertFalse(check_schema(m)["faults"])
        self.assertFalse(check_graph(m)["faults"])
        self.assertEqual(m["glue"][0]["kind"], "ORDINARY_GLUE")


class ProtocolTests(unittest.TestCase):
    def test_no_null(self):
        with self.assertRaises(ContractRefusal) as ctx:
            strict_json(b'{"a":[{"k":null}]}')
        self.assertEqual(ctx.exception.code, "NULL_FORBIDDEN")

    def test_duplicate_member(self):
        with self.assertRaises(ContractRefusal) as ctx:
            strict_json(b'{"k":1,"k":2}')
        self.assertEqual(ctx.exception.code, "DUPLICATE_JSON_KEY")

    def test_nan_forbidden(self):
        with self.assertRaises(ContractRefusal) as ctx:
            strict_json(b'{"k":NaN}')
        self.assertEqual(ctx.exception.code, "NON_STANDARD_JSON_NUMBER")

    def test_size_limit(self):
        with self.assertRaises(ContractRefusal):
            strict_json(b' ' * (MAX_INPUT_BYTES+1))

    def test_overflowed_numeric_exponent(self):
        with self.assertRaises(ContractRefusal) as ctx:
            strict_json(b'{"k":1e999999}')
        self.assertEqual(ctx.exception.code, "NON_FINITE_NUMBER")

    def test_digest_order_invariant(self):
        self.assertEqual(digest({"a":1,"b":2}), digest({"b":2,"a":1}))

    def test_process_rejects_bad_authority(self):
        envelope = {
            "protocol_version":PROTOCOL_VERSION,"request_id":"bad-authority",
            "operation":"validate_manifest_schema", "authority":{"mode":"FULL_CONTROL","basis":"INVALID"},
            "payload":{"manifest":src_manifest()}
        }
        result = subprocess.run([sys.executable,"-m","microtrans.schema_gate"], cwd=ROOT,
                                input=canonical_bytes(envelope)+b"\n",capture_output=True,timeout=10)
        self.assertEqual(result.returncode, 0)
        res = strict_json(result.stdout)
        self.assertEqual(res["decision"],"REFUSED")
        self.assertEqual(res["faults"][0]["code"],"AUTHORITY_SCOPE")
        self.assertEqual(res["admission"],"NOT_ADMITTED")

    def test_process_rejects_multiple_messages(self):
        result = subprocess.run([sys.executable,"-m","microtrans.schema_gate"], cwd=ROOT,
                                input=b'{}\n{}\n',capture_output=True,timeout=10)
        self.assertEqual(strict_json(result.stdout)["faults"][0]["code"], "MULTIPLE_MESSAGES")

    def test_process_rejects_malformed_and_duplicate(self):
        for raw, code in [(b'{"hello":\n', "MALFORMED_JSON"), (b'{"a":1,"a":2}\n', "DUPLICATE_JSON_KEY")]:
            with self.subTest(code=code):
                result=subprocess.run([sys.executable,"-m","microtrans.schema_gate"],cwd=ROOT,input=raw,capture_output=True,timeout=10)
                self.assertEqual(strict_json(result.stdout)["faults"][0]["code"],code)


class GlueTests(unittest.TestCase):
    def test_two_real_microserver_processes_and_separate_outputs(self):
        manifest=src_manifest()
        schema_response=invoke("schema-gate", manifest, "schema-001")
        graph_response=invoke("graph-gate", manifest, "graph-001")
        self.assertEqual(schema_response["decision"],"ACCEPTED")
        self.assertEqual(graph_response["decision"],"ACCEPTED")
        self.assertEqual(schema_response["data"],manifest)
        self.assertEqual(schema_response["input_sha256"],digest(manifest))
        self.assertEqual(graph_response["data"]["graph_check"],"STATIC_PASSED_NOT_ADMITTED")
        self.assertEqual(schema_response["admission"],"NOT_ADMITTED")

    def test_contract_schemas_validate_real_ipc(self):
        manifest=src_manifest()
        for service, filename in [("schema-gate","response_v0_3.schema.json"), ("graph-gate","response_v0_3.schema.json")]:
            with self.subTest(service=service):
                schema=json.loads((ROOT/"contracts"/filename).read_text())
                response=invoke(service,manifest,"schema-check")
                Draft202012Validator(schema).validate(response)
        contract=json.loads((ROOT/"contracts"/"request_v0_3.schema.json").read_text())
        example=json.loads((ROOT/"examples"/"request_schema_v0_3.json").read_text())
        Draft202012Validator(contract).validate(example)

    def test_composition_happy_path(self):
        receipt=compose(src_manifest())
        self.assertEqual(receipt["decision"], "STATIC_PASSED")
        schema=json.loads((ROOT/"contracts"/"composition_receipt_v0_3.schema.json").read_text())
        Draft202012Validator(schema).validate(receipt)
        self.assertEqual(receipt["publication"], "NOT_PUBLISHED")
        self.assertEqual([x["service"] for x in receipt["transcript"]], ["schema-gate","graph-gate"])

    def test_schema_refusal_blocks_graph_execution(self):
        m=src_manifest()
        m["admission"]["decision"]="ADMITTED"
        calls=[]
        def spy(server, manifest, request_id):
            calls.append(server)
            if server=="graph-gate":
                raise AssertionError("graph must not be called")
            return invoke(server, manifest, request_id)
        receipt=compose(m,runner=spy)
        self.assertEqual(receipt["decision"],"REFUSED")
        self.assertEqual(calls,["schema-gate"])
        self.assertEqual(receipt["faults"][0]["code"],"SCHEMA_REFUSED")

    def test_graph_refusal_propagates(self):
        m=src_manifest()
        m["glue"][0]["to"]["server_id"]="unknown"
        receipt=compose(m)
        self.assertEqual(receipt["decision"],"REFUSED")
        self.assertEqual(receipt["faults"][0]["code"],"GRAPH_REFUSED")
        self.assertEqual(len(receipt["transcript"]),2)

    def test_glue_payload_tamper_refuses(self):
        m=src_manifest()
        def tamper(server, manifest, req_id):
            out=invoke(server,manifest,req_id)
            if server=="schema-gate":
                out["data"]=copy.deepcopy(manifest)
                out["data"]["manifest_id"]="modified-by-glue"
            return out
        receipt=compose(m,runner=tamper)
        self.assertEqual(receipt["decision"],"REFUSED")
        self.assertEqual(receipt["faults"][0]["code"],"GLUE_INTEGRITY")

    def test_glue_downstream_digest_tamper_refuses(self):
        m=src_manifest()
        def tamper(server, manifest, req_id):
            out=invoke(server,manifest,req_id)
            if server=="graph-gate":
                out["input_sha256"]="bad-hash"
            return out
        receipt=compose(m,runner=tamper)
        self.assertEqual(receipt["decision"],"REFUSED")
        self.assertEqual(receipt["faults"][0]["code"],"GLUE_INTEGRITY")

    def test_no_implicit_crete(self):
        receipt=compose(src_manifest())
        self.assertNotIn("Crete",receipt["composition"])
        self.assertEqual(receipt["admission"],"NOT_ADMITTED")


if __name__ == "__main__":
    unittest.main()
