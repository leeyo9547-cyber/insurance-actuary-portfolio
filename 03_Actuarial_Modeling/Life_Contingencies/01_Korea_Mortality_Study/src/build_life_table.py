"""Build a period life table and selected survival probabilities (Python 3.10+)."""

from __future__ import annotations

import csv
import math
from pathlib import Path

from mortality import build_lx, qx_to_px, survival_probability

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "kosis_2024_complete_life_table_qx.csv"
LIFE_OUTPUT = ROOT / "data" / "processed" / "kosis_2024_life_table.csv"
SURVIVAL_OUTPUT = ROOT / "results" / "survival_probability_10_20_years.csv"
YEAR = 2024
RADIX = 100_000.0
SEXES = ("M", "F")
START_AGES = (30, 40, 50, 60)
TERMS = (10, 20)


def load_qx(path: Path = INPUT) -> dict[str, list[float]]:
    values = {}
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != ["year", "sex", "age", "qx"]:
            raise ValueError("Expected columns: year,sex,age,qx")
        for line, row in enumerate(reader, start=2):
            try:
                year, age, qx = int(row["year"]), int(row["age"]), float(row["qx"])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid numeric input at line {line}") from None
            sex = row["sex"]
            if year != YEAR or sex not in SEXES or not 0 <= age <= 99:
                raise ValueError(f"Unexpected year, sex or exact age at line {line}")
            if not math.isfinite(qx) or not 0 <= qx <= 1:
                raise ValueError(f"Invalid qx at line {line}: {qx}")
            key = (sex, age)
            if key in values:
                raise ValueError(f"Duplicate sex/age at line {line}: {key}")
            values[key] = qx
    expected = {(sex, age) for sex in SEXES for age in range(100)}
    if set(values) != expected:
        raise ValueError(f"Missing sex/age records: {sorted(expected - set(values))}")
    return {sex: [values[sex, age] for age in range(100)] for sex in SEXES}


def survival_at_age(qx: list[float], start_age: int, term: int) -> float:
    if not 0 <= start_age < len(qx) or term < 0 or start_age + term > len(qx):
        raise ValueError("Survival interval must use available exact-age qx only")
    return survival_probability(qx[start_age:start_age + term])


def calculate(qx_by_sex: dict[str, list[float]]) -> tuple[list[dict], list[dict]]:
    life_rows, survival_rows = [], []
    for sex in SEXES:
        qx = qx_by_sex[sex]
        if len(qx) != 100:
            raise ValueError("Each sex needs all 100 exact-age probabilities")
        lx = build_lx(qx, radix=RADIX)  # Includes l_100, but no q_100 is assumed.
        for age, probability in enumerate(qx):
            px = qx_to_px(probability)
            dx = lx[age] * probability
            if not math.isclose(probability + px, 1.0, abs_tol=1e-12):
                raise ValueError("qx + px must equal 1")
            if not math.isclose(lx[age] - dx, lx[age + 1], rel_tol=1e-12, abs_tol=1e-8):
                raise ValueError("Life table does not reconcile")
            if not 0 <= lx[age + 1] <= lx[age] <= RADIX:
                raise ValueError("Survivors must be nonnegative and nonincreasing")
            life_rows.append({
                "year": YEAR, "sex": sex, "age": age,
                "qx": f"{probability:.5f}", "px": f"{px:.5f}",
                "lx": f"{lx[age]:.6f}", "dx": f"{dx:.6f}",
            })
        if not math.isclose(sum(lx[age] * qx[age] for age in range(100)) + lx[100],
                            RADIX, rel_tol=1e-12, abs_tol=1e-8):
            raise ValueError("Deaths through age 99 plus survivors at age 100 must equal radix")
        for start_age in START_AGES:
            for term in TERMS:
                probability = survival_at_age(qx, start_age, term)
                if lx[start_age] > 0 and not math.isclose(
                    probability, lx[start_age + term] / lx[start_age],
                    rel_tol=1e-12, abs_tol=1e-12,
                ):
                    raise ValueError("Survival product does not match lx ratio")
                survival_rows.append({
                    "year": YEAR, "sex": sex, "start_age": start_age,
                    "term_years": term, "end_age": start_age + term,
                    "survival_probability": f"{probability:.12f}",
                })
    return life_rows, survival_rows


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    life_rows, survival_rows = calculate(load_qx())
    write_csv(LIFE_OUTPUT, ["year", "sex", "age", "qx", "px", "lx", "dx"], life_rows)
    write_csv(SURVIVAL_OUTPUT,
              ["year", "sex", "start_age", "term_years", "end_age", "survival_probability"],
              survival_rows)
    print(f"{LIFE_OUTPUT.name}: {len(life_rows)} rows")
    print(f"{SURVIVAL_OUTPUT.name}: {len(survival_rows)} rows")
    print("Validation passed: complete ages, qx + px = 1, lx - dx = next lx, survival product = lx ratio")


if __name__ == "__main__":
    main()
