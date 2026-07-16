"""
training load math.

core metric here is ACWR (acute:chronic workload ratio).

- daily load per session = duration_min * rpe (session-RPE / Foster's method)
- acute load = rolling 7-day average of daily load (how much I've been doing lately)
- chronic load = rolling 28-day average (my baseline fitness)
- ACWR = acute / chronic

risk bands below come from Gabbett's 2016 "sweet spot" research --
it's a widely used model in sports science, using it here as a
reasonable default, not diagnosing anything:

    ACWR < 0.8         -> "undertrained"   (detraining risk, doing too little)
    0.8 <= ACWR <= 1.3  -> "sweet spot"    (lower injury risk)
    1.3 < ACWR <= 1.5   -> "moderate risk" (load rising faster than fitness)
    ACWR > 1.5          -> "high risk"     (sharp spike in load)

built this for my own training awareness -- not a replacement for an
actual coach or doctor.
"""

from datetime import timedelta
import pandas as pd


# 7 days represents short-term fatigue; 28 days represents long-term fitness baseline.
ACUTE_WINDOW_DAYS = 7
CHRONIC_WINDOW_DAYS = 28

# Standard thresholds from sports science studies (specifically Gabbett, 2016).
RISK_BANDS = {
    "undertrained": (0.0, 0.8),
    "sweet spot": (0.8, 1.3),
    "moderate risk": (1.3, 1.5),
    "high risk": (1.5, float("inf")),
}

# Plain-language context to display in the frontend card so the numbers actually make sense to a human.
RECOMMENDATIONS = {
    "undertrained": "Load is well below your fitness baseline. Safe to gradually increase volume.",
    "sweet spot": "Load and fitness are well matched. This is a low-risk range to keep training in.",
    "moderate risk": "Load is climbing faster than your baseline. Consider holding volume steady for a few days.",
    "high risk": "Load has spiked sharply relative to your recent baseline. Consider a lighter or rest day.",
}


def classify_risk(acwr: float) -> str:
    # Quick utility to map a decimal ACWR ratio straight to its corresponding risk bracket.
    for label, (low, high) in RISK_BANDS.items():
        if low <= acwr < high:
            return label
    return "high risk"


def sessions_to_daily_series(sessions: list[dict]) -> pd.DataFrame:
    """
    turns a list of session dicts into a continuous daily series,
    filling rest days with 0 so the rolling averages are calculated
    over real calendar days, not just days I actually ran.
    """
    if not sessions:
        return pd.DataFrame(columns=["date", "daily_load"])

    df = pd.DataFrame(sessions)
    df["date"] = pd.to_datetime(df["date"])

    # If I log multiple runs on the same day, group and sum their workloads together first.
    daily = df.groupby("date")["load"].sum().rename("daily_load")

    # CRITICAL STEP: Without this reindex, if you only ran 3 times in a month, 
    # a rolling(7) window would stretch back months to find 7 runs!
    # By creating a full range of real calendar days and filling gaps with 0.0,
    # rolling(7) correctly calculates the last 7 calendar days.
    full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_range, fill_value=0.0)
    daily.index.name = "date"

    return daily.reset_index()


def compute_training_load_series(sessions: list[dict]) -> pd.DataFrame:
    """
    takes raw sessions and returns a day-by-day table with acute load,
    chronic load, ACWR, and risk_level all calculated
    """
    daily = sessions_to_daily_series(sessions)
    if daily.empty:
        return daily

    # Use .mean() over the rolling windows to find my daily average load for the periods.
    daily["acute_load"] = (
        daily["daily_load"].rolling(window=ACUTE_WINDOW_DAYS, min_periods=1).mean()
    )
    daily["chronic_load"] = (
        daily["daily_load"].rolling(window=CHRONIC_WINDOW_DAYS, min_periods=1).mean()
    )

    # ACWR doesn't mean much without a real chronic baseline built up,
    # so holding off until there's enough history to trust it
    # We require at least 14 days (half of the chronic window) before attempting to show a score.
    enough_history = daily.index >= (CHRONIC_WINDOW_DAYS // 2)

    # Prevent division by zero: if chronic_load is 0 (e.g. completely sedentary month),
    # replace it with pd.NA so the program doesn't crash with an error.
    daily["acwr"] = daily["acute_load"] / daily["chronic_load"].replace(0, pd.NA)
    daily.loc[~enough_history, "acwr"] = pd.NA

    # Apply our categorization function day-by-day across the full history.
    daily["risk_level"] = daily["acwr"].apply(
        lambda x: classify_risk(x) if pd.notna(x) else None
    )

    return daily


def get_current_risk(sessions: list[dict]) -> dict:
    """most recent day's ACWR plus a plain-language recommendation"""
    series = compute_training_load_series(sessions)

    days_of_data = len(series)
    has_enough_data = days_of_data >= CHRONIC_WINDOW_DAYS

    # Handle brand new setups with zero logs gracefully so the page doesn't break.
    if series.empty:
        return {
            "date": None,
            "acwr": None,
            "risk_level": "no data",
            "recommendation": "Upload or log training sessions to see your risk status.",
            "days_of_data": 0,
            "has_enough_data": False,
        }

    latest = series.iloc[-1]
    acwr = latest["acwr"]

    # If the user is in their first 2 weeeks, return a helpful setup status message.
    if pd.isna(acwr):
        return {
            "date": latest["date"].date(),
            "acwr": None,
            "risk_level": "insufficient data",
            "recommendation": (
                f"Need at least {CHRONIC_WINDOW_DAYS // 2} days of training history "
                "for a reliable ACWR. Keep logging sessions."
            ),
            "days_of_data": days_of_data,
            "has_enough_data": has_enough_data,
        }

    risk_level = classify_risk(acwr)
    return {
        "date": latest["date"].date(),
        # Round to 2 decimal places to make it look clean on the frontend gauge.
        "acwr": round(float(acwr), 2),
        "risk_level": risk_level,
        "recommendation": RECOMMENDATIONS[risk_level],
        "days_of_data": days_of_data,
        "has_enough_data": has_enough_data,
    }