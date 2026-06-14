# Hotel Bookings Preprocessing Report

## Files
- Raw input: `Hotel_bookings_final.csv`
- Clean output: `Hotel_bookings_cleaned_analysis_ready.csv`

## Data Quality Actions
- Raw shape: 30,000 rows x 24 columns.
- Exact duplicate rows removed: 0.
- Negative coupon values corrected to 0: 69.
- Selling price rows recalculated from costprice + markup: 0.
- Refund status corrected from refund_amount: 4,882 zero-refund rows changed to `No`.
- Missing check-in dates before/after: 5,468 / 0.
- Missing check-out dates before/after: 5,468 / 0.
- Date-imputed rows flagged in `date_imputed`: 5,468.
- Broken chronology rows removed: 0.
- Broken required-value rows removed: 0.
- Suspicious source travel dates flagged before booking: 24,398.
- Suspicious source travel dates flagged after checkout: 4,818.
- Final shape: 30,000 rows x 35 columns.

## Analysis-Ready Additions
- Standardized column names to snake_case.
- Converted date and numeric fields to proper types during processing.
- Added `lead_time_days`, `nights`, `booking_month`, and `check_in_month`.
- Added `gross_revenue`, `net_revenue`, `gross_margin`, and `gross_margin_pct`.
- Added `refund_issued`, `date_imputed`, and `travel_date_quality` flags for filtering.
