"""One-time migration: move flat data/*.csv into data/YYYY/*.csv with dedup.

Reads Published date from first data row to determine year.
Removes duplicate (rawid, version) rows during migration.
"""

import csv
import os
import sys


def migrate(data_dir="./data"):
    """Migrate flat CSVs in data_dir to data_dir/YYYY/WW.csv with dedup."""
    csv_files = sorted(
        f for f in os.listdir(data_dir) if f.endswith(".csv") and f != "dummy-data.csv"
    )

    for fname in csv_files:
        src_path = os.path.join(data_dir, fname)
        with open(src_path, newline="", encoding="UTF8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                continue

            rows = list(reader)
            if not rows:
                continue

        # Determine year from first row's Published date (YYYY-...)
        year = rows[0][0][:4]

        # Dedup by (rawid, version) — columns 3 and 4
        seen = set()
        deduped = []
        for row in rows:
            if len(row) >= 5:
                key = (row[3], str(row[4]))
                if key not in seen:
                    seen.add(key)
                    deduped.append(row)

        # Write to year dir
        dest_dir = os.path.join(data_dir, year)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, fname)

        with open(dest_path, "w", newline="", encoding="UTF8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(deduped)

        # Remove original flat file
        os.remove(src_path)

        dupes = len(rows) - len(deduped)
        print(f"{fname} → {year}/{fname}: {len(deduped)} rows ({dupes} duplicates removed)")


if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "./data"
    migrate(data_dir)
