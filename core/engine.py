"""Pure data/analytics logic. No Streamlit imports, so it is unit-testable."""
from io import BytesIO

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

SOURCES = {
    "Restaurant demand (Germany)": dict(file="data_preprocessed (1)(1).csv", sep=";", kind="restaurant",
        desc="Daily restaurant product-category demand with engineered features."),
    "Grupo Bimbo sales (Mexico)": dict(file="train_sample_30k.csv", sep=",", kind="bimbo",
        desc="30,000-row bakery sales and returns sample. Not restaurant-specific."),
    "Open Food Facts products": dict(file="open_food_facts_sample(1).csv", sep=",", kind="off",
        desc="Product ingredients, packaging and nutrition fields. Not sales data."),
}
RESTAURANT_TARGETS = ["TOTAL", "TOTAL_FISCHPROD", "TOTAL_FLEISCH", "CALAMARI", "FISCH", "GARNELEN", "HAEHNCHEN", "KOEFTE", "LAMM", "STEAK"]
BIMBO_REQUIRED = {"Semana", "Producto_ID", "Cliente_ID", "Agencia_ID", "Demanda_uni_equil"}
OFF_EXPECTED = ["product_name", "packaging", "ingredients_text"]
SEPARATORS = {"Auto-detect": None, "Comma (,)": ",", "Semicolon (;)": ";", "Tab": "\t"}

# module -> {dataset kind: (tone, label)}   tone: ok | warn | no
READINESS = {
    "Demand forecasting": dict(restaurant=("ok", "Ready"), bimbo=("warn", "Weekly view only"), off=("no", "Needs sales data")),
    "Inventory intelligence": dict(restaurant=("ok", "Planning signals"), bimbo=("ok", "Demand and returns"), off=("no", "Needs stock data")),
    "Supplier & procurement": dict(restaurant=("warn", "Scenario tool"), bimbo=("warn", "Scenario tool"), off=("warn", "Scenario tool")),
    "Food-waste intelligence": dict(restaurant=("warn", "Demand signals only"), bimbo=("warn", "Return signals only"), off=("no", "Needs waste data")),
    "Customer intelligence": dict(restaurant=("no", "Needs customer data"), bimbo=("ok", "Customer IDs"), off=("no", "Needs customer data")),
    "Logistics & delivery": dict(restaurant=("no", "Needs route data"), bimbo=("warn", "Identifiers only"), off=("no", "Needs route data")),
    "ESG & sustainability": dict(restaurant=("no", "Needs company data"), bimbo=("no", "Needs company data"), off=("ok", "Product attributes")),
}


def detect_sep(data: bytes, default=","):
    """Pick the delimiter that appears most often in the header line."""
    head = data[:8192].decode("utf-8-sig", errors="replace")
    first = next((l for l in head.splitlines() if l.strip()), "")
    counts = {s: first.count(s) for s in [",", ";", "\t"]}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else default


def read_csv_bytes(data: bytes, sep=None, default_sep=","):
    if not data or not data.strip():
        raise ValueError("The file is empty.")
    used = sep or detect_sep(data, default_sep)
    try:
        df = pd.read_csv(BytesIO(data), sep=used, low_memory=False, encoding="utf-8-sig", encoding_errors="replace")
    except pd.errors.EmptyDataError:
        raise ValueError("The file has no readable columns.")
    except pd.errors.ParserError as e:
        raise ValueError(f"The file could not be parsed with separator {used!r}: {e}")
    df.columns = df.columns.astype(str).str.strip()
    if df.shape[1] == 1 and sep is not None:
        raise ValueError("Only one column was found. The separator is probably wrong; choose another or use auto-detect.")
    return df, used


def validate(kind, df):
    """Return a list of (level, message). level: error | warning."""
    out = []
    if df.empty:
        return [("error", "The file has no data rows.")]
    if kind == "restaurant":
        if "DEMAND_DATE" not in df:
            out.append(("error", "Missing required column DEMAND_DATE."))
        if not [c for c in RESTAURANT_TARGETS if c in df]:
            out.append(("error", "None of the expected demand columns were found (for example TOTAL, FISCH, STEAK)."))
    elif kind == "bimbo":
        miss = sorted(BIMBO_REQUIRED - set(df.columns))
        if miss:
            out.append(("error", "Missing required columns: " + ", ".join(miss) + "."))
        for c in ["Venta_uni_hoy", "Dev_uni_proxima", "Ruta_SAK"]:
            if c not in df:
                out.append(("warning", f"Optional column {c} is absent; related views will be limited."))
    else:
        if not any(c in df for c in OFF_EXPECTED):
            out.append(("warning", "None of product_name, packaging or ingredients_text were found; ESG views will be limited."))
    return out


def prepare(kind, df):
    """Clean the frame for a dataset kind. Returns (df, targets). Raises ValueError on a bad schema."""
    errors = [m for lvl, m in validate(kind, df) if lvl == "error"]
    if errors:
        raise ValueError(" ".join(errors))
    df = df.copy()
    if kind == "restaurant":
        df["DEMAND_DATE"] = pd.to_datetime(df["DEMAND_DATE"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["DEMAND_DATE"]).sort_values("DEMAND_DATE")
        if df.empty:
            raise ValueError("No valid dates were found in DEMAND_DATE.")
        targets = [c for c in RESTAURANT_TARGETS if c in df]
        for c in targets:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df, targets
    if kind == "bimbo":
        for c in BIMBO_REQUIRED | {"Venta_uni_hoy", "Dev_uni_proxima", "Ruta_SAK"}:
            if c in df:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["Semana", "Demanda_uni_equil"])
        if df.empty:
            raise ValueError("No usable rows remain after removing missing Semana / Demanda_uni_equil values.")
        return df, ["Demanda_uni_equil"]
    for c in ["fat_100g", "sugars_100g", "proteins_100g"]:
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df, []


def daily_series(df, target):
    return df.groupby("DEMAND_DATE")[target].sum(min_count=1).dropna().sort_index()


def quality_report(df):
    return pd.DataFrame({
        "Column": df.columns, "Type": [str(df[c].dtype) for c in df],
        "Missing": [int(df[c].isna().sum()) for c in df],
        "Missing (%)": [round(float(df[c].isna().mean() * 100), 1) for c in df],
        "Unique": [int(df[c].nunique(dropna=True)) for c in df]})


FEATURES = ["dow", "month", "lag1", "lag7", "roll7"]


def _frame(y):
    f = y.rename("y").to_frame()
    f["dow"], f["month"] = f.index.dayofweek, f.index.month
    f["lag1"], f["lag7"] = f.y.shift(1), f.y.shift(7)
    f["roll7"] = f.y.shift(1).rolling(7).mean()
    return f.dropna()


def run_forecast(daily, horizon=14):
    """Random-forest forecast with a chronological 80/20 holdout. Returns None if < 30 usable rows."""
    y = daily.asfreq("D")
    f = _frame(y)
    if len(f) < 30:
        return None
    split = int(len(f) * .8)
    train, test = f.iloc[:split], f.iloc[split:]
    mk = lambda: RandomForestRegressor(n_estimators=150, random_state=42, min_samples_leaf=2, n_jobs=-1)
    m = mk().fit(train[FEATURES], train.y)
    pred = m.predict(test[FEATURES])
    resid = float(np.std(test.y.values - pred))
    res = dict(mae=float(mean_absolute_error(test.y, pred)), base=float(mean_absolute_error(test.y, test.lag7)),
               test=pd.DataFrame({"Actual": test.y, "Predicted": pred}, index=test.index), n_test=len(test),
               importance=pd.Series(m.feature_importances_, index=FEATURES).sort_values(ascending=False))
    full = mk().fit(f[FEATURES], f.y)
    hist = list(y.ffill().values)
    dates, vals = [], []
    for i in range(1, horizon + 1):
        d = y.index[-1] + pd.Timedelta(days=i)
        x = pd.DataFrame([{"dow": d.dayofweek, "month": d.month, "lag1": hist[-1], "lag7": hist[-7], "roll7": float(np.mean(hist[-7:]))}])
        p = max(0.0, float(full.predict(x[FEATURES])[0]))
        hist.append(p); dates.append(d); vals.append(p)
    fc = pd.DataFrame({"date": dates, "value": vals})
    fc["lo"], fc["hi"] = (fc.value - 1.28 * resid).clip(lower=0), fc.value + 1.28 * resid
    res["forecast"] = fc
    return res
