"""Normalize the checked-in KOSIS 2024 CSV without an API key."""

from __future__ import annotations

import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "kosis_2024_male_female_mortality.csv"
PROCESSED = ROOT / "data" / "processed"
YEAR = 2024
FIELDS = ["year", "sex", "age", "qx"]
SEX_COLUMNS = {"M": "사망확률(남자)", "F": "사망확률(여자)"}


def normalize(path: Path = RAW) -> tuple[list[dict], list[dict]]:
    exact, terminal = [], []
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {"연령별", *SEX_COLUMNS.values()}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing columns: {sorted(required - set(reader.fieldnames or []))}")
        for line, row in enumerate(reader, start=2):
            label = row["연령별"].replace(" ", "")
            if label == "100세이상":
                age = "100+"
            else:
                match = re.fullmatch(r"(\d+)세", label)
                if not match or not 0 <= int(match[1]) <= 99:
                    raise ValueError(f"Unexpected age at line {line}: {label!r}")
                age = int(match[1])
            if age in seen:
                raise ValueError(f"Duplicate age at line {line}: {age}")
            seen.add(age)
            for sex, column in SEX_COLUMNS.items():
                value = row[column]
                try:
                    qx = Decimal(value)
                except (InvalidOperation, TypeError):
                    raise ValueError(f"Invalid qx at line {line}: {sex} {value!r}") from None
                if not qx.is_finite() or not 0 <= qx <= 1:
                    raise ValueError(f"qx outside [0, 1] at line {line}: {sex} {value!r}")
                formatted = format(qx, ".5f")
                if Decimal(formatted) != qx:
                    raise ValueError(f"qx would lose precision at line {line}: {value!r}")
                record = {"year": YEAR, "sex": sex, "age": age, "qx": formatted}
                (terminal if age == "100+" else exact).append(record)
    expected = set(range(100)) | {"100+"}
    if seen != expected:
        raise ValueError(f"Missing ages: {sorted(expected - seen, key=str)}")
    order = {"M": 0, "F": 1}
    exact.sort(key=lambda row: (order[row["sex"]], row["age"]))
    terminal.sort(key=lambda row: order[row["sex"]])
    return exact, terminal


def main() -> None:
    exact, terminal = normalize()
    PROCESSED.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("kosis_2024_complete_life_table_qx.csv", exact),
        ("kosis_2024_terminal_open_age.csv", terminal),
    ):
        with (PROCESSED / filename).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"{filename}: {len(rows)} rows")


if __name__ == "__main__":
    main()
