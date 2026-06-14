from pathlib import Path

import pandas as pd


DATA_FILE = Path("Hotel_bookings_cleaned_analysis_ready.csv")
REPORT_FILE = Path("hotel_booking_company_report.md")
VALID_STATUSES = ["Confirmed", "Cancelled"]


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def money(value: float) -> str:
    return f"${value:,.0f}"


def comparison_table(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    valid = df[df["booking_status"].isin(VALID_STATUSES)]
    table = (
        valid.groupby(dimension, dropna=False)
        .agg(
            booking_count=("booking_status", "size"),
            cancellations=("booking_status", lambda s: (s == "Cancelled").sum()),
            avg_net_revenue=("net_revenue", "mean"),
            avg_nights=("nights", "mean"),
        )
        .reset_index()
    )
    table["share_pct"] = table["booking_count"] / table["booking_count"].sum()
    table["cancellation_rate"] = table["cancellations"] / table["booking_count"]
    return table.sort_values("cancellation_rate", ascending=False).reset_index(drop=True)


def display_table(table: pd.DataFrame, dimension: str) -> pd.DataFrame:
    output = table.copy()
    output["Share %"] = output["share_pct"].map(pct)
    output["Cancellation Rate"] = output["cancellation_rate"].map(pct)
    output["Avg Net Revenue"] = output["avg_net_revenue"].map(money)
    output["Avg Nights"] = output["avg_nights"].map(lambda v: f"{v:.2f}")
    output = output.rename(
        columns={
            dimension: dimension.replace("_", " ").title(),
            "booking_count": "Booking Count",
        }
    )
    return output[
        [
            dimension.replace("_", " ").title(),
            "Booking Count",
            "Share %",
            "Cancellation Rate",
            "Avg Net Revenue",
            "Avg Nights",
        ]
    ]


def markdown_table(table: pd.DataFrame) -> str:
    headers = [str(col) for col in table.columns]
    rows = table.astype(str).values.tolist()
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    df = pd.read_csv(DATA_FILE)
    valid = df[df["booking_status"].isin(VALID_STATUSES)].copy()

    cancelled = int(valid["booking_status"].eq("Cancelled").sum())
    confirmed = int(valid["booking_status"].eq("Confirmed").sum())
    overall_cancel_rate = cancelled / (cancelled + confirmed)

    booking_channel = comparison_table(df, "booking_channel")
    room_type = comparison_table(df, "room_type")
    star_rating = comparison_table(df, "star_rating")
    city = comparison_table(df, "city")
    stay_type = comparison_table(df, "stay_type")
    nights = comparison_table(df, "nights")

    lead_bins = list(range(0, 66, 5))
    valid["lead_time_band"] = pd.cut(
        valid["lead_time_days"],
        bins=lead_bins,
        right=True,
        include_lowest=True,
        labels=[f"{start + 1}-{end}" if start else "1-5" for start, end in zip(lead_bins[:-1], lead_bins[1:])],
    )
    lead_table = (
        valid.groupby("lead_time_band", observed=False)
        .agg(
            bookings=("booking_status", "size"),
            cancellations=("booking_status", lambda s: (s == "Cancelled").sum()),
            avg_net_revenue=("net_revenue", "mean"),
            avg_nights=("nights", "mean"),
        )
        .reset_index()
    )
    lead_table = lead_table[lead_table["bookings"] > 0].copy()
    lead_table["cancellation_rate"] = lead_table["cancellations"] / lead_table["bookings"]
    lead_table["cancel_share"] = lead_table["cancellations"] / cancelled
    spike = lead_table.sort_values("cancellation_rate", ascending=False).iloc[0]
    spike_start, spike_end = [int(value) for value in str(spike["lead_time_band"]).split("-")]
    spike_cancel_records = valid[
        valid["lead_time_days"].between(spike_start, spike_end)
        & valid["booking_status"].eq("Cancelled")
    ].copy()
    spike_cancel_records["booking_date"] = pd.to_datetime(spike_cancel_records["booking_date"])
    spike_cancel_records["check_in_date"] = pd.to_datetime(spike_cancel_records["check_in_date"])
    spike_booking_window = (
        f"{spike_cancel_records['booking_date'].min().strftime('%b %d, %Y')} - "
        f"{spike_cancel_records['booking_date'].max().strftime('%b %d, %Y')}"
    )
    spike_checkin_window = (
        f"{spike_cancel_records['check_in_date'].min().strftime('%b %d, %Y')} - "
        f"{spike_cancel_records['check_in_date'].max().strftime('%b %d, %Y')}"
    )

    four_night_rate = float(nights.loc[nights["nights"].eq(4), "cancellation_rate"].iloc[0])
    other_night_rate = (
        valid[valid["nights"].ne(4)]["booking_status"].eq("Cancelled").sum()
        / valid[valid["nights"].ne(4)].shape[0]
    )

    channel_high = booking_channel.iloc[0]
    channel_low = booking_channel.iloc[-1]
    room_high = room_type.iloc[0]
    room_low = room_type.iloc[-1]
    star_gap = star_rating["cancellation_rate"].max() - star_rating["cancellation_rate"].min()
    city_gap = city["cancellation_rate"].max() - city["cancellation_rate"].min()
    stay_type_gap = stay_type["cancellation_rate"].max() - stay_type["cancellation_rate"].min()

    lead_output = lead_table.copy()
    lead_output["Cancellation Rate"] = lead_output["cancellation_rate"].map(pct)
    lead_output["Share of Cancellations"] = lead_output["cancel_share"].map(pct)
    lead_output = lead_output.rename(
        columns={
            "lead_time_band": "Lead-Time Band",
            "bookings": "Bookings",
            "cancellations": "Cancellations",
        }
    )
    lead_output = lead_output[
        ["Lead-Time Band", "Bookings", "Cancellations", "Cancellation Rate", "Share of Cancellations"]
    ]

    lines = [
        "# Hotel Booking Business Insights Report",
        "",
        "## Executive Summary",
        f"- Total analyzed bookings: {len(valid):,} Confirmed/Cancelled bookings.",
        f"- Overall cancellation rate: {pct(overall_cancel_rate)} ({cancelled:,} Cancelled / {cancelled + confirmed:,} Confirmed + Cancelled).",
        f"- Average net revenue: {money(valid['net_revenue'].mean())}.",
        f"- Average stay length: {valid['nights'].mean():.2f} nights.",
        "",
        "## Most Meaningful Trends",
        f"1. Lead-time cancellations spike in the {spike['lead_time_band']} day gap before check-in: {pct(float(spike['cancellation_rate']))} cancellation rate and {pct(float(spike['cancel_share']))} of all cancellations. Booking dates in this spike range from {spike_booking_window}; check-in dates range from {spike_checkin_window}. Why it matters: this points to a likely cancellation-policy or reminder deadline window.",
        f"2. Four-night stays cancel at {pct(four_night_rate)}, compared with {pct(other_night_rate)} for all other stay lengths combined. Why it matters: stay length is a strong cancellation-risk signal.",
        f"3. Travel Agent bookings have the highest cancellation rate at {pct(float(channel_high['cancellation_rate']))}, while Web is lowest at {pct(float(channel_low['cancellation_rate']))}. Why it matters: cancellation management should vary by sales channel.",
        f"4. Star rating is not a major cancellation driver: the highest and lowest star-rating cancellation rates differ by only {star_gap * 100:.1f} percentage points. Why it matters: focus more on lead time, booking channel, and stay length because those show clearer differences.",
        "",
        "## Booking Channel Comparison",
        markdown_table(display_table(booking_channel, "booking_channel")),
        "",
        "Direction: Cancellations from Travel Agent bookings are the highest; Web bookings have the lowest cancellation rate. Avg net revenue is broadly stable across channels.",
        "",
        "## Room Type Comparison",
        markdown_table(display_table(room_type, "room_type")),
        "",
        "Direction: Standard rooms have the highest cancellation rate; Deluxe has the lowest. Avg net revenue and nights show no meaningful difference.",
        "",
        "## Star Rating Comparison",
        markdown_table(display_table(star_rating, "star_rating")),
        "",
        f"Direction: Star rating is not a major cancellation driver; the highest and lowest star-rating cancellation rates differ by only {star_gap * 100:.1f} percentage points.",
        "",
        "## Lead-Time Cancellation Analysis",
        markdown_table(lead_output),
        "",
        f"Cancellation behavior is concentrated, not evenly spread. The largest spike is {spike['lead_time_band']} days before check-in, accounting for {pct(float(spike['cancel_share']))} of all cancellations. Booking dates in this spike range from {spike_booking_window}; check-in dates range from {spike_checkin_window}.",
        "",
        "## Additional Checks",
        f"- City cancellation-rate spread: {city_gap * 100:.1f} percentage points, so city is not a major driver.",
        f"- Stay type cancellation-rate spread: {stay_type_gap * 100:.1f} percentage points, so Business vs Leisure is not a major driver.",
        "- `channel_of_booking` was ignored because it is a device field, not a sales channel.",
        "- Cancellation was measured only from `booking_status`; refund columns were not used.",
    ]

    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report created: {REPORT_FILE}")


if __name__ == "__main__":
    main()
