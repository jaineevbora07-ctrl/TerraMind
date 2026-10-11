# TerraMind – SIH26017 Prototype

A Streamlit prototype for the SIH problem:
**Predictive Analytics System for Early Detection of Land Acquisition Delays**

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
streamlit run app.py
```

The browser will open the TerraMind dashboard.

## Prototype note

The current scoring engine is intentionally explainable and does NOT claim to be a trained ML model.
It is designed for the SIH prototype/demo. With verified historical government data, the scoring
engine can be replaced by a trained and validated machine-learning model.

## Main screens

- Dashboard
- New Case Prediction
- Case Monitoring
- About
