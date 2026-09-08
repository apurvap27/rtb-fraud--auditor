# 📡 Digital Advertising RTB & Ad Fraud Detection Auditor

A production-style Streamlit dashboard simulating a Real-Time Bidding (RTB) 
bidstream and applying rule-based Invalid Traffic (IVT) / ad fraud detection, 
built to demonstrate AdTech data analytics and fraud auditing workflows.

## Features
- Synthetic, reproducible 15,000-row RTB bidstream dataset (advertisers, 
  publishers, geos, devices, exchanges, bid/win economics)
- Rule-based fraud scoring engine detecting 4 distinct IVT signals:
  high bid frequency, inhuman click latency, datacenter IP signatures, 
  and high-risk geography
- Ground-truth fraud typologies (bid flooding bots, click farms, evasive 
  fraud) used to validate detector performance (Precision / Recall / F1)
- Interactive filtering by date range, advertiser, geography, and device
- Live KPI dashboard: spend, win rate, fraud rate, wasted spend
- Visual analytics: bid volume & fraud trend, fraud rate by geography, 
  top fraud-linked publishers, device mix, fraud-by-rule breakdown

## Tech Stack
- Python 3.12
- Streamlit 1.38
- Pandas 2.2 / NumPy 1.26
- Plotly 5.24

## Running Locally
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
config.py -- central constants, schema, thresholds, color palette
data_generator.py -- synthetic bidstream data generation
fraud_engine.py -- rule-based fraud scoring logic
utils.py -- KPI calculations & formatting helpers
app.py -- Streamlit dashboard UI


## Disclaimer
All data is synthetically generated for demonstration purposes. No real 
advertiser, publisher, or user data is used.