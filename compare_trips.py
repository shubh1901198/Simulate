#!/usr/bin/env python3
# compare_trips.py

import pandas as pd
from datetime import datetime
import argparse
import sys
import os

def load_thresholds(csv_path):
    import os
    if not os.path.isfile(csv_path) or os.path.getsize(csv_path) == 0:
        raise RuntimeError(
            f"Threshold file missing or empty: {csv_path}. "
            "Expected columns: Metric,Acceptable Difference"
        )
    try:
        # Handle UTF-8 BOM safely
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        required_cols = {"Metric", "Acceptable Difference"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Threshold file must have columns: {required_cols}")
        # Clean and validate numeric
        metrics = df["Metric"].astype(str).str.strip()
        diffs = pd.to_numeric(df["Acceptable Difference"], errors="coerce")
        if diffs.isna().any():
            bad_rows = df[diffs.isna()]
            raise ValueError(
                "Threshold 'Acceptable Difference' must be numeric for all rows.\n"
                f"Problem rows:\n{bad_rows}"
            )
        thresholds = dict(zip(metrics, diffs))
        return thresholds
    except Exception as e:
        raise RuntimeError(f"Error reading thresholds CSV: {e}")

def load_trip_b_last10(csv_path):
    import os
    if not os.path.isfile(csv_path):
        raise RuntimeError(f"Trip B CSV not found at path: {csv_path}")

    size = os.path.getsize(csv_path)
    if size == 0:
        raise RuntimeError(
            "Trip B CSV is empty (0 bytes). Please provide a file with headers and rows.\n"
            "Expected header: Timestamp,Trip Meter,Distance,Fuel Used,Avg Speed,Duration"
        )

    # Try multiple delimiter/encoding combos to avoid EmptyDataError / wrong dialect
    attempts = [
        dict(sep=",", encoding="utf-8-sig"),
        dict(sep=",", encoding="utf-8"),
        dict(sep=";", encoding="utf-8-sig"),
        dict(sep="|", encoding="utf-8-sig"),
    ]
    last_exc = None
    df = None
    for opts in attempts:
        try:
            df = pd.read_csv(csv_path, **opts)
            break
        except Exception as e:
            last_exc = e

    if df is None:
        raise RuntimeError(f"Error reading Trip B CSV with multiple attempts: {last_exc}")

    required = {"Trip Meter", "Timestamp", "Distance", "Fuel Used", "Avg Speed", "Duration"}
    if not required.issubset(df.columns):
        raise RuntimeError(
            "Trip B CSV is missing required columns.\n"
            f"Found columns: {list(df.columns)}\n"
            f"Required: {sorted(required)}\n"
            "Tip: Ensure the first row is the header and delimiter is consistent."
        )

    # Filter Trip B and take last 10
    trip_b = df[df["Trip Meter"].astype(str).str.strip() == "Trip B"].tail(10).reset_index(drop=True)
    if trip_b.empty:
        raise RuntimeError(
            "No 'Trip B' rows found in the CSV. "
            "Tip: Check exact spelling/case of 'Trip B' in 'Trip Meter'."
        )

    # Ensure numeric columns for comparison
    for col in ["Distance", "Fuel Used", "Avg Speed", "Duration"]:
        trip_b[col] = pd.to_numeric(trip_b[col], errors="coerce")

    before = len(trip_b)
    trip_b = trip_b.dropna(subset=["Distance", "Fuel Used", "Avg Speed", "Duration"]).reset_index(drop=True)
    dropped = before - len(trip_b)
    if dropped > 0:
        print(f"⚠️ Note: Dropped {dropped} Trip B rows due to non-numeric metric values.")

    if trip_b.empty:
        raise RuntimeError(
            "After cleaning, no valid Trip B rows remain. "
            "Cause: non-numeric values in Distance/Fuel Used/Avg Speed/Duration."
        )

    return trip_b

def load_trip_a_source(csv_path):
    try:
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if not {"Trip Meter", "Timestamp", "Distance", "Fuel Used", "Avg Speed", "Duration"}.issubset(df.columns):
            raise ValueError("Trip A source CSV missing required columns.")
        # Keep only Trip A
        df = df[df["Trip Meter"].astype(str).str.strip() == "Trip A"].reset_index(drop=True)
        if df.empty:
            raise ValueError("No Trip A rows found in the provided CSV.")
        # Coerce numeric just like Trip B
        for col in ["Distance", "Fuel Used", "Avg Speed", "Duration"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["Distance", "Fuel Used", "Avg Speed", "Duration"]).reset_index(drop=True)
        if df.empty:
            raise ValueError("After cleaning, no valid Trip A rows remain (non-numeric metrics?).")
        return df
    except Exception as e:
        raise RuntimeError(f"Error reading Trip A CSV: {e}")

def compare_rows(trip_a_df, trip_b_df, thresholds):
    n = min(len(trip_a_df), len(trip_b_df))
    comparison_results = []
    pass_count = fail_count = 0

    for i in range(n):
        a = trip_a_df.iloc[i]
        b = trip_b_df.iloc[i]
        differences = {
            "Distance": abs(a["Distance"] - b["Distance"]),
            "Fuel Used": abs(a["Fuel Used"] - b["Fuel Used"]),
            "Avg Speed": abs(a["Avg Speed"] - b["Avg Speed"]),
            "Duration": abs(a["Duration"] - b["Duration"]),
        }
        # NOTE: real operator <= (not HTML-escaped)
        pass_fail = all(
            differences.get(metric, float("inf")) <= thresholds[metric]
            for metric in thresholds
        )
        result = "Pass" if pass_fail else "Fail"
        pass_count += 1 if pass_fail else 0
        fail_count += 0 if pass_fail else 1

        comparison_results.append({
            "Trip A Timestamp": a["Timestamp"],
            "Trip B Timestamp": b["Timestamp"],
            "Distance Diff": differences["Distance"],
            "Fuel Used Diff": differences["Fuel Used"],
            "Avg Speed Diff": differences["Avg Speed"],
            "Duration Diff": differences["Duration"],
            "Pass/Fail": result,
        })
    return comparison_results, pass_count, fail_count

def write_log(log_path, results, pass_count, fail_count):
    with open(log_path, "w") as f:
        f.write(f"Trip Comparison Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n")
        for row in results:
            f.write(
                f"{row['Trip A Timestamp']} | {row['Trip B Timestamp']} | "
                f"Distance Diff: {row['Distance Diff']:.2f} | "
                f"Fuel Used Diff: {row['Fuel Used Diff']:.2f} | "
                f"Avg Speed Diff: {row['Avg Speed Diff']:.2f} | "
                f"Duration Diff: {row['Duration Diff']} | "
                f"Result: {row['Pass/Fail']}\n"
            )
        f.write("=" * 100 + "\n")
        f.write(f"Summary: {pass_count} Passed, {fail_count} Failed\n")

def main():
    parser = argparse.ArgumentParser(
        description="Compare Trip A entries against last 10 Trip B entries using thresholds."
    )
    parser.add_argument(
        "-a", "--trip-a-csv",
        default="trip_a_generated.csv",
        help="CSV containing Trip A rows (default: trip_a_generated.csv)"
    )
    parser.add_argument(
        "-b", "--trip-b-csv",
        default="trip_log_history.csv",
        help="CSV containing historical Trip B rows (default: trip_log_history.csv)"
    )
    parser.add_argument(
        "-t", "--thresholds-csv",
        default="comparison_thresholds.csv",
        help="Threshold CSV with columns: Metric,Acceptable Difference (default: comparison_thresholds.csv)"
    )
    parser.add_argument(
        "-l", "--log",
        default="trip_comparison.log",
        help="Output .log file path (default: trip_comparison.log)"
    )
    parser.add_argument(
        "--align",
        choices=["head", "tail"],
        default="head",
        help="Pick alignment for Trip A rows: 'head' uses the first N rows, 'tail' uses the last N rows (default: head)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.thresholds_csv):
        print(f"❌ Threshold file not found: {args.thresholds_csv}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.trip_b_csv):
        print(f"❌ Trip B CSV not found: {args.trip_b_csv}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.trip_a_csv):
        print(f"❌ Trip A CSV not found: {args.trip_a_csv}", file=sys.stderr)
        sys.exit(1)

    thresholds = load_thresholds(args.thresholds_csv)
    trip_b_df = load_trip_b_last10(args.trip_b_csv)
    trip_a_df = load_trip_a_source(args.trip_a_csv)

    # Align the number of rows
    n = min(len(trip_a_df), len(trip_b_df))
    if n == 0:
        print("❌ No rows to compare.", file=sys.stderr)
        sys.exit(2)

    trip_a_slice = trip_a_df.head(n) if args.align == "head" else trip_a_df.tail(n).reset_index(drop=True)
    trip_b_slice = trip_b_df.head(n).reset_index(drop=True)

    results, pass_count, fail_count = compare_rows(trip_a_slice, trip_b_slice, thresholds)

    # Console summary
    print(f"\n🔎 Compared {n} pairs (Trip A vs Trip B)")
    print(f"✅ Passed: {pass_count} | ❌ Failed: {fail_count}")
    if n > 0:
        print("Example row:")
        r0 = results[0]
        print(
            f"- A[{r0['Trip A Timestamp']}] vs B[{r0['Trip B Timestamp']}]: "
            f"ΔDistance={r0['Distance Diff']:.2f}, ΔFuel={r0['Fuel Used Diff']:.2f}, "
            f"ΔAvgSpeed={r0['Avg Speed Diff']:.2f}, ΔDuration={r0['Duration Diff']} -> {r0['Pass/Fail']}"
        )

    write_log(args.log, results, pass_count, fail_count)
    print(f"📝 Detailed log saved to: {args.log}\n")


if __name__ == "__main__":
    main()  