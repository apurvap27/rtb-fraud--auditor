"""
utils.py
--------
Shared helper functions for KPI calculations and formatting used
throughout the dashboard. Centralizing these ensures every metric
displayed in app.py is calculated exactly once, the same way,
everywhere it appears.
"""

import pandas as pd
import config


def format_currency(value):
    """Formats a number as USD currency, e.g. 1234.5 -> '$1,234.50'."""
    return f"${value:,.2f}"


def format_percent(value, decimals=1):
    """Formats a 0-1 float as a percentage string, e.g. 0.073 -> '7.3%'."""
    return f"{value * 100:.{decimals}f}%"


def format_count(value):
    """Formats an integer count with thousands separators, e.g. 15000 -> '15,000'."""
    return f"{value:,.0f}"


def calculate_kpis(df):
    """
    Calculates the core top-line KPIs for the dashboard header.
    Expects the fraud-scored DataFrame (output of apply_fraud_detection).
    Returns a dictionary of raw numeric values -- formatting happens
    separately in app.py using the functions above, keeping this
    function's output reusable and unit-testable.
    """
    total_bids = len(df)
    total_spend = df[config.COL_WIN_PRICE].where(df[config.COL_IS_WIN]).sum()
    win_rate = df[config.COL_IS_WIN].mean()
    avg_bid_price = df[config.COL_BID_PRICE].mean()

    fraud_detected_count = int(df[config.COL_IS_FRAUD_DETECTED].sum())
    fraud_detected_rate = df[config.COL_IS_FRAUD_DETECTED].mean()

    # Estimated wasted spend: winning bids that were flagged as fraud
    wasted_spend = df.loc[
        df[config.COL_IS_WIN] & df[config.COL_IS_FRAUD_DETECTED],
        config.COL_WIN_PRICE
    ].sum()

    return {
        "total_bids": total_bids,
        "total_spend": total_spend,
        "win_rate": win_rate,
        "avg_bid_price": avg_bid_price,
        "fraud_detected_count": fraud_detected_count,
        "fraud_detected_rate": fraud_detected_rate,
        "wasted_spend": wasted_spend,
    }


def calculate_confusion_matrix(df):
    """
    Compares detected fraud against ground-truth actual fraud.
    Returns counts plus derived precision/recall/F1 metrics.
    Guards against division by zero if a category is ever empty.
    """
    actual = df[config.COL_IS_FRAUD_ACTUAL]
    detected = df[config.COL_IS_FRAUD_DETECTED]

    true_positive = int((actual & detected).sum())
    false_negative = int((actual & ~detected).sum())
    false_positive = int((~actual & detected).sum())
    true_negative = int((~actual & ~detected).sum())

    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive) > 0 else 0.0
    )
    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative) > 0 else 0.0
    )
    f1_score = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )

    return {
        "true_positive": true_positive,
        "false_negative": false_negative,
        "false_positive": false_positive,
        "true_negative": true_negative,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
    }


def top_n_by_fraud(df, group_col, n=5):
    """
    Returns the top-N values of a given categorical column (e.g. publisher,
    advertiser, geo_country) ranked by number of detected fraud events.
    Used for 'Top Fraud Sources' style tables/charts in the dashboard.
    """
    result = (
        df[df[config.COL_IS_FRAUD_DETECTED]]
        .groupby(group_col)
        .size()
        .sort_values(ascending=False)
        .head(n)
        .reset_index(name="fraud_count")
    )
    return result


if __name__ == "__main__":
    from data_generator import generate_bidstream_data
    from fraud_engine import apply_fraud_detection

    raw = generate_bidstream_data()
    scored = apply_fraud_detection(raw)

    kpis = calculate_kpis(scored)
    print("--- KPIs ---")
    for key, value in kpis.items():
        print(f"{key}: {value}")

    cm = calculate_confusion_matrix(scored)
    print("\n--- Confusion Matrix & Metrics ---")
    for key, value in cm.items():
        print(f"{key}: {value}")

    print("\n--- Top 5 Publishers by Detected Fraud ---")
    print(top_n_by_fraud(scored, config.COL_PUBLISHER, n=5))

    print("\n--- Formatting examples ---")
    print(format_currency(kpis["total_spend"]))
    print(format_percent(kpis["fraud_detected_rate"]))
    print(format_count(kpis["total_bids"]))