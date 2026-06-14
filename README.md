# Hotel Booking Performance & Cancellation Analysis

An end-to-end hotel booking analytics project focused on cleaning raw booking data, preparing an analysis-ready dataset, and building a professional Streamlit dashboard for business insights.

The dashboard analyzes cancellation behavior, booking-channel risk, stay-length patterns, and net revenue stability using a cleaned hotel bookings dataset.

## Project Objective

The goal of this project is to identify meaningful business trends from hotel booking data and present them in a clear dashboard/report format.

Key business questions answered:

- What is the overall cancellation rate?
- Which booking segments have the highest cancellation risk?
- Are cancellations evenly distributed or concentrated around a specific lead-time window?
- Does net revenue vary meaningfully across booking channel, room type, or star rating?
- Do city, stay type, or star rating materially change cancellation behavior?

## Important Analysis Rule

Cancellation rate is calculated only from `booking_status`:

```text
Cancellation Rate = Cancelled / (Cancelled + Confirmed)
```

`Failed` bookings are excluded from cancellation-rate calculations.

Refund columns are not used to infer cancellations.

## Dashboard

The Streamlit dashboard includes:

- Executive KPI cards
- Key cancellation insights
- Booking-channel, room-type, and star-rating comparison tables
- Lead-time cancellation spike analysis
- Net revenue lift vs overall average
- Cancellation rate by stay length
- Additional checks for city and stay type

## Key Findings

- Overall cancellation rate: **21.9%**
- Lead-time cancellations spike in the **26-30 day gap before check-in**
- The 26-30 day band accounts for **51.1% of all cancellations**
- Four-night stays have the highest stay-length cancellation risk at **62.6%**
- Travel Agent bookings have the highest channel cancellation rate at **29.7%**
- Web bookings have the lowest channel cancellation rate at **18.6%**
- Star rating is not a major cancellation driver; the spread is only **1.6 percentage points**
- Net revenue is broadly stable across booking channel, room type, and star rating

## Files Included

| File | Purpose |
| --- | --- |
| `hotel_dashboard.py` | Streamlit dashboard application |
| `hotel_booking_analysis_code.py` | Analysis script that generates the business report |
| `hotel_booking_company_report.md` | Markdown report with key tables and findings |
| `preprocess_hotel_bookings.py` | Data preprocessing and cleaning script |
| `hotel_bookings_preprocessing_report.md` | Data cleaning audit report |
| `Hotel_bookings_cleaned_analysis_ready.csv` | Cleaned dataset used for analysis |
| `Hotel Booking Performance & Cancellation Analysis.pdf` | PDF export of the dashboard/report |
| `.streamlit/config.toml` | Streamlit theme configuration |

## Data Preprocessing Summary

The raw hotel bookings data was cleaned and prepared for analysis by:

- Standardizing column names
- Fixing invalid negative coupon values
- Correcting refund status using actual refund amount
- Handling missing check-in and check-out dates
- Adding date-imputation flags
- Checking and removing duplicate or broken records
- Creating analysis-ready fields such as:
  - `lead_time_days`
  - `nights`
  - `booking_month`
  - `check_in_month`
  - `gross_revenue`
  - `net_revenue`
  - `gross_margin`
  - `gross_margin_pct`

## How to Run

Install the required Python packages if needed:

```bash
pip install pandas plotly streamlit
```

Run the Streamlit dashboard:

```bash
python3 -m streamlit run hotel_dashboard.py
```

Then open:

```text
http://localhost:8501
```

## Regenerate the Report

To regenerate the Markdown business report:

```bash
python3 hotel_booking_analysis_code.py
```

This recreates:

```text
hotel_booking_company_report.md
```

## Regenerate the Clean Dataset

To rerun preprocessing:

```bash
python3 preprocess_hotel_bookings.py
```

This recreates:

```text
Hotel_bookings_cleaned_analysis_ready.csv
hotel_bookings_preprocessing_report.md
```

## Tech Stack

- Python
- Pandas
- Plotly
- Streamlit
- Git/GitHub

## Notes

- `channel_of_booking` is treated as a device/platform field, not a sales channel.
- Booking-channel analysis uses `booking_channel`.
- Cancellation analysis is based strictly on `booking_status`.
