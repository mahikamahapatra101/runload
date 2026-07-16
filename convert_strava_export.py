"""
Takes my Strava export (activities.csv) and turns it into the format
my backend actually wants: date,distance_mi,duration_min,rpe,notes

Run it like:
    python convert_strava_export.py activities.csv runload_import.csv

Notes to self:
- Strava gives distance in meters and time in seconds, converting both
- Only keeping actual runs, not rides/swims/whatever else is in there
- Strava does have a "Perceived Exertion" field but I've barely used it,
  so most rows won't have it. For those I'm just estimating effort from
  pace compared to my normal easy pace. Not perfect but good enough.
- Strava's column names shift around sometimes between export versions,
  so if this throws a KeyError, print the header row and fix the names below.
"""

import csv
import sys
from datetime import datetime


EASY_PACE_MIN_PER_MI = 8.5  # 8:30/mile, roughly my easy days


def parse_strava_date(raw: str) -> str:
    """
    Strava dates look like "Jan 1, 2026, 8:00:00 AM" - converting to
    plain YYYY-MM-DD since that's what the backend expects.
    """
    raw = raw.strip()
    formats = [
        "%b %d, %Y, %I:%M:%S %p",
        "%B %d, %Y, %I:%M:%S %p",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"couldn't parse this date: {raw!r}, format must've changed")


def estimate_rpe_from_pace(pace_min_per_mi: float) -> float:
    """
    Backup RPE guess based on pace vs my easy pace, since most of my
    runs don't have a real effort rating attached. Rough bands, not
    scientific, just enough to get a reasonable number in there.
    """
    if pace_min_per_mi <= 0:
        return 5.0

    ratio = EASY_PACE_MIN_PER_MI / pace_min_per_mi  # faster than easy = higher ratio

    if ratio <= 0.85:
        return 3.0   # slower than easy, basically a recovery jog
    elif ratio <= 1.0:
        return 4.5   # normal easy pace
    elif ratio <= 1.1:
        return 6.0   # picked it up a bit
    elif ratio <= 1.25:
        return 7.5   # tempo-ish effort
    else:
        return 9.0   # fast, speed work territory


def convert(input_path: str, output_path: str):
    rows_written = 0
    rows_skipped = 0

    with open(input_path, newline="", encoding="utf-8-sig") as infile:
        raw_reader = csv.reader(infile)
        header = next(raw_reader)

        # Strava's export has a quirk: "Distance", "Elapsed Time", and a
        # few others each show up TWICE in the header (once in an early
        # summary block, once again later in raw metric units). Using
        # DictReader here would silently just take whichever one comes
        # last, which happened to work but was luck, not something I
        # want to rely on. Grabbing exact column positions instead.
        def col_index(name):
            if name not in header:
                print(f"missing column: {name!r}")
                print(f"here's what's actually in the file: {header}")
                sys.exit(1)
            return header.index(name)

        date_idx = col_index("Activity Date")
        type_idx = col_index("Activity Type")
        duration_idx = col_index("Moving Time")       # seconds
        distance_idx = duration_idx + 1                # meters -- sits right after Moving Time
        rpe_idx = col_index("Perceived Exertion")      # blank on most of my runs
        name_idx = col_index("Activity Name")

        if header[distance_idx] != "Distance":
            print("expected a 'Distance' column right after 'Moving Time' but didn't find one")
            print(f"here's what's actually in the file: {header}")
            sys.exit(1)

        out_rows = []

        for row in raw_reader:
            activity_type = (row[type_idx] or "").strip().lower()
            if activity_type not in ("run", "trail run", "treadmill run"):
                rows_skipped += 1
                continue

            try:
                distance_m = float(row[distance_idx] or 0)
                duration_s = float(row[duration_idx] or 0)
            except ValueError:
                rows_skipped += 1
                continue

            if distance_m <= 0 or duration_s <= 0:
                rows_skipped += 1
                continue

            distance_mi = round(distance_m / 1609.344, 2)
            duration_min = round(duration_s / 60, 1)
            pace_min_per_mi = duration_min / distance_mi if distance_mi else 0

            raw_rpe = (row[rpe_idx] or "").strip()
            if raw_rpe:
                try:
                    rpe = float(raw_rpe)
                except ValueError:
                    rpe = estimate_rpe_from_pace(pace_min_per_mi)
            else:
                rpe = estimate_rpe_from_pace(pace_min_per_mi)

            date_str = parse_strava_date(row[date_idx])
            notes = (row[name_idx] or "").strip()

            out_rows.append({
                "date": date_str,
                "distance_mi": distance_mi,
                "duration_min": duration_min,
                "rpe": rpe,
                "notes": notes,
            })
            rows_written += 1

    out_rows.sort(key=lambda r: r["date"])

    # Added encoding="utf-8" below to prevent emoji-related crash
    with open(output_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(
            outfile, fieldnames=["date", "distance_mi", "duration_min", "rpe", "notes"]
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"wrote {rows_written} runs to {output_path}")
    print(f"skipped {rows_skipped} rows (not a run, or bad data)")
    if rows_written:
        print(f"heads up: rpe was guessed from pace wherever I didn't tag "
              f"perceived exertion myself. worth skimming {output_path} "
              f"before uploading in case any of those look off.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: python convert_strava_export.py activities.csv runload_import.csv")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])