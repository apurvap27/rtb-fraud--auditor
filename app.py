"""
app.py
------
Main Streamlit entry point for the Digital Advertising RTB & Ad Fraud
Detection Auditor.
"""

import textwrap

import streamlit as st
import pandas as pd
import plotly.express as px

import config
from data_generator import generate_bidstream_data
from fraud_engine import apply_fraud_detection
import utils


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN SYSTEM -- semantic accent colors per KPI category (used consistently,
# never randomly, so color always carries the same meaning across the app)
# =============================================================================
ACCENTS = {
    "blue":   {"icon_bg": "#EEF4FF", "icon_fg": "#3538CD", "top": "#3538CD"},
    "teal":   {"icon_bg": "#E9FBF6", "icon_fg": "#0F9D6B", "top": "#0F9D6B"},
    "purple": {"icon_bg": "#F5F0FF", "icon_fg": "#7A5AF8", "top": "#7A5AF8"},
    "amber":  {"icon_bg": "#FFF7E6", "icon_fg": "#B45309", "top": "#F59E0B"},
    "danger": {"icon_bg": "#FEE4E2", "icon_fg": config.COLOR_FRAUD, "top": config.COLOR_FRAUD},
    "navy":   {"icon_bg": "#EEF2FF", "icon_fg": config.COLOR_PRIMARY, "top": config.COLOR_PRIMARY},
}

# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stAppViewContainer"] {{
        background: radial-gradient(circle at top left, #F3F6FC 0%, #EEF1F6 45%, #EAEDF3 100%);
    }}

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {config.COLOR_PRIMARY} 0%, #0C2E4E 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {{
        color: #FFFFFF !important;
    }}
    [data-testid="stSidebar"] label {{
        color: #CBD5E1 !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] > div > div,
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-testid="stDateInput"] input {{
        background-color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 8px !important;
        color: #101828 !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: #101828 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSelectbox"] svg,
    [data-testid="stSidebar"] [data-testid="stMultiSelect"] svg,
    [data-testid="stSidebar"] [data-testid="stDateInput"] svg,
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        fill: #667085 !important;
    }}
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
        background: linear-gradient(135deg, {config.COLOR_ACCENT} 0%, #00A88F 100%) !important;
        border-radius: 6px !important;
    }}
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span,
    [data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] svg {{
        color: #06251F !important;
        fill: #06251F !important;
        font-weight: 800 !important;
    }}
    [data-baseweb="popover"] li {{
        color: #101828 !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.10) !important;
    }}

    /* Sidebar-only: neutralize the bordered-container styling so it never
       paints a white card behind sidebar widgets */
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* ---------- TOP STATUS STRIP ---------- */
    .status-strip {{
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 14px;
        font-size: 12.5px;
        font-weight: 700;
        color: #475467;
        letter-spacing: 0.3px;
    }}
    .pulse-dot {{
        width: 8px; height: 8px; border-radius: 50%;
        background: {config.COLOR_ACCENT};
        box-shadow: 0 0 0 0 rgba(0,194,168,0.6);
        animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(0,194,168,0.55); }}
        70% {{ box-shadow: 0 0 0 8px rgba(0,194,168,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(0,194,168,0); }}
    }}

    /* ---------- HEADER BANNER ---------- */
    .app-header {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, {config.COLOR_PRIMARY} 0%, #0D3B66 55%, #0E6BA8 120%);
        padding: 34px 38px;
        border-radius: 18px;
        margin-bottom: 26px;
        box-shadow: 0 16px 40px rgba(10,37,64,0.35);
    }}
    .app-header::after {{
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 220px; height: 220px;
        background: radial-gradient(circle, rgba(0,194,168,0.35) 0%, rgba(0,194,168,0) 70%);
        border-radius: 50%;
    }}
    .app-header h1 {{
        color: #FFFFFF !important;
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.4px;
        position: relative; z-index: 1;
    }}
    .app-header p {{
        color: rgba(255,255,255,0.80);
        margin: 8px 0 0 0;
        font-size: 14.5px;
        position: relative; z-index: 1;
    }}
    .header-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.25);
        color: #FFFFFF; font-size: 11.5px; font-weight: 700;
        padding: 5px 12px; border-radius: 20px;
        margin-top: 14px; position: relative; z-index: 1;
        letter-spacing: 0.4px;
    }}

    /* ---------- KPI CARDS ---------- */
                .kpi-card {{
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px 20px 18px 20px;
        box-shadow: 0 10px 26px rgba(16,24,40,0.09), 0 2px 6px rgba(16,24,40,0.05);
        border: 2px solid #98A2B3;
        height: 100%;
        min-height: 168px;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}
    }}
    .kpi-card::before {{
        content: "";
        position: absolute; top: 0; left: 0; right: 0;
        height: 4px;
        background: var(--kpi-top-color);
    }}
    .kpi-icon {{
        width: 38px; height: 38px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 17px;
        background: var(--kpi-icon-bg);
    }}
        .kpi-label {{
        font-size: 13px; font-weight: 800; color: #344054;
        text-transform: uppercase; letter-spacing: 0.6px;
    }}
    .kpi-value {{
        font-size: 28px; font-weight: 900; color: #101828;
        line-height: 1.1; margin-top: 16px; letter-spacing: -0.6px;
    }}
    .kpi-sub {{
        font-size: 12px; color: #667085; margin-top: 7px; font-weight: 600;
    }}
    .kpi-sub.is-danger {{ color: {config.COLOR_FRAUD}; }}

    /* ---------- SECTION HEADERS ---------- */
    .section-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 8px 0 16px 0;
    }}
    .section-header .left {{
        display: flex; align-items: center; gap: 10px;
    }}
    .section-header .bar {{
        width: 6px; height: 26px;
        background: linear-gradient(180deg, {config.COLOR_ACCENT} 0%, #00A88F 100%);
        border-radius: 3px;
    }}
    .section-header .text {{
        font-size: 20px; font-weight: 800; color: {config.COLOR_PRIMARY};
        letter-spacing: -0.2px;
    }}
    .section-header .tag {{
        font-size: 11px; font-weight: 700; color: #667085;
        background: #F2F4F7; padding: 4px 10px; border-radius: 20px;
    }}

        /* ---------- CHART / TABLE CARD SHELLS (main content only) ---------- */
        [data-testid="stMain"] [data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 16px !important;
        border: 2px solid #98A2B3 !important;
        box-shadow: 0 10px 28px rgba(16,24,40,0.08) !important;
        background: #FFFFFF !important;
    }}

    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# CHART FONT DEFAULTS
# =============================================================================
CHART_FONT = dict(family="Inter", size=13, color="#1D2939")
PLOTLY_CONFIG = {"displayModeBar": False}


def wrap_label(text, width=20):
    return "<br>".join(textwrap.wrap(text, width=width))


# =============================================================================
# REUSABLE HTML COMPONENTS
# =============================================================================
def render_kpi_card(icon, label, value, sub=None, accent="navy"):
    a = ACCENTS[accent]
    sub_class = "kpi-sub is-danger" if accent == "danger" else "kpi-sub"
    sub_html = f'<div class="{sub_class}">{sub}</div>' if sub else ""
    style_vars = f'style="--kpi-top-color:{a["top"]}; --kpi-icon-bg:{a["icon_bg"]};"'
    card_html = (
        f'<div class="kpi-card" {style_vars}>'
        '<div style="display:flex; align-items:center; gap:10px;">'
        f'<div class="kpi-icon" style="color:{a["icon_fg"]};">{icon}</div>'
        f'<div class="kpi-label">{label}</div>'
        '</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}'
        '</div>'
    )
    return card_html


def section_header(icon, text, tag=None):
    tag_html = f'<div class="tag">{tag}</div>' if tag else ""
    header_html = (
        '<div class="section-header">'
        '<div class="left">'
        '<div class="bar"></div>'
        f'<div class="text">{icon} {text}</div>'
        '</div>'
        f'{tag_html}'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data
def load_data():
    raw_df = generate_bidstream_data()
    scored_df = apply_fraud_detection(raw_df)
    return scored_df


df = load_data()


# =============================================================================
# SIDEBAR -- BRANDING + FILTERS
# =============================================================================
sidebar_brand_html = (
    '<div style="text-align:center; padding: 12px 0 22px 0;">'
    '<div style="font-size: 38px;">📡</div>'
    '<div style="font-size: 17px; font-weight: 800; letter-spacing: 1px; color:#FFFFFF; margin-top:6px;">RTB AUDITOR</div>'
    '<div style="font-size: 10.5px; opacity: 0.6; letter-spacing: 1.5px; color:#FFFFFF; margin-top:2px;">FRAUD DETECTION CONSOLE</div>'
    '</div>'
    '<hr style="margin-bottom: 22px;">'
)
st.sidebar.markdown(sidebar_brand_html, unsafe_allow_html=True)

st.sidebar.markdown(
    '<div style="font-size:13px; font-weight:800; color:#FFFFFF; letter-spacing:0.5px; margin-bottom:14px;">🎛️ FILTERS</div>',
    unsafe_allow_html=True,
)

min_date = df[config.COL_TIMESTAMP].min().date()
max_date = df[config.COL_TIMESTAMP].max().date()

date_range = st.sidebar.date_input(
    "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date,
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

selected_advertisers = st.sidebar.multiselect(
    "Advertiser", options=sorted(df[config.COL_ADVERTISER].unique()),
    default=[], placeholder="All advertisers",
)
selected_countries = st.sidebar.multiselect(
    "Geography", options=sorted(df[config.COL_COUNTRY].unique()),
    default=[], placeholder="All countries",
)
selected_devices = st.sidebar.multiselect(
    "Device Type", options=sorted(df[config.COL_DEVICE].unique()),
    default=[], placeholder="All devices",
)
fraud_only = st.sidebar.checkbox("Show only fraud-flagged bids", value=False)


def apply_filters(data):
    filtered = data[
        (data[config.COL_TIMESTAMP].dt.date >= start_date)
        & (data[config.COL_TIMESTAMP].dt.date <= end_date)
    ]
    if selected_advertisers:
        filtered = filtered[filtered[config.COL_ADVERTISER].isin(selected_advertisers)]
    if selected_countries:
        filtered = filtered[filtered[config.COL_COUNTRY].isin(selected_countries)]
    if selected_devices:
        filtered = filtered[filtered[config.COL_DEVICE].isin(selected_devices)]
    if fraud_only:
        filtered = filtered[filtered[config.COL_IS_FRAUD_DETECTED]]
    return filtered


filtered_df = apply_filters(df)

st.sidebar.markdown("---")
records_box_html = (
    '<div style="background: linear-gradient(135deg, rgba(0,194,168,0.15) 0%, rgba(255,255,255,0.05) 100%);'
    ' border: 1px solid rgba(0,194,168,0.25); border-radius: 12px; padding: 14px; text-align:center;">'
    '<div style="font-size: 11px; opacity: 0.7; color:#FFFFFF; letter-spacing:0.5px; font-weight:700;">RECORDS IN VIEW</div>'
    f'<div style="font-size: 30px; font-weight: 900; color: {config.COLOR_ACCENT}; margin-top:4px;">{utils.format_count(len(filtered_df))}</div>'
    f'<div style="font-size: 11px; opacity: 0.55; color:#FFFFFF; margin-top:2px;">of {utils.format_count(len(df))} total</div>'
    '</div>'
)
st.sidebar.markdown(records_box_html, unsafe_allow_html=True)


# =============================================================================
# MAIN -- STATUS STRIP + HEADER BANNER
# =============================================================================
st.markdown(
    '<div class="status-strip"><div class="pulse-dot"></div>LIVE SIMULATION &nbsp;•&nbsp; '
    f'DATA WINDOW: {config.DATE_RANGE_DAYS} DAYS &nbsp;•&nbsp; SEED-REPRODUCIBLE DATASET</div>',
    unsafe_allow_html=True,
)

header_html = (
    '<div class="app-header">'
    f'<h1>{config.APP_ICON} {config.APP_TITLE}</h1>'
    '<p>Real-time bidstream monitoring &amp; rule-based Invalid Traffic (IVT) detection across your programmatic supply chain.</p>'
    '<div class="header-badge">🛡️ 4 Detection Rules Active</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No records match the current filters. Adjust filters in the sidebar.")
    st.stop()


# =============================================================================
# KPI ROW 1 -- Business Metrics
# =============================================================================
kpis = utils.calculate_kpis(filtered_df)
cm = utils.calculate_confusion_matrix(filtered_df)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(render_kpi_card("📊", "Total Bid Requests", utils.format_count(kpis["total_bids"]), accent="blue"),
                unsafe_allow_html=True)
with c2:
    st.markdown(render_kpi_card("💰", "Total Spend", utils.format_currency(kpis["total_spend"]), accent="teal"),
                unsafe_allow_html=True)
with c3:
    st.markdown(render_kpi_card("🏆", "Win Rate", utils.format_percent(kpis["win_rate"]), accent="purple"),
                unsafe_allow_html=True)
with c4:
    st.markdown(render_kpi_card("🚨", "Fraud Detected", utils.format_percent(kpis["fraud_detected_rate"]),
                                 sub=f"{utils.format_count(kpis['fraud_detected_count'])} bids flagged",
                                 accent="danger"), unsafe_allow_html=True)
with c5:
    st.markdown(render_kpi_card("🕳️", "Wasted Spend", utils.format_currency(kpis["wasted_spend"]),
                                 sub="Spent on fraudulent wins", accent="danger"), unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# =============================================================================
# KPI ROW 2 -- Detection Model Performance
# =============================================================================
d1, d2, d3 = st.columns(3)
with d1:
    st.markdown(render_kpi_card("🎯", "Detection Precision", f"{cm['precision']*100:.1f}%",
                                 sub="Of flagged bids, % truly fraudulent", accent="navy"), unsafe_allow_html=True)
with d2:
    st.markdown(render_kpi_card("🔍", "Detection Recall", f"{cm['recall']*100:.1f}%",
                                 sub="Of actual fraud, % successfully caught", accent="navy"), unsafe_allow_html=True)
with d3:
    st.markdown(render_kpi_card("⚖️", "F1 Score", f"{cm['f1_score']*100:.1f}%",
                                 sub="Balance of precision & recall", accent="navy"), unsafe_allow_html=True)

st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)


# =============================================================================
# RECENT BIDSTREAM TABLE
# =============================================================================
display_cols = [
    config.COL_TIMESTAMP, config.COL_BID_ID, config.COL_ADVERTISER,
    config.COL_PUBLISHER, config.COL_COUNTRY, config.COL_BID_PRICE,
    config.COL_WIN_PRICE, config.COL_FRAUD_SCORE, config.COL_IS_FRAUD_DETECTED,
]
preview_df = filtered_df.sort_values(config.COL_TIMESTAMP, ascending=False)[display_cols].head(50).copy()

table_tag = f"Showing {len(preview_df)} of {utils.format_count(len(filtered_df))} filtered rows"
section_header("📋", "Recent Bidstream Activity", tag=table_tag)
preview_df = filtered_df.sort_values(config.COL_TIMESTAMP, ascending=False)[display_cols].head(50).copy()
preview_df[config.COL_IS_FRAUD_DETECTED] = preview_df[config.COL_IS_FRAUD_DETECTED].map(
    {True: "🔴 Fraud", False: "🟢 Clean"}
)

with st.container(border=True):
            st.dataframe(
        preview_df,
        use_container_width=True,
        height=460,
        hide_index=True,
        column_config={
            config.COL_TIMESTAMP: st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
            config.COL_BID_ID: st.column_config.TextColumn("Bid ID"),
            config.COL_ADVERTISER: st.column_config.TextColumn("Advertiser"),
            config.COL_PUBLISHER: st.column_config.TextColumn("Publisher"),
            config.COL_COUNTRY: st.column_config.TextColumn("Country"),
            config.COL_BID_PRICE: st.column_config.NumberColumn("Bid Price", format="$%.2f"),
            config.COL_WIN_PRICE: st.column_config.NumberColumn("Win Price", format="$%.2f"),
            config.COL_FRAUD_SCORE: st.column_config.ProgressColumn("Fraud Score", min_value=0, max_value=100, format="%d"),
            config.COL_IS_FRAUD_DETECTED: st.column_config.TextColumn("Status"),
        },
    )

st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)


# =============================================================================
# CHARTS -- TREND OVER TIME
# =============================================================================
section_header("📈", "Bid Volume & Fraud Trend", tag=f"{config.DATE_RANGE_DAYS}-day window")

trend_df = filtered_df.copy()
trend_df["date"] = trend_df[config.COL_TIMESTAMP].dt.date

daily_summary = trend_df.groupby("date").agg(
    total_bids=(config.COL_BID_ID, "count"),
    fraud_bids=(config.COL_IS_FRAUD_DETECTED, "sum"),
).reset_index()

peak_fraud_day = daily_summary.loc[daily_summary["fraud_bids"].idxmax()]

fig_trend = px.area(daily_summary, x="date", y="total_bids", labels={"total_bids": "Bid Count", "date": ""})
fig_trend.update_traces(
    line_color=config.COLOR_PRIMARY, line_width=3, line_shape="spline",
    fillcolor="rgba(10,37,64,0.10)", name="Total Bids", showlegend=True,
)
fig_trend.add_scatter(
    x=daily_summary["date"], y=daily_summary["fraud_bids"], mode="lines", name="Fraud Detected",
    line=dict(color=config.COLOR_FRAUD, width=3, shape="spline"),
)
fig_trend.add_annotation(
    x=peak_fraud_day["date"], y=peak_fraud_day["fraud_bids"],
    text=f"<b>Peak · {int(peak_fraud_day['fraud_bids'])} fraud bids</b>",
    showarrow=True, arrowhead=2, arrowcolor=config.COLOR_FRAUD, arrowwidth=2,
    ax=0, ay=-42, font=dict(size=12, color="#FFFFFF", family="Inter"),
    bgcolor=config.COLOR_FRAUD, bordercolor=config.COLOR_FRAUD, borderwidth=1, borderpad=6,
)
fig_trend.update_layout(
    plot_bgcolor="white", paper_bgcolor="white", font=CHART_FONT,
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, title="",
                font=dict(size=13, color="#1D2939")),
    margin=dict(l=10, r=10, t=45, b=10), height=380,
)
fig_trend.update_xaxes(showgrid=False, tickfont=dict(size=12, color="#344054"))
fig_trend.update_yaxes(showgrid=True, gridcolor="#F1F4F9", tickfont=dict(size=12, color="#344054"))

with st.container(border=True):
    st.plotly_chart(fig_trend, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)


# =============================================================================
# CHARTS -- GEOGRAPHY + TOP PUBLISHERS
# =============================================================================
col_geo, col_pub = st.columns(2)

with col_geo:
    section_header("🌍", "Fraud Rate by Geography")

    geo_summary = filtered_df.groupby(config.COL_COUNTRY).agg(
        total_bids=(config.COL_BID_ID, "count"),
        fraud_bids=(config.COL_IS_FRAUD_DETECTED, "sum"),
    ).reset_index()
    geo_summary["fraud_rate"] = (geo_summary["fraud_bids"] / geo_summary["total_bids"]) * 100
    geo_summary = geo_summary.sort_values("fraud_rate", ascending=True)
    geo_summary["label"] = geo_summary["fraud_rate"].map(lambda v: f"{v:.1f}%")

    fig_geo = px.bar(
        geo_summary, x="fraud_rate", y=config.COL_COUNTRY, orientation="h",
        labels={"fraud_rate": "Fraud Rate (%)", config.COL_COUNTRY: ""},
        color="fraud_rate", color_continuous_scale=[config.COLOR_ACCENT, "#F59E0B", config.COLOR_FRAUD],
        text="label",
    )
    fig_geo.update_traces(textposition="outside", cliponaxis=False,
                           textfont=dict(size=12, color="#101828", family="Inter"),
                           marker_line_width=0)
    fig_geo.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font=CHART_FONT,
        coloraxis_showscale=False, margin=dict(l=10, r=40, t=10, b=10), height=420, bargap=0.35,
    )
    fig_geo.update_xaxes(showgrid=True, gridcolor="#F1F4F9", tickfont=dict(size=12, color="#344054"))
    fig_geo.update_yaxes(showgrid=False, tickfont=dict(size=13, color="#101828"))

    with st.container(border=True):
        st.plotly_chart(fig_geo, use_container_width=True, config=PLOTLY_CONFIG)

with col_pub:
    section_header("🏢", "Top 5 Publishers by Fraud")

    top_publishers = utils.top_n_by_fraud(filtered_df, config.COL_PUBLISHER, n=5)
    top_publishers = top_publishers.sort_values("fraud_count", ascending=True)

    fig_pub = px.bar(
        top_publishers, x="fraud_count", y=config.COL_PUBLISHER, orientation="h",
        labels={"fraud_count": "Detected Fraud Count", config.COL_PUBLISHER: ""},
        text="fraud_count",
        range_x=[0, top_publishers["fraud_count"].max() * 1.3],
    )
    fig_pub.update_traces(marker_color=config.COLOR_PRIMARY, textposition="outside", cliponaxis=False,
                           textfont=dict(size=12, color="#101828", family="Inter"), marker_line_width=0)
    fig_pub.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font=CHART_FONT,
        margin=dict(l=10, r=40, t=10, b=10), height=420, bargap=0.35,
    )
    fig_pub.update_xaxes(showgrid=True, gridcolor="#F1F4F9", tickfont=dict(size=12, color="#344054"))
    fig_pub.update_yaxes(showgrid=False, tickfont=dict(size=13, color="#101828"))

    with st.container(border=True):
        st.plotly_chart(fig_pub, use_container_width=True, config=PLOTLY_CONFIG)

st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)


# =============================================================================
# CHARTS -- DEVICE TYPE + FRAUD TYPOLOGY BREAKDOWN
# =============================================================================
col_device, col_reason = st.columns(2)

with col_device:
    section_header("📱", "Traffic Mix by Device Type")

    device_summary = filtered_df[config.COL_DEVICE].value_counts().reset_index()
    device_summary.columns = [config.COL_DEVICE, "count"]

    fig_device = px.pie(
        device_summary, names=config.COL_DEVICE, values="count", hole=0.62,
        color_discrete_sequence=[config.COLOR_PRIMARY, config.COLOR_ACCENT, "#7A5AF8", "#F59E0B"],
    )
    fig_device.update_traces(textposition="outside", textinfo="percent+label",
                              textfont=dict(size=13, color="#101828", family="Inter"),
                              marker=dict(line=dict(color="#FFFFFF", width=3)))
    fig_device.update_layout(
        font=CHART_FONT, showlegend=False, margin=dict(l=30, r=30, t=20, b=20), height=400,
        annotations=[dict(
            text=f"<b>{utils.format_count(len(filtered_df))}</b><br><span style='font-size:12px;color:#667085;'>Total Bids</span>",
            x=0.5, y=0.5, font_size=18, showarrow=False,
            font=dict(family="Inter", color=config.COLOR_PRIMARY),
        )],
    )

    with st.container(border=True):
        st.plotly_chart(fig_device, use_container_width=True, config=PLOTLY_CONFIG)

with col_reason:
    section_header("🧭", "Fraud by Rule Triggered")

    fraud_only_df = filtered_df[filtered_df[config.COL_IS_FRAUD_DETECTED]]

    rule_labels = [
        "High bid frequency from single IP",
        "Inhuman click latency",
        "Datacenter IP signature",
        "High-risk geography",
    ]
    rule_counts = [
        int(fraud_only_df[config.COL_FRAUD_REASON].str.contains(lbl, regex=False).sum())
        for lbl in rule_labels
    ]
    reason_summary = pd.DataFrame({"reason": rule_labels, "count": rule_counts})
    reason_summary = reason_summary.sort_values("count", ascending=True)
    reason_summary["wrapped_reason"] = reason_summary["reason"].apply(lambda t: wrap_label(t, width=20))

    max_count = reason_summary["count"].max()
    fig_reason = px.bar(
        reason_summary, x="count", y="wrapped_reason", orientation="h",
        labels={"count": "Bids Flagged", "wrapped_reason": ""},
        text="count",
        range_x=[0, max_count * 1.3 if max_count > 0 else 1],
    )
    fig_reason.update_traces(marker_color=config.COLOR_FRAUD, textposition="outside", cliponaxis=False,
                              textfont=dict(size=12, color="#101828", family="Inter"), marker_line_width=0)
    fig_reason.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", font=CHART_FONT,
        margin=dict(l=190, r=40, t=20, b=10), height=400, bargap=0.4,
    )
    fig_reason.update_xaxes(showgrid=True, gridcolor="#F1F4F9", tickfont=dict(size=12, color="#344054"))
    fig_reason.update_yaxes(showgrid=False, tickfont=dict(size=12, color="#101828"))

    with st.container(border=True):
        st.plotly_chart(fig_reason, use_container_width=True, config=PLOTLY_CONFIG)