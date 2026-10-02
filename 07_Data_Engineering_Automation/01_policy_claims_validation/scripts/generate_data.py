"""Reproduce the synthetic Day 1 dataset using the Python standard library."""

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20260930
CUTOFF = date(2026, 9, 30)


def generate():
    rng = random.Random(SEED)
    products = ["TERM_A", "ACCIDENT_B", "HEALTH_C"]
    policies = []
    for i in range(1000):
        start = date(2025, 1, 1) + timedelta(days=rng.randrange(638))
        policies.append({
            "record_id": f"POL{i + 1:04d}",
            "policy_id": f"P{i + 1:04d}",
            "product": products[rng.randrange(3)],
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=364)).isoformat(),
        })

    # Keep the reference population intact while generating claim records.
    # A contract may have multiple claims; one claim has one payment here.
    eligible = [i for i in range(1000) if i not in (5, 116, 304, 499, 799)]
    claims = []
    for i in range(200):
        p = policies[eligible[rng.randrange(len(eligible))]]
        start = date.fromisoformat(p["start_date"])
        last_accident = min(date.fromisoformat(p["end_date"]), CUTOFF)
        accident = start + timedelta(days=rng.randrange((last_accident - start).days + 1))
        payment = min(accident + timedelta(days=rng.randrange(46)), CUTOFF)
        claims.append({
            "record_id": f"CLM{i + 1:04d}",
            "claim_id": f"C{i + 1:04d}",
            "policy_id": p["policy_id"],
            "accident_date": accident.isoformat(),
            "payment_date": payment.isoformat(),
            "paid_amount": rng.randrange(1, 101) * 10000,
        })

    # Include a legitimate zero payment and a claim referencing a duplicate key.
    claims[0]["paid_amount"] = 0
    p = policies[5]
    start = date.fromisoformat(p["start_date"])
    accident = min(start + timedelta(days=30), CUTOFF)
    claims[10].update(policy_id=p["policy_id"], accident_date=accident.isoformat(),
                      payment_date=min(accident + timedelta(days=10), CUTOFF).isoformat())

    # Deliberate training cases: preserve record_id as a stable source-row key.
    policies[116]["policy_id"] = policies[5]["policy_id"]
    policies[304]["policy_id"] = ""
    policies[499]["product"] = ""
    policies[799]["end_date"] = (date.fromisoformat(policies[799]["start_date"]) - timedelta(days=1)).isoformat()
    claims[36]["claim_id"] = claims[5]["claim_id"]
    claims[79]["policy_id"] = ""
    claims[104]["policy_id"] = "P9999"
    claims[129]["paid_amount"] = -10000
    claims[159]["paid_amount"] = ""
    claims[179]["payment_date"] = (date.fromisoformat(claims[179]["accident_date"]) - timedelta(days=1)).isoformat()
    p = next(p for p in policies if p["policy_id"] == claims[194]["policy_id"])
    accident = date.fromisoformat(p["start_date"]) - timedelta(days=1)
    claims[194].update(accident_date=accident.isoformat(), payment_date=(accident + timedelta(days=5)).isoformat())
    claims[198]["payment_date"] = ""
    return policies, claims


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in zip(("policies_raw.csv", "claims_raw.csv"), generate()):
        with (args.output_dir / name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"{name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
