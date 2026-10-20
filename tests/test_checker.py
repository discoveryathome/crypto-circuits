import copy
import json
from pathlib import Path
import random
import tempfile
import unittest

from linear_pilot.checker import Invalid, read_json, verify, design_properties
from linear_pilot.synthesis import published_mds, paar, walk

ROOT = Path(__file__).resolve().parents[1]


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.spec = {"kind":"linear","inputs":2,"outputs":2,"matrix":[[1,1],[1,0]]}
        self.c = {"inputs":2,"gates":[["XOR",0,1]],"outputs":[2,0]}

    def test_correct_affine_certificate(self):
        self.assertTrue(verify(self.c,self.spec)["ok"])

    def test_bad_certificates(self):
        cases = []
        for gate in (["LOOKUP",0,1],["AND",0,1],["XOR",2,0],["XOR",-1,0],
                     ["XOR",True,0],["XOR",0.0,1],["NOT",0,1],["XOR",0],["XOR","x",1]):
            c = copy.deepcopy(self.c); c["gates"] = [gate]; cases.append(c)
        c = copy.deepcopy(self.c); c["hidden"] = "lookup"; cases.append(c)
        c = copy.deepcopy(self.c); c["outputs"] = [0,1]; cases.append(c)
        c = copy.deepcopy(self.c); c["outputs"] = [2,True]; cases.append(c)
        c = copy.deepcopy(self.c); c["outputs"] = [2]; cases.append(c)
        c = copy.deepcopy(self.c); c["gates"] += [["NOT",2]]; c["outputs"][0] = 3; cases.append(c)
        for c in cases:
            with self.subTest(c=c), self.assertRaises(Invalid):
                verify(c,self.spec)

    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"bad.json"; p.write_text('{"inputs":2,"inputs":3}')
            with self.assertRaises(Invalid):
                read_json(p)

    def test_dead_gates_are_paid(self):
        c = copy.deepcopy(self.c); c["gates"].append(["XOR",0,1])
        m = verify(c,self.spec)["metrics"]
        self.assertEqual((m["XOR"],m["dead_gates"]),(2,1))

    def test_mds_property_and_wrong_design(self):
        spec = {"kind":"design","inputs":16,"outputs":16,"involutory":False}
        result = verify(published_mds(), spec)
        self.assertEqual(result["metrics"]["XOR"],35)
        self.assertEqual(result["evidence"]["block_minors"],69)
        identity = [[int(i == j) for j in range(16)] for i in range(16)]
        with self.assertRaises(Invalid):
            design_properties(identity,False)
        spec["involutory"] = True
        with self.assertRaises(Invalid):
            verify(published_mds(),spec)

    def test_synthesis_semantics(self):
        rng = random.Random(7)
        for n in (3,7,16):
            matrix = [[rng.randrange(2) for _ in range(n)] for _ in range(n)]
            spec = {"kind":"linear","inputs":n,"outputs":n,"matrix":matrix}
            c = paar(matrix,rng)
            verify(c,spec)
            for item in walk(c,rng,50)[0]:
                verify(item,spec)

    def test_multiplier_and_mutation(self):
        spec = json.loads((ROOT/"portfolio/gf4-13.json").read_text())
        c = json.loads((ROOT/spec["baselines"][0]["path"]).read_text())
        self.assertEqual(verify(c,spec)["evidence"]["exhaustive_inputs"],256)
        c["outputs"][0] = 0
        with self.assertRaises(Invalid):
            verify(c,spec)


if __name__ == "__main__":
    unittest.main()
