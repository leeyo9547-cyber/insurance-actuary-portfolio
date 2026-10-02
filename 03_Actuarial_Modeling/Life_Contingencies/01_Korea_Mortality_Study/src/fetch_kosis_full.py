from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from pykosis import KOSIS, pivot_items

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

ORG_ID = "101"
TABLE_ID = "DT_1B42"
YEAR = "2024"


def _age_from_row(row: dict) -> tuple[int | None, bool]:
    """Return (age, is_open_ended) from KOSIS classification labels."""
    candidates = []
    for key, value in row.items():
        if key.startswith("c") and key.endswith("_nm") and value is not None:
            candidates.append(str(value).strip())

    for text in candidates:
        normalized = text.replace(" ", "")
        if "100세이상" in normalized or "100+" in normalized:
            return 100, True
        m = re.fullmatch(r"(\d+)세?", normalized)
        if m:
            return int(m.group(1)), False
    return None, False


def _find_qx_columns(row: dict) -> tuple[str, str]:
    keys = list(row.keys())

    def match(sex_words: tuple[str, ...]) -> str:
        for key in keys:
            label = str(key).replace(" ", "")
            if "사망확률" in label and any(word in label for word in sex_words):
                return key
        raise KeyError(
            f"Could not find qx column for {sex_words}. "
            f"Available columns: {keys}"
        )

    male = match(("남자", "남성", "Male", "male"))
    female = match(("여자", "여성", "Female", "female"))
    return male, female


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # KOSIS() reads KOSIS_API_KEY from the environment or pykosis credentials.
    kosis = KOSIS()

    rows = kosis.fetch_data(
        org_id=ORG_ID,
        tbl_id=TABLE_ID,
        obj_l1="ALL",
        frequency="annual",
        start_period=YEAR,
        end_period=YEAR,
    )

    raw_path = RAW_DIR / f"kosis_{YEAR}_{TABLE_ID}_raw.json"
    raw_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    wide = pivot_items(rows, label="itm_nm")
    if not wide:
        raise RuntimeError("KOSIS returned no rows.")

    wide_path = RAW_DIR / f"kosis_{YEAR}_{TABLE_ID}_wide.json"
    wide_path.write_text(
        json.dumps(wide, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    male_qx_col, female_qx_col = _find_qx_columns(wide[0])

    normalized = []
    for row in wide:
        age, is_open_ended = _age_from_row(row)
        if age is None:
            continue

        for sex, qx_col in (("M", male_qx_col), ("F", female_qx_col)):
            value = row.get(qx_col)
            if value in (None, "", "-"):
                continue
            normalized.append(
                {
                    "source": "KOSIS",
                    "table_id": TABLE_ID,
                    "year": int(YEAR),
                    "sex": sex,
                    "age": age,
                    "qx": float(value),
                    "open_ended": is_open_ended,
                }
            )

    # Main actuarial basis: exact ages 0-99 only.
    exact = [
        row for row in normalized
        if 0 <= row["age"] <= 99 and not row["open_ended"]
    ]

    expected = {(sex, age) for sex in ("M", "F") for age in range(100)}
    actual = {(row["sex"], row["age"]) for row in exact}
    missing = sorted(expected - actual)
    if missing:
        raise RuntimeError(
            "The normalized table is incomplete. Missing sex/age cells: "
            + ", ".join(f"{sex}{age}" for sex, age in missing[:20])
        )

    out_path = PROCESSED_DIR / "kosis_2024_complete_life_table_qx.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["year", "sex", "age", "qx"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in sorted(exact, key=lambda x: (x["sex"] != "M", x["age"])):
            writer.writerow({**{k: row[k] for k in fieldnames}, "qx": f"{row['qx']:.5f}"})

    terminal = [row for row in normalized if row["open_ended"]]
    if terminal:
        terminal_path = PROCESSED_DIR / "kosis_2024_terminal_open_age.csv"
        with terminal_path.open("w", encoding="utf-8", newline="") as f:
            fieldnames = ["year", "sex", "age", "qx"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for row in sorted(terminal, key=lambda x: x["sex"] != "M"):
                writer.writerow({
                    "year": row["year"], "sex": row["sex"],
                    "age": "100+", "qx": f"{row['qx']:.5f}",
                })

    print(f"raw: {raw_path}")
    print(f"processed: {out_path}")
    print(f"rows: {len(exact)} (expected 200)")


if __name__ == "__main__":
    main()
