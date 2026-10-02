from __future__ import annotations

import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from build_life_table import RADIX, calculate, load_qx, survival_at_age


class LifeTableTests(unittest.TestCase):
    def test_constant_mortality_has_geometric_survival(self):
        life, survival = calculate({sex: [0.1] * 100 for sex in ("M", "F")})
        self.assertEqual(len(life), 200)
        self.assertEqual(len(survival), 16)
        for row in life:
            age = row["age"]
            self.assertAlmostEqual(float(row["lx"]), RADIX * 0.9 ** age, delta=1e-6)
            self.assertAlmostEqual(float(row["dx"]), RADIX * 0.9 ** age * 0.1, delta=1e-6)
        for row in survival:
            self.assertAlmostEqual(float(row["survival_probability"]), 0.9 ** row["term_years"], delta=1e-12)

    def test_zero_mortality(self):
        life, survival = calculate({sex: [0.0] * 100 for sex in ("M", "F")})
        self.assertTrue(all(float(row["lx"]) == RADIX and float(row["dx"]) == 0 for row in life))
        self.assertTrue(all(float(row["survival_probability"]) == 1 for row in survival))

    def test_survival_uses_attained_age_and_excludes_endpoint(self):
        qx = [0.0] * 100
        qx[30], qx[31], qx[32] = 0.1, 0.2, 1.0
        self.assertAlmostEqual(survival_at_age(qx, 30, 2), 0.72)
        self.assertEqual(survival_at_age(qx, 30, 3), 0.0)
        self.assertEqual(survival_at_age(qx, 30, 0), 1.0)

    def test_exact_age_boundary(self):
        qx = [0.1] * 100
        self.assertAlmostEqual(survival_at_age(qx, 99, 1), 0.9)
        for start, term in ((99, 2), (100, 1), (-1, 1), (30, -1)):
            with self.subTest(start=start, term=term), self.assertRaises(ValueError):
                survival_at_age(qx, start, term)

    def test_loader_rejects_incomplete_duplicate_and_invalid_inputs(self):
        rows = [{"year": "2024", "sex": sex, "age": str(age), "qx": "0.01"}
                for sex in ("M", "F") for age in range(100)]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "qx.csv"
            scenarios = [rows[:-1], rows + [rows[0]]]
            for field, value in (("qx", "NaN"), ("qx", "1.1"), ("qx", "-0.1"),
                                 ("age", "100+"), ("sex", "X"), ("year", "2025")):
                scenarios.append([{**rows[0], field: value}, *rows[1:]])
            for invalid in scenarios:
                with path.open("w", encoding="utf-8", newline="") as file:
                    writer = csv.DictWriter(file, fieldnames=["year", "sex", "age", "qx"])
                    writer.writeheader()
                    writer.writerows(invalid)
                with self.assertRaises(ValueError):
                    load_qx(path)

    def test_source_data_and_survival_reconcile_independently(self):
        source = load_qx()
        life, survival = calculate(source)
        for sex in ("M", "F"):
            rows = [row for row in life if row["sex"] == sex]
            l100 = RADIX * math.prod(1 - q for q in source[sex])
            self.assertAlmostEqual(sum(float(row["dx"]) for row in rows) + l100, RADIX, delta=0.0001)
            for previous, following in zip(rows, rows[1:]):
                self.assertAlmostEqual(float(previous["lx"]) - float(previous["dx"]), float(following["lx"]), delta=2e-6)
        for row in survival:
            start, end, sex = row["start_age"], row["end_age"], row["sex"]
            expected = math.prod(1 - q for q in source[sex][start:end])
            self.assertAlmostEqual(float(row["survival_probability"]), expected, delta=1e-12)


if __name__ == "__main__":
    unittest.main()
