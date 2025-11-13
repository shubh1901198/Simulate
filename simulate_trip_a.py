#!/usr/bin/env python3
# simulate_trip_a.py

import pandas as pd
import random
from datetime import datetime
import argparse
import os

def simulate_trip_a_rows(n=10):
    rows = []
    for _ in range(n):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "Distance": round(120 + random.uniform(-5, 5), 1),
            "Fuel Used": round(8.5 + random.uniform(-0.3, 0.3), 2),
            "Avg Speed": round(48 + random.uniform(-3, 3), 1),
            "Duration": 150 + random.randint(-5, 5),
        }
        rows.append({
            "Timestamp": timestamp,
            "Trip Meter": "Trip A",
            "Distance": data["Distance"],
            "Fuel Used": data["Fuel Used"],
            "Avg Speed": data["Avg Speed"],
            "Duration": data["Duration"],
        })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(
        description="Simulate Trip A entries and write to CSV."
    )
    parser.add_argument(
        "-o", "--output",
        default="trip_a_generated.csv",
        help="Output CSV file for Trip A simulations (default: trip_a_generated.csv)"
    )
    parser.add_argument(
        "-n", "--num",
        type=int,
        default=10,
        help="Number of Trip A entries to simulate (default: 10)"
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to output CSV if it exists (default: overwrite)"
    )
    args = parser.parse_args()

    df = simulate_trip_a_rows(args.num)

    # Write CSV
    write_header = True
    if args.append and os.path.isfile(args.output):
        write_header = False

    mode = "a" if args.append else "w"
    df.to_csv(args.output, index=False, mode=mode, header=write_header)

    print(f"✅ Generated {len(df)} Trip A rows -> {args.output}")
    print("Columns:", ", ".join(df.columns))

if __name__ == "__main__":
    main()
    