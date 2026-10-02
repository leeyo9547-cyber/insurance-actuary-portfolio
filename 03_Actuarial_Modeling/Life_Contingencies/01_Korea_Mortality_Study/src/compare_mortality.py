from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KOSIS = ROOT / "data" / "processed" / "kosis_2024_complete_life_table_qx.csv"
KIDI = ROOT / "data" / "raw" / "kidi_9th_experience_sample.csv"
OUT = ROOT / "results" / "kidi9_vs_kosis2024_age50_95.csv"


def load_kosis():
    out = {}
    with KOSIS.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            out[(row["sex"], int(row["age"]))] = float(row["qx"])
    return out


def load_kidi():
    out = {}
    with KIDI.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            age = int(row["age"])
            out[("M", age)] = float(row["male_qx"])
            out[("F", age)] = float(row["female_qx"])
    return out


def main():
    kosis = load_kosis()
    kidi = load_kidi()
    rows = []

    for sex in ("M", "F"):
        for age in range(50, 100, 5):
            key = (sex, age)
            if key not in kosis or key not in kidi:
                continue
            ki = kidi[key]
            ko = kosis[key]
            ratio = ki / ko
            rows.append({
                "sex": sex,
                "age": age,
                "kidi_9th_qx": f"{ki:.5f}",
                "kosis_2024_qx": f"{ko:.5f}",
                "difference_kidi_minus_kosis": f"{ki-ko:.5f}",
                "ratio_kidi_to_kosis": f"{ratio:.4f}",
                "kidi_lower_pct": f"{(1-ratio)*100:.1f}",
            })

    with OUT.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"saved {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
