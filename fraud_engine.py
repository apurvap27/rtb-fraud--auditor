"""
fraud_engine.py
----------------
Rule-based Invalid Traffic (IVT) / fraud detection engine for the
RTB bidstream. Applies independent, explainable detection rules,
producing a cumulative fraud_score, a boolean detection flag, and
a human-readable reason string per row -- mirroring how real ad
verification platforms (e.g. DoubleVerify, HUMAN) explain flags
rather than returning an opaque black-box result.
"""

import numpy as np
import pandas as pd

import config


def _flag_high_ip_frequency(df):
    """
    Flags rows where the same IP address appears more than
    config.MAX_BIDS_PER_IP_PER_MINUTE times within the same
    calendar minute (a proxy for a rolling-window bid-frequency check).
    """
    minute_bucket = df[config.COL_TIMESTAMP].dt.floor("min")
    group_counts = df.groupby(
        [df[config.COL_IP_ADDRESS], minute_bucket]
    ).transform("size")
    return group_counts > config.MAX_BIDS_PER_IP_PER_MINUTE


def _flag_fast_click(df):
    """Flags clicks that occur faster than humanly plausible."""
    return df[config.COL_CLICK_LATENCY] < config.MIN_CLICK_LATENCY_SECONDS


def _flag_datacenter_ip(df):
    """Flags IPs matching known simulated datacenter/bot prefixes."""
    escaped_prefixes = [p.replace(".", r"\.") for p in config.DATACENTER_IP_PREFIXES]
    pattern = "^(?:" + "|".join(escaped_prefixes) + ")"
    return df[config.COL_IP_ADDRESS].str.contains(pattern, regex=True, na=False)


def _flag_high_risk_geo(df):
    """Flags traffic originating from configured high-risk geographies."""
    return df[config.COL_COUNTRY].isin(config.HIGH_RISK_COUNTRIES)


def apply_fraud_detection(df):
    """
    Master function: takes the raw bidstream DataFrame and returns a
    NEW DataFrame enriched with fraud_score, is_fraud_detected, and
    fraud_reason. Does not mutate the original input DataFrame.
    """
    df = df.copy()

    rule_high_freq = _flag_high_ip_frequency(df)
    rule_fast_click = _flag_fast_click(df)
    rule_datacenter = _flag_datacenter_ip(df)
    rule_high_risk_geo = _flag_high_risk_geo(df)

    # --- Cumulative weighted fraud score ---
    df[config.COL_FRAUD_SCORE] = (
        rule_high_freq.astype(int) * 40
        + rule_fast_click.astype(int) * 35
        + rule_datacenter.astype(int) * 25
        + rule_high_risk_geo.astype(int) * 15
    )

    FRAUD_SCORE_THRESHOLD = 50
    df[config.COL_IS_FRAUD_DETECTED] = df[config.COL_FRAUD_SCORE] >= FRAUD_SCORE_THRESHOLD

    # --- Human-readable explanation per row (transparency/auditability) ---
    flags_df = pd.DataFrame({
        "High bid frequency from single IP": rule_high_freq,
        "Inhuman click latency": rule_fast_click,
        "Datacenter IP signature": rule_datacenter,
        "High-risk geography": rule_high_risk_geo,
    })

    def _row_reason(row):
        active_reasons = [label for label, flagged in row.items() if flagged]
        return "; ".join(active_reasons) if active_reasons else "No anomaly detected"

    df[config.COL_FRAUD_REASON] = flags_df.apply(_row_reason, axis=1)

    return df


if __name__ == "__main__":
    from data_generator import generate_bidstream_data

    raw_data = generate_bidstream_data()
    scored_data = apply_fraud_detection(raw_data)

    print("Shape after scoring:", scored_data.shape)
    print()
    print(scored_data[[
        config.COL_IS_FRAUD_ACTUAL,
        config.COL_IS_FRAUD_DETECTED,
        config.COL_FRAUD_SCORE,
        config.COL_FRAUD_REASON
    ]].head(15))

    # --- Confusion matrix sanity check ---
    actual = scored_data[config.COL_IS_FRAUD_ACTUAL]
    detected = scored_data[config.COL_IS_FRAUD_DETECTED]

    true_positive = int((actual & detected).sum())
    false_negative = int((actual & ~detected).sum())
    false_positive = int((~actual & detected).sum())
    true_negative = int((~actual & ~detected).sum())

    print("\n--- Detection Performance ---")
    print(f"True Positives:  {true_positive}")
    print(f"False Negatives: {false_negative}")
    print(f"False Positives: {false_positive}")
    print(f"True Negatives:  {true_negative}")