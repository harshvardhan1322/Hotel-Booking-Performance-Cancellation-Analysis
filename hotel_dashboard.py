from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE = Path("Hotel_bookings_cleaned_analysis_ready.csv")
VALID_STATUSES = ["Confirmed", "Cancelled"]
COLORS = {
    "teal": "#0F766E",
    "red": "#DC2626",
    "blue": "#2563EB",
    "amber": "#D97706",
    "ink": "#111827",
    "muted": "#4B5563",
    "line": "#D1D5DB",
    "soft": "#F8FAFC",
    "navy": "#123047",
    "panel": "#FFFFFF",
}


st.set_page_config(
    page_title="Hotel Booking Performance & Cancellation Analysis",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    for col in ["booking_date", "check_in_date", "check_out_date", "travel_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def money(value: float) -> str:
    return f"${value:,.0f}"


def comparison_table(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    base = df[df["booking_status"].isin(VALID_STATUSES)].copy()
    grouped = (
        base.groupby(dimension, dropna=False)
        .agg(
            booking_count=("booking_status", "size"),
            cancellations=("booking_status", lambda s: (s == "Cancelled").sum()),
            avg_net_revenue=("net_revenue", "mean"),
            avg_nights=("nights", "mean"),
        )
        .reset_index()
    )
    grouped["share_pct"] = grouped["booking_count"] / grouped["booking_count"].sum()
    grouped["cancellation_rate"] = grouped["cancellations"] / grouped["booking_count"]
    return grouped.sort_values("cancellation_rate", ascending=False).reset_index(drop=True)


def format_table(table: pd.DataFrame, dimension: str) -> pd.DataFrame:
    result = table.copy()
    result["Share %"] = result["share_pct"].map(lambda v: f"{v * 100:.1f}%")
    result["Cancellation Rate"] = result["cancellation_rate"].map(pct)
    result["Avg Net Revenue"] = result["avg_net_revenue"].map(money)
    result["Avg Nights"] = result["avg_nights"].map(lambda v: f"{v:.2f}")
    result = result.rename(
        columns={
            dimension: dimension.replace("_", " ").title(),
            "booking_count": "Bookings",
        }
    )
    return result[
        [
            dimension.replace("_", " ").title(),
            "Bookings",
            "Share %",
            "Cancellation Rate",
            "Avg Net Revenue",
            "Avg Nights",
        ]
    ]


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(title: str, value: str, finding: str, impact: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
          <div class="card-label">Key Insight</div>
          <h3>{title}</h3>
          <div class="insight-value">{value}</div>
          <p>{finding}</p>
          <div class="impact"><b>Business impact:</b> {impact}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clean_chart(fig, height: int = 420):
    fig.update_layout(
        height=height,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color=COLORS["ink"], size=13),
        title=dict(font=dict(color=COLORS["ink"], size=19)),
        xaxis=dict(
            title_font=dict(color=COLORS["ink"], size=14),
            tickfont=dict(color=COLORS["ink"], size=12),
            gridcolor="#E5E7EB",
            linecolor=COLORS["line"],
        ),
        yaxis=dict(
            title_font=dict(color=COLORS["ink"], size=14),
            tickfont=dict(color=COLORS["ink"], size=12),
            gridcolor="#E5E7EB",
            linecolor=COLORS["line"],
        ),
        legend=dict(font=dict(color=COLORS["ink"], size=13), title_font=dict(color=COLORS["ink"])),
        margin=dict(l=24, r=24, t=58, b=48),
    )
    return fig


def revenue_lift_display(table: pd.DataFrame) -> pd.DataFrame:
    display = table.sort_values("Revenue Lift", ascending=False).copy()
    display["Bookings"] = display["booking_count"].map(lambda v: f"{int(v):,}")
    display["Avg Net Revenue"] = display["avg_net_revenue"].map(money)
    display["Lift $"] = display["Revenue Lift"].map(lambda v: f"${v:+,.0f}")
    display["Lift %"] = display["Revenue Lift %"].map(lambda v: f"{v * 100:+.2f}%")
    return display[["Segment", "Bookings", "Avg Net Revenue", "Lift $", "Lift %"]]


def nights_display(table: pd.DataFrame) -> pd.DataFrame:
    display = table.sort_values("nights").copy()
    display["Nights"] = display["nights"].astype(int)
    display["Bookings"] = display["booking_count"].map(lambda v: f"{int(v):,}")
    display["Cancellation Rate"] = display["cancellation_rate"].map(pct)
    display["Avg Net Revenue"] = display["avg_net_revenue"].map(money)
    return display[["Nights", "Bookings", "Cancellation Rate", "Avg Net Revenue"]]


df = load_data()
valid = df[df["booking_status"].isin(VALID_STATUSES)].copy()

confirmed = int(valid["booking_status"].eq("Confirmed").sum())
cancelled = int(valid["booking_status"].eq("Cancelled").sum())
overall_cancel_rate = cancelled / (confirmed + cancelled)

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
]
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
city_high = city.iloc[0]
city_low = city.iloc[-1]
city_gap = city["cancellation_rate"].max() - city["cancellation_rate"].min()
stay_high = stay_type.iloc[0]
stay_low = stay_type.iloc[-1]
stay_type_gap = stay_type["cancellation_rate"].max() - stay_type["cancellation_rate"].min()

revenue_spread = pd.DataFrame(
    {
        "Dimension": ["Booking Channel", "Room Type", "Star Rating"],
        "Spread": [
            booking_channel["avg_net_revenue"].max() - booking_channel["avg_net_revenue"].min(),
            room_type["avg_net_revenue"].max() - room_type["avg_net_revenue"].min(),
            star_rating["avg_net_revenue"].max() - star_rating["avg_net_revenue"].min(),
        ],
    }
)

overall_avg_net_revenue = valid["net_revenue"].mean()
revenue_data = pd.concat(
    [
        booking_channel.assign(Dimension="Booking Channel", Segment=booking_channel["booking_channel"]),
        room_type.assign(Dimension="Room Type", Segment=room_type["room_type"]),
        star_rating.assign(Dimension="Star Rating", Segment=star_rating["star_rating"].astype(str)),
    ],
    ignore_index=True,
)
revenue_data["Revenue Lift"] = revenue_data["avg_net_revenue"] - overall_avg_net_revenue
revenue_data["Revenue Lift %"] = revenue_data["Revenue Lift"] / overall_avg_net_revenue
revenue_data["Direction"] = revenue_data["Revenue Lift"].map(lambda v: "Above Avg" if v >= 0 else "Below Avg")
revenue_leader = revenue_data.sort_values("Revenue Lift", ascending=False).iloc[0]
revenue_lagger = revenue_data.sort_values("Revenue Lift").iloc[0]

st.markdown(
    """
    <style>
    .stApp {
      background: linear-gradient(180deg, #F5F8FB 0%, #EDF4F7 100%);
      color: #111827;
    }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
      display: none;
    }
    .block-container {
      padding-top: 28px;
      padding-bottom: 44px;
      max-width: 1320px;
    }
    h1, h2, h3, p, li, span, div {
      color: #111827;
      letter-spacing: 0;
    }
    .hero {
      background: linear-gradient(135deg, #FFFFFF 0%, #F1F7F8 100%);
      border: 1px solid #D7E2EA;
      border-radius: 8px;
      padding: 28px 30px;
      margin-bottom: 18px;
      box-shadow: 0 14px 34px rgba(18, 48, 71, .09);
    }
    .hero h1 {
      font-size: 38px;
      line-height: 1.12;
      margin: 0 0 8px;
      color: #123047;
    }
    .hero p {
      font-size: 16px;
      color: #4B5563;
      margin: 0;
    }
    .metric-card, .insight-card, .summary-box {
      background: #FFFFFF;
      border: 1px solid #D7E2EA;
      border-radius: 8px;
      box-shadow: 0 10px 26px rgba(18, 48, 71, .07);
    }
    .metric-card {
      padding: 18px 18px 15px;
      min-height: 118px;
    }
    .metric-label, .card-label {
      color: #64748B;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }
    .metric-value {
      color: #0F766E;
      font-size: 32px;
      font-weight: 800;
      margin-top: 8px;
    }
    .metric-note {
      color: #475569;
      font-size: 13px;
      margin-top: 4px;
    }
    .insight-card {
      padding: 18px 18px 16px;
      min-height: 226px;
      border-top: 5px solid #0F766E;
    }
    .insight-card h3 {
      font-size: 20px;
      margin: 6px 0 8px;
    }
    .insight-value {
      font-size: 30px;
      font-weight: 800;
      color: #DC2626;
      margin: 8px 0;
    }
    .impact {
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 6px;
      padding: 10px 12px;
      margin-top: 12px;
      color: #111827;
    }
    .summary-box {
      padding: 16px 18px;
      margin: 10px 0 16px;
      border-left: 5px solid #2563EB;
    }
    div[data-testid="stDataFrame"] {
      border: 1px solid #D7E2EA;
      border-radius: 8px;
      background: #FFFFFF;
    }
    .stTabs [data-baseweb="tab-list"] {
      gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
      background: #FFFFFF;
      border: 1px solid #D7E2EA;
      border-radius: 8px 8px 0 0;
      color: #475569;
    }
    .stTabs [aria-selected="true"] {
      background: #EAF7F5;
      color: #0F766E;
      border-color: #0F766E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Hotel Booking Performance & Cancellation Analysis</h1>
      <p>Executive dashboard for cancellation patterns, revenue behavior, booking-channel risk, and stay-length insights.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    metric_card("Analyzed Bookings", f"{len(valid):,}", "Confirmed + Cancelled")
with kpi2:
    metric_card("Cancellation Rate", pct(overall_cancel_rate), f"{cancelled:,} cancelled bookings")
with kpi3:
    metric_card("Avg Net Revenue", money(valid["net_revenue"].mean()), "Across analyzed bookings")
with kpi4:
    metric_card("Avg Nights", f"{valid['nights'].mean():.2f}", "Average stay length")

st.markdown("## Executive Findings")
c1, c2 = st.columns(2)
with c1:
    insight_card(
        "Lead-time spike near 30 days",
        pct(float(spike["cancellation_rate"])),
        f"The {spike['lead_time_band']} day gap before check-in has {int(spike['cancellations']):,} cancellations.",
        f"{pct(float(spike['cancel_share']))} of all cancellations occur in this window. Booking dates: {spike_booking_window}; check-in dates: {spike_checkin_window}.",
    )
with c2:
    insight_card(
        "Four-night bookings are the highest-risk stay length",
        pct(four_night_rate),
        f"All other stay lengths combined cancel at {pct(other_night_rate)}.",
        "Stay length should be included in cancellation forecasting and retention targeting.",
    )

c3, c4 = st.columns(2)
with c3:
    insight_card(
        "Travel Agent bookings carry the highest channel risk",
        pct(float(channel_high["cancellation_rate"])),
        f"Web bookings are lowest at {pct(float(channel_low['cancellation_rate']))}.",
        "Channel-specific cancellation controls can reduce avoidable lost bookings.",
    )
with c4:
    insight_card(
        "Star rating is not a major cancellation driver",
        "Only 1.6% gap",
        "Cancellation rates are almost the same for 2-star, 3-star, 4-star, and 5-star hotels.",
        "Focus more on lead time, booking channel, and stay length because those show clearer differences.",
    )

st.markdown("## Segment Comparison Tables")
t1, t2, t3 = st.tabs(["Booking Channel", "Room Type", "Star Rating"])
with t1:
    st.dataframe(format_table(booking_channel, "booking_channel"), use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="summary-box"><b>Cancellations from Travel Agent bookings are the highest</b> at <b>{pct(float(channel_high["cancellation_rate"]))}</b>. Web bookings have the lowest cancellation rate at <b>{pct(float(channel_low["cancellation_rate"]))}</b>. Avg net revenue shows no material channel difference.</div>',
        unsafe_allow_html=True,
    )
with t2:
    st.dataframe(format_table(room_type, "room_type"), use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="summary-box">Standard rooms are highest at <b>{pct(float(room_high["cancellation_rate"]))}</b>; Deluxe is lowest at <b>{pct(float(room_low["cancellation_rate"]))}</b>. Avg nights and avg net revenue are broadly stable.</div>',
        unsafe_allow_html=True,
    )
with t3:
    st.dataframe(format_table(star_rating, "star_rating"), use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="summary-box">Star rating has no meaningful cancellation difference. The full spread is only <b>{star_gap * 100:.1f} percentage points</b>.</div>',
        unsafe_allow_html=True,
    )

st.markdown("## Cancellation by Lead-Time Band")
left, right = st.columns([1.35, 1])
with left:
    fig = px.bar(
        lead_table,
        x="lead_time_band",
        y="cancellation_rate",
        text=lead_table["cancellation_rate"].map(lambda v: f"{v * 100:.1f}%"),
        color="cancellation_rate",
        color_continuous_scale=["#DBEAFE", COLORS["teal"], COLORS["red"]],
        title="Cancellation Rate by 5-Day Lead-Time Band",
        labels={"lead_time_band": "Lead-Time Band", "cancellation_rate": "Cancellation Rate"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, yaxis_tickformat=".0%")
    st.plotly_chart(clean_chart(fig, 450), use_container_width=True)
with right:
    lead_display = lead_table.copy()
    lead_display["Cancellation Rate"] = lead_display["cancellation_rate"].map(pct)
    lead_display["Share of Cancellations"] = lead_display["cancel_share"].map(pct)
    lead_display = lead_display.rename(
        columns={
            "lead_time_band": "Lead-Time Band",
            "bookings": "Bookings",
            "cancellations": "Cancellations",
        }
    )
    st.dataframe(
        lead_display[
            ["Lead-Time Band", "Bookings", "Cancellations", "Cancellation Rate", "Share of Cancellations"]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.markdown(
    f'<div class="summary-box">Spike window: <b>{spike["lead_time_band"]} days before check-in</b> | Share of cancellations: <b>{pct(float(spike["cancel_share"]))}</b> | Booking dates: <b>{spike_booking_window}</b> | Check-in dates: <b>{spike_checkin_window}</b></div>',
    unsafe_allow_html=True,
)

st.markdown("## Net Revenue Lift by Segment")
st.markdown(
    f'<div class="summary-box">Overall average net revenue is <b>{money(overall_avg_net_revenue)}</b>. The charts below show whether each segment is above or below that benchmark.</div>',
    unsafe_allow_html=True,
)

revenue_tabs = st.tabs(["Booking Channel", "Room Type", "Star Rating"])
for tab, dimension_name in zip(revenue_tabs, ["Booking Channel", "Room Type", "Star Rating"]):
    with tab:
        dimension_data = revenue_data[revenue_data["Dimension"].eq(dimension_name)].sort_values(
            "Revenue Lift"
        )
        left_col, right_col = st.columns([1.35, 1])
        with left_col:
            fig = px.bar(
                dimension_data,
                y="Segment",
                x="Revenue Lift",
                orientation="h",
                color="Direction",
                text=dimension_data["Revenue Lift"].map(lambda v: f"${v:,.0f}"),
                color_discrete_map={"Above Avg": COLORS["teal"], "Below Avg": COLORS["red"]},
                hover_data={
                    "booking_count": ":,",
                    "avg_net_revenue": ":$,.0f",
                    "Revenue Lift": ":$,.0f",
                    "Revenue Lift %": ":.2%",
                },
                title=f"{dimension_name}: Revenue Lift vs Overall Average",
                labels={"Revenue Lift": "Difference from Overall Avg", "Segment": ""},
            )
            fig.add_vline(
                x=0,
                line_width=2,
                line_color=COLORS["ink"],
                annotation_text="Overall Avg",
                annotation_position="top",
                annotation_font_color=COLORS["ink"],
            )
            fig.update_traces(textposition="outside", cliponaxis=False)
            fig.update_layout(
                xaxis_tickprefix="$",
                xaxis_tickformat=",",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(clean_chart(fig, 340), use_container_width=True)
        with right_col:
            st.dataframe(
                revenue_lift_display(dimension_data),
                use_container_width=True,
                hide_index=True,
            )
            best = dimension_data.sort_values("Revenue Lift", ascending=False).iloc[0]
            lowest = dimension_data.sort_values("Revenue Lift").iloc[0]
            st.markdown(
                f'<div class="summary-box"><b>{best["Segment"]}</b> leads this dimension at <b>${best["Revenue Lift"]:+,.0f}</b> vs average. <b>{lowest["Segment"]}</b> is lowest at <b>${lowest["Revenue Lift"]:+,.0f}</b>.</div>',
                unsafe_allow_html=True,
            )

st.markdown("## Cancellation Rate by Stay Length")
left_nights, right_nights = st.columns([1.25, 1])
with left_nights:
    fig = px.bar(
        nights.sort_values("nights"),
        x="nights",
        y="cancellation_rate",
        text=nights.sort_values("nights")["cancellation_rate"].map(lambda v: f"{v * 100:.1f}%"),
        color="cancellation_rate",
        color_continuous_scale=["#DBEAFE", COLORS["teal"], COLORS["red"]],
        title="Cancellation Rate by Nights",
        labels={"nights": "Nights", "cancellation_rate": "Cancellation Rate"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, yaxis_tickformat=".0%")
    st.plotly_chart(clean_chart(fig, 430), use_container_width=True)
with right_nights:
    st.dataframe(
        nights_display(nights),
        use_container_width=True,
        hide_index=True,
    )
    st.markdown(
        f'<div class="summary-box">Four-night stays are the clear outlier at <b>{pct(four_night_rate)}</b>, while all other stays combined are only <b>{pct(other_night_rate)}</b>.</div>',
        unsafe_allow_html=True,
    )

st.markdown("## Additional Checks")
st.markdown(
    '<div class="summary-box">City and stay type were checked as secondary drivers. Both show only small differences, so they are not the main cancellation drivers in this dataset.</div>',
    unsafe_allow_html=True,
)

city_col, stay_col = st.columns([1.35, 1])
with city_col:
    city_chart = city.sort_values("cancellation_rate")
    fig = px.bar(
        city_chart,
        y="city",
        x="cancellation_rate",
        orientation="h",
        text=city_chart["cancellation_rate"].map(lambda v: f"{v * 100:.1f}%"),
        color="cancellation_rate",
        color_continuous_scale=["#DBEAFE", COLORS["teal"], COLORS["red"]],
        title="City Cancellation Rate Check",
        labels={"city": "City", "cancellation_rate": "Cancellation Rate"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(coloraxis_showscale=False, xaxis_tickformat=".0%")
    st.plotly_chart(clean_chart(fig, 460), use_container_width=True)

with stay_col:
    st.markdown("### Stay Type Check")
    st.dataframe(format_table(stay_type, "stay_type"), use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="summary-box"><b>City:</b> Highest is <b>{city_high["city"]}</b> at <b>{pct(float(city_high["cancellation_rate"]))}</b>; lowest is <b>{city_low["city"]}</b> at <b>{pct(float(city_low["cancellation_rate"]))}</b>. Gap: <b>{city_gap * 100:.1f} percentage points</b>.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="summary-box"><b>Stay type insight:</b> Leisure and Business bookings behave almost the same. {stay_high["stay_type"]} is <b>{pct(float(stay_high["cancellation_rate"]))}</b> and {stay_low["stay_type"]} is <b>{pct(float(stay_low["cancellation_rate"]))}</b>, a gap of only <b>{stay_type_gap * 100:.1f} percentage points</b>.</div>',
        unsafe_allow_html=True,
    )
