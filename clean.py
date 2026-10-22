"""
Jaipur hourly weather + air quality dataset (2025)
Fetches from Open-Meteo, cleans, validates, and writes:
  data/raw_jaipur.csv
  data/jaipur_weather_air_2025_clean.csv
  data/jaipur_daily_summary_2025.csv
  data/quality_report.txt
Run from anywhere:  python clean.py
"""
from pathlib import Path
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

LAT, LON = 26.9124, 75.7873  # Jaipur
START, END = "2025-01-01", "2025-12-31"
TZ = "Asia/Kolkata"

RENAME = {
    "time": "timestamp",
    "temperature_2m": "temp_c",
    "relative_humidity_2m": "humidity_pct",
    "precipitation": "precip_mm",
    "wind_speed_10m": "wind_kmh",
    "pm10": "pm10_ugm3",
    "pm2_5": "pm25_ugm3",
    "nitrogen_dioxide": "no2_ugm3",
    "ozone": "o3_ugm3",
}

# physically plausible ranges, used for flagging only (nothing is deleted)
RANGES = {
    "temp_c": (-5, 55),
    "humidity_pct": (0, 100),
    "precip_mm": (0, 150),
    "wind_kmh": (0, 150),
    "pm10_ugm3": (0, 2000),
    "pm25_ugm3": (0, 1000),
    "no2_ugm3": (0, 1000),
    "o3_ugm3": (0, 1000),
}


def fetch():
    w = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={"latitude": LAT, "longitude": LON, "start_date": START,
                "end_date": END, "timezone": TZ,
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m"},
        timeout=60)
    w.raise_for_status()
    a = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={"latitude": LAT, "longitude": LON, "start_date": START,
                "end_date": END, "timezone": TZ,
                "hourly": "pm10,pm2_5,nitrogen_dioxide,ozone"},
        timeout=60)
    a.raise_for_status()
    return pd.DataFrame(w.json()["hourly"]).merge(
        pd.DataFrame(a.json()["hourly"]), on="time", how="outer")


def clean(raw):
    log = []
    df = raw.copy()
    df["time"] = pd.to_datetime(df["time"])
    n0 = len(df)
    df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    log.append(f"Rows in raw: {n0}; duplicates removed: {n0 - len(df)}")
    df = df.rename(columns=RENAME)

    # make sure the hourly index is complete
    full = pd.date_range(df["timestamp"].min(), df["timestamp"].max(), freq="h")
    missing_hours = len(full) - len(df)
    df = df.set_index("timestamp").reindex(full).rename_axis("timestamp")
    log.append(f"Missing hourly timestamps re-inserted: {missing_hours}")

    # flag out-of-range values (kept, but flagged)
    flagged = pd.Series(False, index=df.index)
    for col, (lo, hi) in RANGES.items():
        bad = (df[col] < lo) | (df[col] > hi)
        log.append(f"Out-of-range values in {col}: {int(bad.sum())}")
        flagged |= bad.fillna(False)

    na_before = df.isna().sum()
    df = df.interpolate(limit=3, limit_area="inside")
    na_after = df.isna().sum()
    log.append("Missing values per column (before -> after interpolation, max gap 3h):")
    for c in df.columns:
        log.append(f"  {c}: {int(na_before[c])} -> {int(na_after[c])}")

    df["was_flagged"] = flagged.astype(int)
    return df.reset_index(), log


def cpcb_pm25(x):
    # CPCB India 24-hour PM2.5 breakpoints (ug/m3)
    if pd.isna(x): return None
    for hi, name in [(30, "Good"), (60, "Satisfactory"), (90, "Moderate"),
                     (120, "Poor"), (250, "Very Poor")]:
        if x <= hi: return name
    return "Severe"


def cpcb_pm10(x):
    # CPCB India 24-hour PM10 breakpoints (ug/m3)
    if pd.isna(x): return None
    for hi, name in [(50, "Good"), (100, "Satisfactory"), (250, "Moderate"),
                     (350, "Poor"), (430, "Very Poor")]:
        if x <= hi: return name
    return "Severe"


def daily(df):
    d = df.set_index("timestamp")
    out = pd.DataFrame({
        "temp_mean_c": d["temp_c"].resample("D").mean(),
        "temp_min_c": d["temp_c"].resample("D").min(),
        "temp_max_c": d["temp_c"].resample("D").max(),
        "humidity_mean_pct": d["humidity_pct"].resample("D").mean(),
        "precip_total_mm": d["precip_mm"].resample("D").sum(min_count=1),
        "wind_mean_kmh": d["wind_kmh"].resample("D").mean(),
        "pm10_mean_ugm3": d["pm10_ugm3"].resample("D").mean(),
        "pm25_mean_ugm3": d["pm25_ugm3"].resample("D").mean(),
        "no2_mean_ugm3": d["no2_ugm3"].resample("D").mean(),
        "o3_mean_ugm3": d["o3_ugm3"].resample("D").mean(),
        "hours_with_data": d["temp_c"].resample("D").count(),
    }).round(2)
    out["pm25_category_cpcb"] = out["pm25_mean_ugm3"].map(cpcb_pm25)
    out["pm10_category_cpcb"] = out["pm10_mean_ugm3"].map(cpcb_pm10)
    return out.reset_index().rename(columns={"timestamp": "date"})


def main():
    raw = fetch()
    raw.to_csv(DATA / "raw_jaipur.csv", index=False)

    df, log = clean(raw)
    df.round(2).to_csv(DATA / "jaipur_weather_air_2025_clean.csv", index=False)
    daily(df).to_csv(DATA / "jaipur_daily_summary_2025.csv", index=False)

    log.append(f"Final rows: {len(df)} (expected 8760 for a full non-leap year)")
    log.append("Min / max after cleaning:")
    for c in RANGES:
        log.append(f"  {c}: {df[c].min():.2f} / {df[c].max():.2f}")
    (DATA / "quality_report.txt").write_text("\n".join(log), encoding="utf-8")
    print("\n".join(log))


if __name__ == "__main__":
    main()
