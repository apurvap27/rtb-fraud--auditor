"""
data_generator.py
------------------
Generates a synthetic, reproducible RTB (Real-Time Bidding) bidstream
dataset for the Ad Fraud Detection Auditor. Fraud is injected using
three distinct, realistic typologies rather than random noise, so the
fraud_engine.py has genuine, explainable patterns to detect.
All values are simulated for portfolio/demo purposes only.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

import config


def _generate_timestamps(n, days_back, rng):
    """Generate n random timestamps spread across the last `days_back` days."""
    now = datetime.now()
    start = now - timedelta(days=days_back)
    total_seconds = int((now - start).total_seconds())
    random_offsets = rng.integers(0, total_seconds, size=n)
    return [start + timedelta(seconds=int(offset)) for offset in random_offsets]


def _generate_ip_addresses(n, rng, datacenter_prob=0.02):
    """
    Generate a pool of unique-looking IPs, then sample from that pool.
    A smaller pool relative to n creates natural IP reuse. datacenter_prob
    controls how often a simulated cloud/bot-style prefix is injected into
    otherwise ordinary traffic (kept low to avoid noisy false positives).
    """
    num_unique_ips = 1200
    pool = []
    for _ in range(num_unique_ips):
        octet_2 = rng.integers(0, 255)
        octet_3 = rng.integers(0, 255)
        octet_4 = rng.integers(1, 254)
        if rng.random() < datacenter_prob:
            prefix = rng.choice(config.DATACENTER_IP_PREFIXES)
            ip = f"{prefix}{octet_3}.{octet_4}"
        else:
            ip = f"192.{octet_2}.{octet_3}.{octet_4}"
        pool.append(ip)
    return rng.choice(pool, size=n)


def generate_bidstream_data():
    """
    Master function: builds the full synthetic RTB bidstream DataFrame,
    including three realistic, named fraud typologies.
    """
    rng = np.random.default_rng(config.RANDOM_SEED)
    n = config.NUM_RECORDS
    now = datetime.now()
    range_start = now - timedelta(days=config.DATE_RANGE_DAYS)

    df = pd.DataFrame({
        config.COL_BID_ID: [f"BID-{100000 + i}" for i in range(n)],
        config.COL_TIMESTAMP: _generate_timestamps(n, config.DATE_RANGE_DAYS, rng),
        config.COL_ADVERTISER: rng.choice(config.ADVERTISERS, size=n),
        config.COL_PUBLISHER: rng.choice(config.PUBLISHERS, size=n),
        config.COL_DEVICE: rng.choice(config.DEVICE_TYPES, size=n, p=[0.55, 0.30, 0.10, 0.05]),
        config.COL_BROWSER: rng.choice(config.BROWSERS, size=n),
        config.COL_COUNTRY: rng.choice(config.GEO_COUNTRIES, size=n),
        config.COL_AD_FORMAT: rng.choice(config.AD_FORMATS, size=n, p=[0.40, 0.35, 0.20, 0.05]),
        config.COL_EXCHANGE: rng.choice(config.EXCHANGES, size=n),
        config.COL_IP_ADDRESS: _generate_ip_addresses(n, rng, datacenter_prob=0.02),
    })

    # --- Bid economics ---
    df[config.COL_BID_PRICE] = np.round(rng.lognormal(mean=1.1, sigma=0.6, size=n), 2)
    df[config.COL_BID_PRICE] = df[config.COL_BID_PRICE].clip(0.10, 45.00)

    win_ratio = rng.uniform(0.55, 0.98, size=n)
    df[config.COL_WIN_PRICE] = np.round(df[config.COL_BID_PRICE] * win_ratio, 2)
    df[config.COL_IS_WIN] = rng.random(n) < 0.62

    # Baseline click latency for LEGITIMATE traffic only.
    # Shifted by MIN_CLICK_LATENCY_SECONDS so it can never accidentally
    # dip into "inhuman" territory -- guarantees a clean signal boundary.
    df[config.COL_CLICK_LATENCY] = np.round(
        config.MIN_CLICK_LATENCY_SECONDS + rng.exponential(scale=4.0, size=n), 2
    )

    # =========================================================================
    # FRAUD INJECTION -- three distinct, realistic typologies
    # =========================================================================
    df[config.COL_IS_FRAUD_ACTUAL] = False

    total_fraud = int(round(n * 0.07))
    fraud_indices = rng.choice(df.index.to_numpy(), size=total_fraud, replace=False)
    df.loc[fraud_indices, config.COL_IS_FRAUD_ACTUAL] = True

    shuffled = fraud_indices.copy()
    rng.shuffle(shuffled)

    n_flooding = int(total_fraud * 0.48)
    n_click_farm = int(total_fraud * 0.43)

    flooding_idx = shuffled[:n_flooding]
    click_farm_idx = shuffled[n_flooding:n_flooding + n_click_farm]
    # remaining ~9% -> "evasive" fraud: intentionally left unmodified,
    # simulating sophisticated fraud that slips past rule-based detection.

    # --- Type A: Bid Flooding Bots ---
    # Clustered into short timestamp bursts from a small set of datacenter
    # IPs -- simulating automated scripts hammering the exchange in seconds.
    num_bot_ips = 25
    bot_ip_groups = np.array_split(flooding_idx, num_bot_ips)
    total_seconds_range = int((now - range_start).total_seconds())

    for group in bot_ip_groups:
        if len(group) == 0:
            continue
        burst_prefix = rng.choice(config.DATACENTER_IP_PREFIXES)
        burst_ip = f"{burst_prefix}{rng.integers(0, 255)}.{rng.integers(1, 254)}"
        burst_offset = int(rng.integers(0, total_seconds_range))
        burst_minute = (range_start + timedelta(seconds=burst_offset)).replace(
            second=0, microsecond=0
        )
        offsets = rng.uniform(0, 50, size=len(group))  # stays within one minute bucket
        df.loc[group, config.COL_IP_ADDRESS] = burst_ip
        df.loc[group, config.COL_TIMESTAMP] = [
            burst_minute + timedelta(seconds=float(o)) for o in offsets
        ]

    # --- Type B: Click Farms ---
    # Ultra-fast, inhuman click latency, concentrated in a configured
    # high-risk geography.
    df.loc[click_farm_idx, config.COL_CLICK_LATENCY] = np.round(
        rng.uniform(0.05, 0.9, size=len(click_farm_idx)), 2
    )
    df.loc[click_farm_idx, config.COL_COUNTRY] = rng.choice(
        config.HIGH_RISK_COUNTRIES, size=len(click_farm_idx)
    )

    # Sort chronologically -- bidstream logs are naturally time-ordered
    df = df.sort_values(by=config.COL_TIMESTAMP).reset_index(drop=True)

    return df


if __name__ == "__main__":
    data = generate_bidstream_data()
    print(data.shape)
    print(data.head(10))
    print(data.dtypes)
    print("\nActual fraud count:", data[config.COL_IS_FRAUD_ACTUAL].sum())