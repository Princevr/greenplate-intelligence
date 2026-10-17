# GreenPlate Intelligence

Streamlit multi-page app for sustainable food operations: landing page, executive dashboard, seven analytics
modules and a Data Management workspace.

## Structure
```
app.py                  entry point: theme, navigation, sidebar
core/engine.py          pure analytics: CSV parsing, delimiter detection, validation, forecasting (no Streamlit)
core/data.py            active dataset in session state, cached loading, shared filters
core/theme.py           design system: CSS, icons, KPI/section/chart components
views/                  landing, dashboard, data_management + 7 module pages
assets/logo.svg         sidebar logo
tests/test_engine.py    unit tests (pandas/numpy/scikit-learn only)
tests/smoke_views.py    headless run of every page with a stubbed Streamlit and synthetic data
```
Keep your three CSV files in the project root, next to `app.py`:
`data_preprocessed (1)(1).csv`, `train_sample_30k.csv`, `open_food_facts_sample(1).csv`.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
python tests/test_engine.py && python tests/smoke_views.py   # optional checks
```

## Deploy (Streamlit Community Cloud)
1. Copy this folder's contents into your repository root (keep your CSVs; replace `app.py` and `requirements.txt`).
2. `git add . && git commit -m "Redesign GreenPlate as multi-page SaaS app" && git push`
3. In Streamlit Cloud, open the app, set **Main file path** to `app.py`, and reboot. It redeploys on each push.

## Known limitations
- Uploaded CSVs live in the browser session only; there is no database, login, accounts or billing.
- No dataset contains supplier, stock, waste, route or customer-history data, so those modules show scenario tools,
  source-field signals or empty states rather than predictions.
- The forecast is a random forest on one restaurant's history; check the baseline comparison before trusting it.
- Streamlit limits layout control; a custom React/Next.js frontend would be the next step if you need pixel-level UI or accounts.
