"""
config.py
---------
Centralized configuration for the RTB & Ad Fraud Detection Auditor.
All constants, schemas, thresholds, and styling live here.
No other file should hardcode values that belong in this file.
"""

# =============================================================================
# APP METADATA
# =============================================================================
APP_TITLE = "Digital Advertising RTB & Ad Fraud Detection Auditor"
APP_ICON = "📡"
APP_LAYOUT = "wide"

# =============================================================================
# DATA GENERATION SETTINGS
# =============================================================================
RANDOM_SEED = 42  # fixes randomness so data looks the same every time we run the app
NUM_RECORDS = 15000  # total number of simulated bidstream events

# Date range for simulated bidstream events
DATE_RANGE_DAYS = 30

# =============================================================================
# BUSINESS DIMENSION VALUES
# (These are the categorical "universes" our fake data will sample from)
# =============================================================================
ADVERTISERS = [
    "Nike Global", "Samsung Electronics", "Unilever", "Coca-Cola",
    "Amazon Ads", "Toyota Motors", "P&G", "PepsiCo", "L'Oreal", "HSBC"
]

PUBLISHERS = [
    "NewsDaily.com", "SportsHub.net", "TechCrunch Clone", "WeatherNow.io",
    "FinanceWire.com", "GameZone.gg", "TravelBlogger.net", "HealthFirst.org"
]

DEVICE_TYPES = ["Mobile", "Desktop", "Tablet", "Connected TV"]

BROWSERS = ["Chrome", "Safari", "Firefox", "Edge", "Samsung Internet"]

GEO_COUNTRIES = [
    "United States", "India", "United Kingdom", "Germany",
    "Brazil", "Canada", "Australia", "Japan", "France", "Vietnam"
]

AD_FORMATS = ["Banner", "Video", "Native", "Interstitial"]

EXCHANGES = ["Google AdX", "PubMatic", "Rubicon Project", "OpenX", "AppNexus"]

# =============================================================================
# FRAUD DETECTION THRESHOLDS
# (Business rules the fraud_engine.py will apply)
# =============================================================================
MAX_BIDS_PER_IP_PER_MINUTE = 8       # above this = suspicious bid frequency
MIN_CLICK_LATENCY_SECONDS = 1.0      # below this = "too fast to be human"
HIGH_RISK_COUNTRIES = ["Vietnam"]    # example: geo flagged as elevated risk
DATACENTER_IP_PREFIXES = ["34.", "35.", "52."]  # simulated cloud/bot IP ranges

# =============================================================================
# COLOR PALETTE (Corporate / AdTech dashboard styling)
# =============================================================================
COLOR_PRIMARY = "#0A2540"      # deep navy — corporate trust
COLOR_ACCENT = "#00C2A8"       # teal — tech/data accent
COLOR_FRAUD = "#E63946"        # red — fraud/alert signal
COLOR_SAFE = "#2ECC71"         # green — clean traffic
COLOR_WARNING = "#F4A261"      # amber — medium risk

CHART_COLOR_SEQUENCE = [COLOR_PRIMARY, COLOR_ACCENT, COLOR_WARNING, COLOR_FRAUD]

# =============================================================================
# COLUMN NAME SCHEMA
# (Using constants instead of raw strings avoids typos across files)
# =============================================================================
COL_BID_ID = "bid_id"
COL_TIMESTAMP = "timestamp"
COL_ADVERTISER = "advertiser"
COL_PUBLISHER = "publisher"
COL_DEVICE = "device_type"
COL_BROWSER = "browser"
COL_COUNTRY = "geo_country"
COL_AD_FORMAT = "ad_format"
COL_EXCHANGE = "exchange"
COL_BID_PRICE = "bid_price_usd"
COL_WIN_PRICE = "win_price_usd"
COL_IP_ADDRESS = "ip_address"
COL_CLICK_LATENCY = "click_latency_sec"
COL_IS_WIN = "is_win"
COL_IS_FRAUD_ACTUAL = "is_fraud_actual"
COL_FRAUD_SCORE = "fraud_score"
COL_IS_FRAUD_DETECTED = "is_fraud_detected"
COL_FRAUD_REASON = "fraud_reason"