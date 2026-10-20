"""Adversarial controls for the standalone auditor, added after search freeze."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location("standalone", ROOT/"tools/audit_submission.py")
standalone = importlib.util.module_from_spec(loader)
loader.loader.exec_module(standalone)


class SecondCheckerTests(unittest.TestCase):
    def test_structural_and_semantic_rejections(self):
        spec = dict(kind="linear", inputs=2, outputs=2, matrix=[[1, 1], [1, 0]])
        valid = dict(inputs=2, gates=[["XOR", 0, 1]], outputs=[2, 0])
        self.assertTrue(standalone.audit(spec, valid)["ok"])
        variants = []
        for gate in (["LOOKUP", 0, 1], ["AND", 0, 1], ["XOR", 2, 0],
                     ["XOR", -1, 0], ["XOR", True, 0], ["XOR", 0.0, 1],
                     ["NOT", 0, 1], ["XOR", 0], ["XOR", "x", 1]):
            c = copy.deepcopy(valid)
            c["gates"] = [gate]
            variants.append(c)
        c = copy.deepcopy(valid)
        c["hidden_lookup"] = [1, 2, 3]
        variants.append(c)
        c = copy.deepcopy(valid)
        c["outputs"] = [0, 1]
        variants.append(c)
        c = copy.deepcopy(valid)
        c["gates"].append(["NOT", 2])
        c["outputs"][0] = 3
        variants.append(c)
        for c in variants:
            with self.subTest(c=c), self.assertRaises(ValueError):
                standalone.audit(spec, c)

    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"bad.json"
            p.write_text('{"inputs":2,"inputs":3}')
            with self.assertRaises(ValueError):
                standalone.load(p)

    def test_non_mds_and_wrong_product(self):
        spec = dict(kind="design", inputs=16, outputs=16, involutory=False)
        identity = dict(inputs=16, gates=[], outputs=list(range(16)))
        with self.assertRaises(ValueError):
            standalone.audit(spec, identity)
        spec = json.loads((ROOT/"portfolio/gf4-13.json").read_text())
        c = json.loads((ROOT/spec["baselines"][0]["path"]).read_text())
        self.assertEqual(standalone.audit(spec, c)["evaluations"], 256)
        c["outputs"][0] = 0
        with self.assertRaises(ValueError):
            standalone.audit(spec, c)


if __name__ == "__main__":
    unittest.main()
