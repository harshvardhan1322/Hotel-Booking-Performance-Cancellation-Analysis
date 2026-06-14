from pathlib import Path

import pandas as pd


RAW_FILE = Path("Hotel_bookings_final.csv")
CLEAN_FILE = Path("Hotel_bookings_cleaned_analysis_ready.csv")
REPORT_FILE = Path("hotel_bookings_preprocessing_report.md")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {
        "Coupon USed?": "coupon_used",
    }
    df = df.rename(columns=renamed)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^0-9a-zA-Z]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def yes_no_from_bool(value: bool) -> str:
    return "Yes" if value else "No"


def main() -> None:
    raw = pd.read_csv(RAW_FILE)
    report = {
        "raw_rows": len(raw),
        "raw_columns": len(raw.columns),
        "exact_duplicate_rows": int(raw.duplicated().sum()),
    }

    df = normalize_columns(raw.copy())
    df = df.drop_duplicates().reset_index(drop=True)

    text_cols = [
        "city",
        "room_type",
        "stay_type",
        "booking_channel",
        "payment_method",
        "refund_status",
        "channel_of_booking",
        "booking_status",
        "coupon_used",
    ]
    for col in text_cols:
        df[col] = df[col].astype("string").str.strip()

    date_cols = ["booking_date", "check_in_date", "check_out_date", "travel_date"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    numeric_cols = [
        "customer_id",
        "property_id",
        "star_rating",
        "num_rooms_booked",
        "booking_value",
        "costprice",
        "markup",
        "selling_price",
        "refund_amount",
        "cashback",
        "coupon_redeem",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    report["missing_check_in_dates_before"] = int(df["check_in_date"].isna().sum())
    report["missing_check_out_dates_before"] = int(df["check_out_date"].isna().sum())

    # Fix monetary consistency where source fields are derivable.
    report["negative_coupon_values_fixed"] = int((df["coupon_redeem"] < 0).sum())
    df["coupon_redeem"] = df["coupon_redeem"].clip(lower=0)

    expected_selling_price = df["costprice"] + df["markup"]
    price_mismatch = df["selling_price"].ne(expected_selling_price)
    report["selling_price_recalculated_rows"] = int(price_mismatch.sum())
    df.loc[price_mismatch, "selling_price"] = expected_selling_price[price_mismatch]

    df["coupon_used"] = df["coupon_redeem"].gt(0).map(yes_no_from_bool)
    df["refund_issued"] = df["refund_amount"].gt(0)
    report["refund_status_yes_with_zero_amount_fixed"] = int(
        df["refund_status"].eq("Yes").fillna(False).mul(df["refund_amount"].eq(0)).sum()
    )
    df["refund_status"] = df["refund_issued"].map(yes_no_from_bool)

    # Keep rows useful for cancelled/failed booking analysis, but make imputed dates auditable.
    df["date_imputed"] = df["check_in_date"].isna() | df["check_out_date"].isna()
    complete_dates = df.dropna(subset=["booking_date", "check_in_date", "check_out_date"]).copy()
    complete_dates["lead_time_days_tmp"] = (
        complete_dates["check_in_date"] - complete_dates["booking_date"]
    ).dt.days
    complete_dates["nights_tmp"] = (
        complete_dates["check_out_date"] - complete_dates["check_in_date"]
    ).dt.days

    median_lead_by_group = complete_dates.groupby(["city", "room_type"])[
        "lead_time_days_tmp"
    ].median()
    median_nights_by_group = complete_dates.groupby(["city", "room_type"])[
        "nights_tmp"
    ].median()
    global_lead = int(round(complete_dates["lead_time_days_tmp"].median()))
    global_nights = int(round(complete_dates["nights_tmp"].median()))

    missing_date_mask = df["check_in_date"].isna() | df["check_out_date"].isna()
    for idx in df.index[missing_date_mask]:
        key = (df.at[idx, "city"], df.at[idx, "room_type"])
        lead = median_lead_by_group.get(key, global_lead)
        nights = median_nights_by_group.get(key, global_nights)
        lead = int(round(float(lead))) if pd.notna(lead) else global_lead
        nights = int(round(float(nights))) if pd.notna(nights) else global_nights

        if pd.isna(df.at[idx, "check_in_date"]):
            df.at[idx, "check_in_date"] = df.at[idx, "booking_date"] + pd.Timedelta(days=lead)
        if pd.isna(df.at[idx, "check_out_date"]):
            df.at[idx, "check_out_date"] = df.at[idx, "check_in_date"] + pd.Timedelta(days=nights)

    report["missing_check_in_dates_after"] = int(df["check_in_date"].isna().sum())
    report["missing_check_out_dates_after"] = int(df["check_out_date"].isna().sum())

    invalid_chronology = (
        df["booking_date"].isna()
        | df["check_in_date"].isna()
        | df["check_out_date"].isna()
        | (df["check_in_date"] < df["booking_date"])
        | (df["check_out_date"] <= df["check_in_date"])
    )
    report["broken_chronology_rows_removed"] = int(invalid_chronology.sum())
    df = df.loc[~invalid_chronology].copy()

    required_non_null = [
        "customer_id",
        "property_id",
        "city",
        "star_rating",
        "room_type",
        "booking_status",
        "selling_price",
    ]
    broken_required = df[required_non_null].isna().any(axis=1)
    report["broken_required_value_rows_removed"] = int(broken_required.sum())
    df = df.loc[~broken_required].copy()

    # The source travel_date is not a reliable stay date, so preserve it and flag it.
    df["travel_date_quality"] = "valid"
    df.loc[df["travel_date"].isna(), "travel_date_quality"] = "missing"
    df.loc[df["travel_date"] < df["booking_date"], "travel_date_quality"] = "before_booking"
    df.loc[df["travel_date"] > df["check_out_date"], "travel_date_quality"] = "after_checkout"

    df["lead_time_days"] = (df["check_in_date"] - df["booking_date"]).dt.days
    df["nights"] = (df["check_out_date"] - df["check_in_date"]).dt.days
    df["booking_month"] = df["booking_date"].dt.to_period("M").astype(str)
    df["check_in_month"] = df["check_in_date"].dt.to_period("M").astype(str)
    df["gross_revenue"] = df["selling_price"]
    df["net_revenue"] = (
        df["selling_price"] - df["refund_amount"] - df["cashback"] - df["coupon_redeem"]
    ).round(2)
    df["gross_margin"] = df["markup"]
    df["gross_margin_pct"] = (df["markup"] / df["selling_price"]).round(4)

    int_cols = [
        "customer_id",
        "property_id",
        "star_rating",
        "num_rooms_booked",
        "costprice",
        "markup",
        "selling_price",
        "lead_time_days",
        "nights",
    ]
    for col in int_cols:
        df[col] = df[col].astype("int64")

    df = df.sort_values(["booking_date", "customer_id", "property_id"]).reset_index(drop=True)

    for col in date_cols:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

    report["final_rows"] = len(df)
    report["final_columns"] = len(df.columns)
    report["date_imputed_rows"] = int(df["date_imputed"].sum())
    report["travel_date_before_booking_flagged"] = int(
        df["travel_date_quality"].eq("before_booking").sum()
    )
    report["travel_date_after_checkout_flagged"] = int(
        df["travel_date_quality"].eq("after_checkout").sum()
    )

    df.to_csv(CLEAN_FILE, index=False)

    lines = [
        "# Hotel Bookings Preprocessing Report",
        "",
        "## Files",
        f"- Raw input: `{RAW_FILE}`",
        f"- Clean output: `{CLEAN_FILE}`",
        "",
        "## Data Quality Actions",
        f"- Raw shape: {report['raw_rows']:,} rows x {report['raw_columns']:,} columns.",
        f"- Exact duplicate rows removed: {report['exact_duplicate_rows']:,}.",
        f"- Negative coupon values corrected to 0: {report['negative_coupon_values_fixed']:,}.",
        f"- Selling price rows recalculated from costprice + markup: {report['selling_price_recalculated_rows']:,}.",
        f"- Refund status corrected from refund_amount: {report['refund_status_yes_with_zero_amount_fixed']:,} zero-refund rows changed to `No`.",
        f"- Missing check-in dates before/after: {report['missing_check_in_dates_before']:,} / {report['missing_check_in_dates_after']:,}.",
        f"- Missing check-out dates before/after: {report['missing_check_out_dates_before']:,} / {report['missing_check_out_dates_after']:,}.",
        f"- Date-imputed rows flagged in `date_imputed`: {report['date_imputed_rows']:,}.",
        f"- Broken chronology rows removed: {report['broken_chronology_rows_removed']:,}.",
        f"- Broken required-value rows removed: {report['broken_required_value_rows_removed']:,}.",
        f"- Suspicious source travel dates flagged before booking: {report['travel_date_before_booking_flagged']:,}.",
        f"- Suspicious source travel dates flagged after checkout: {report['travel_date_after_checkout_flagged']:,}.",
        f"- Final shape: {report['final_rows']:,} rows x {report['final_columns']:,} columns.",
        "",
        "## Analysis-Ready Additions",
        "- Standardized column names to snake_case.",
        "- Converted date and numeric fields to proper types during processing.",
        "- Added `lead_time_days`, `nights`, `booking_month`, and `check_in_month`.",
        "- Added `gross_revenue`, `net_revenue`, `gross_margin`, and `gross_margin_pct`.",
        "- Added `refund_issued`, `date_imputed`, and `travel_date_quality` flags for filtering.",
    ]
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Created {CLEAN_FILE} with {len(df):,} rows and {len(df.columns):,} columns")
    print(f"Created {REPORT_FILE}")


if __name__ == "__main__":
    main()
