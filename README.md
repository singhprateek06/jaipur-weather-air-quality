# Jaipur Hourly Weather & Air Quality Dataset (2025)

A cleaned, validated and documented hourly dataset of weather and air pollution for Jaipur, Rajasthan, India, covering 1 Jan 2025 to 31 Dec 2025. Built for open research, teaching and data-science practice. Includes the raw download, the cleaned version, a daily summary with Indian CPCB air-quality categories, and the full script to reproduce everything.

<img src="images/profile.jpg" alt="Profile photo" width="110" align="right">

**Prepared by:** Prateek Singh
**Department:** Department of CSE, Manipal University Jaipur (MUJ)
**Contact:** prateek.2430010279@muj.manipal.edu
**GitHub:** https://github.com/singhprateek06

---

## Quick facts

| | |
|---|---|
| Location | Jaipur (26.9124 N, 75.7873 E) |
| Period | 2025-01-01 to 2025-12-31 |
| Resolution | Hourly (daily summary also included) |
| Rows (hourly) | 8,760 |
| Timezone | Asia/Kolkata (IST, UTC+05:30) |
| Variables | 4 weather + 4 air-quality |
| Source | Open-Meteo Historical Weather API and Air Quality API |

## Repository contents

| Path | Description |
|---|---|
| `data/raw_jaipur.csv` | Raw merged API output, untouched |
| `data/jaipur_weather_air_2025_clean.csv` | Cleaned hourly data (main file) |
| `data/jaipur_daily_summary_2025.csv` | Daily aggregates plus CPCB categories |
| `data/quality_report.txt` | Auto-generated cleaning and validation log |
| `clean.py` | Script that downloads, cleans, validates and exports everything |
| `requirements.txt` | Python dependencies |
| `LICENSE` | MIT licence (code) |
| `DATA_LICENSE.md` | CC BY 4.0 notice (data) |

## Data dictionary

### `jaipur_weather_air_2025_clean.csv` (hourly)

| Column | Type | Unit | Description | Source variable |
|---|---|---|---|---|
| `timestamp` | datetime | IST | Start of the hour, local time | `time` |
| `temp_c` | float | °C | Air temperature at 2 m above ground | `temperature_2m` |
| `humidity_pct` | float | % | Relative humidity at 2 m | `relative_humidity_2m` |
| `precip_mm` | float | mm | Total precipitation in the preceding hour | `precipitation` |
| `wind_kmh` | float | km/h | Wind speed at 10 m above ground | `wind_speed_10m` |
| `pm10_ugm3` | float | µg/m³ | Particulate matter, diameter < 10 µm | `pm10` |
| `pm25_ugm3` | float | µg/m³ | Particulate matter, diameter < 2.5 µm | `pm2_5` |
| `no2_ugm3` | float | µg/m³ | Nitrogen dioxide | `nitrogen_dioxide` |
| `o3_ugm3` | float | µg/m³ | Ozone | `ozone` |
| `was_flagged` | int (0/1) | none | 1 if any value in that row fell outside the plausible range (see below); values are kept, not removed | derived |

### `jaipur_daily_summary_2025.csv` (daily)

| Column | Unit | Description |
|---|---|---|
| `date` | date | Calendar day (IST) |
| `temp_mean_c`, `temp_min_c`, `temp_max_c` | °C | Daily mean, minimum, maximum temperature |
| `humidity_mean_pct` | % | Daily mean relative humidity |
| `precip_total_mm` | mm | Daily total precipitation |
| `wind_mean_kmh` | km/h | Daily mean wind speed |
| `pm10_mean_ugm3`, `pm25_mean_ugm3` | µg/m³ | Daily mean particulate matter |
| `no2_mean_ugm3`, `o3_mean_ugm3` | µg/m³ | Daily mean NO₂ and O₃ |
| `hours_with_data` | count | Hours of valid data used for that day (max 24) |
| `pm25_category_cpcb` | category | Good / Satisfactory / Moderate / Poor / Very Poor / Severe, from daily mean PM2.5 |
| `pm10_category_cpcb` | category | Same, from daily mean PM10 |

CPCB breakpoints used (24-hour mean, µg/m³):

| Category | PM2.5 | PM10 |
|---|---|---|
| Good | 0–30 | 0–50 |
| Satisfactory | 31–60 | 51–100 |
| Moderate | 61–90 | 101–250 |
| Poor | 91–120 | 251–350 |
| Very Poor | 121–250 | 351–430 |
| Severe | > 250 | > 430 |

These categories are a simplified classification of each pollutant on its own. They are not the full official AQI, which also uses the other pollutants and minimum-data rules.

## Cleaning and validation steps

1. Merged weather and air-quality tables on timestamp (outer join, so nothing is lost).
2. Parsed timestamps, removed duplicate timestamps, sorted chronologically.
3. Checked the hourly index is complete and re-inserted any missing hours as empty rows.
4. Renamed columns so every name carries its unit.
5. Flagged physically implausible values (ranges below). Nothing is deleted automatically.
6. Filled only short gaps (up to 3 consecutive hours) by linear interpolation. Longer gaps stay empty so no data is invented.
7. Rounded values to 2 decimals and exported.

Plausibility ranges used for flagging: temperature −5 to 55 °C, humidity 0–100 %, precipitation 0–150 mm/h, wind 0–150 km/h, PM10 0–2000, PM2.5 0–1000, NO₂ 0–1000, O₃ 0–1000 (µg/m³).

### Results of the run

Copy the numbers from `data/quality_report.txt` here after running the script:

- Duplicate timestamps removed: 0
- Missing hours re-inserted: 0
- Missing values after cleaning: 0
- Rows flagged as out of range: 0
- Final row count: 8,760

## How to reproduce

```bash
git clone https://github.com/singhprateek06/jaipur-weather-air-quality.git
cd jaipur-weather-air-quality
pip install -r requirements.txt
python clean.py
```

## Quick start for analysis

```python
import pandas as pd

df = pd.read_csv("data/jaipur_weather_air_2025_clean.csv", parse_dates=["timestamp"])
print(df.describe())

# monthly mean PM2.5
print(df.set_index("timestamp")["pm25_ugm3"].resample("MS").mean())
```

## Limitations

- **These are modelled values, not station readings.** Weather comes from reanalysis/forecast models and air quality from atmospheric composition models (CAMS). They can differ from ground monitors, especially during local pollution spikes.
- The values represent a grid cell around the coordinates, not an exact street-level point.
- Interpolation was applied to gaps of at most 3 hours; check `quality_report.txt` for how much was filled.
- Not suitable for regulatory or health-critical decisions.

## Possible uses

Seasonal pollution analysis (post-monsoon and winter PM2.5 in particular), weather–pollution correlation, time-series forecasting practice, visualisation projects, and teaching data cleaning.

## Citation

If you use this dataset, please cite:

> Prateek Singh (2026). *Jaipur Hourly Weather & Air Quality Dataset (2025)*. Manipal University Jaipur. https://github.com/singhprateek06/jaipur-weather-air-quality

and attribute the underlying data: *Weather data by Open-Meteo.com (CC BY 4.0).* Open-Meteo's own pages list the upstream sources (Copernicus ERA5 and CAMS), which should also be acknowledged.

## Licence

Data: CC BY 4.0 (see `DATA_LICENSE.md`). Code: MIT (see `LICENSE`).

Rows in raw: 8760; duplicates removed: 0
Missing hourly timestamps re-inserted: 0
Out-of-range values in temp_c: 0
Out-of-range values in humidity_pct: 0
Out-of-range values in precip_mm: 0
Out-of-range values in wind_kmh: 0
Out-of-range values in pm10_ugm3: 0
Out-of-range values in pm25_ugm3: 0
Out-of-range values in no2_ugm3: 0
Out-of-range values in o3_ugm3: 0
Missing values per column (before -> after interpolation, max gap 3h):
  temp_c: 0 -> 0
  humidity_pct: 0 -> 0
  precip_mm: 0 -> 0
  wind_kmh: 0 -> 0
  pm10_ugm3: 0 -> 0
  pm25_ugm3: 0 -> 0
  no2_ugm3: 0 -> 0
  o3_ugm3: 0 -> 0
Final rows: 8760 (expected 8760 for a full non-leap year)
Min / max after cleaning:
  temp_c: 6.50 / 44.20
  humidity_pct: 3.00 / 100.00
  precip_mm: 0.00 / 10.30
  wind_kmh: 0.00 / 25.00
  pm10_ugm3: 3.20 / 590.50
  pm25_ugm3: 3.20 / 147.60
  no2_ugm3: 0.00 / 88.20
  o3_ugm3: 5.00 / 201.00
