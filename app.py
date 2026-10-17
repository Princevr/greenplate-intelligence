import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ─────────────────────────────────────────────────────────────
# Page config & design tokens
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="GreenPlate Intelligence", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

BRAND, BRAND_DARK, ACCENT, INK, MUTED, LINE = "#2F7D5B", "#12372A", "#D99A1E", "#14221B", "#66766C", "#E2E8E3"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap');
:root{--brand:#2F7D5B;--deep:#12372A;--accent:#D99A1E;--ink:#14221B;--muted:#66766C;--line:#E2E8E3;--bg:#F5F7F4}
.stApp{font-family:'Figtree',sans-serif;background:var(--bg);color:var(--ink)}
h1,h2,h3,h4{font-family:'Bricolage Grotesque',sans-serif!important;color:var(--deep);letter-spacing:-.02em}
#MainMenu,footer{visibility:hidden}header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1400px;padding:1.4rem 2.4rem 3rem}

/* Sidebar */
[data-testid="stSidebar"]{background:var(--deep);border-right:0}
[data-testid="stSidebar"] *{color:#E8F1EB}
[data-testid="stSidebar"] hr{border-color:#2A5543}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:#9DB8A8}
[data-testid="stSidebar"] [role="radiogroup"]{gap:2px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:9px 12px;border-radius:8px;width:100%;cursor:pointer;transition:background .15s}
[data-testid="stSidebar"] [role="radiogroup"] label>div:first-child{display:none}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#1D4A39}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#2F7D5B}
[data-testid="stSidebar"] [role="radiogroup"] label p{font-size:14px;font-weight:600}
.brand{display:flex;align-items:center;gap:10px;margin:4px 0 2px}
.brand-mark{width:34px;height:34px;border-radius:10px;background:var(--accent);display:flex;align-items:center;justify-content:center;font-size:18px}
.brand-name{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:20px;color:#fff!important;line-height:1}
.brand-sub{font-size:12px;color:#9DB8A8!important}

/* Page header */
.ph{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin:2px 0 22px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.ph-crumb{font-size:13px;color:var(--muted);margin-bottom:6px}
.ph h1{font-size:30px;font-weight:800;margin:0 0 6px;line-height:1.1}
.ph p{margin:0;color:var(--muted);font-size:15px;max-width:680px}
.chip{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:12.5px;font-weight:600;color:var(--deep);white-space:nowrap}
.dot{width:7px;height:7px;border-radius:50%;background:var(--brand)}

/* Landing banner (dashboard only) */
.banner{background:var(--deep);color:#fff;border-radius:16px;padding:30px 34px;margin-bottom:18px;display:flex;justify-content:space-between;gap:30px;align-items:center}
.banner h1{color:#fff!important;font-size:30px;margin:0 0 10px;font-weight:800;line-height:1.12;max-width:560px}
.banner p{margin:0;color:#B9D2C3;font-size:15px;max-width:560px}
.banner-stat{text-align:right;min-width:170px}
.banner-stat b{font-family:'Bricolage Grotesque',sans-serif;font-size:44px;font-weight:800;color:var(--accent);display:block;line-height:1}
.banner-stat span{font-size:13px;color:#B9D2C3}

/* KPI */
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;height:100%}
.kpi-l{font-size:13px;color:var(--muted);font-weight:500;margin-bottom:8px}
.kpi-v{font-family:'Bricolage Grotesque',sans-serif;font-size:28px;font-weight:700;color:var(--deep);line-height:1.1}
.kpi-s{font-size:12.5px;color:var(--muted);margin-top:6px}

/* Containers, tabs, tables, inputs */
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:12px}
.sec-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:17px;color:var(--deep);margin:0 0 2px}
.sec-sub{font-size:13px;color:var(--muted);margin-bottom:10px}
.row{display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #EEF2EF;font-size:14px}
.row:last-child{border-bottom:0}.row span:last-child{color:var(--muted);font-size:13px;text-align:right}
.tag{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12px;font-weight:600}
.tag-ok{background:#E3F2E9;color:#1F6B47}.tag-warn{background:#FBF0D6;color:#8A5E0B}
.mod{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;height:100%}
.mod-i{font-size:20px;margin-bottom:8px}.mod b{display:block;font-size:14.5px;color:var(--deep);margin-bottom:4px}.mod span{font-size:13px;color:var(--muted);line-height:1.5}
.empty{border:1.5px dashed #C9D6CD;border-radius:12px;padding:18px 20px;background:#FAFCFA}
.empty b{color:var(--deep)}.empty ul{margin:8px 0 0;padding-left:18px;color:var(--muted);font-size:14px}
button[kind],.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:8px;font-weight:600}
[data-testid="stFormSubmitButton"]>button,.stDownloadButton>button{background:var(--brand);color:#fff;border:0}
[data-testid="stTabs"] [role="tab"]{font-weight:600}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
[data-testid="stAlert"]{border-radius:10px}
.foot{font-size:12.5px;color:var(--muted);padding-top:14px;border-top:1px solid var(--line);margin-top:30px}
@media(max-width:800px){.block-container{padding:1rem}.ph{flex-direction:column;align-items:flex-start}.banner{flex-direction:column;align-items:flex-start}.banner-stat{text-align:left}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# Data sources
# ─────────────────────────────────────────────────────────────
SOURCES = {
    "Restaurant demand (Germany)": ("data_preprocessed (1)(1).csv", ";", "Daily restaurant product-category demand and engineered features."),
    "Grupo Bimbo sales (Mexico)": ("train_sample_30k.csv", ",", "30,000-row bakery sales and returns sample; not restaurant-specific."),
    "Open Food Facts products": ("open_food_facts_sample(1).csv", ",", "Product ingredients, packaging and nutrition fields; not sales data."),
}
RESTAURANT_TARGETS = ["TOTAL", "TOTAL_FISCHPROD", "TOTAL_FLEISCH", "CALAMARI", "FISCH", "GARNELEN", "HAEHNCHEN", "KOEFTE", "LAMM", "STEAK"]


def num(s):
    return pd.to_numeric(s, errors="coerce")


@st.cache_data(show_spinner="Loading data…")
def load_csv(path, sep, upload_bytes=None):
    from io import BytesIO
    src = BytesIO(upload_bytes) if upload_bytes is not None else path
    df = pd.read_csv(src, sep=sep, low_memory=False)
    df.columns = df.columns.astype(str).str.strip()
    return df


def prepare(source, df):
    """Clean the raw frame for the selected source. Returns (df, targets)."""
    if source == "Restaurant demand (Germany)":
        if "DEMAND_DATE" not in df:
            raise ValueError("Expected a DEMAND_DATE column.")
        df = df.copy()
        df["DEMAND_DATE"] = pd.to_datetime(df["DEMAND_DATE"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["DEMAND_DATE"]).sort_values("DEMAND_DATE")
        targets = [c for c in RESTAURANT_TARGETS if c in df]
        for c in targets:
            df[c] = num(df[c])
        return df, targets
    if source == "Grupo Bimbo sales (Mexico)":
        required = {"Semana", "Producto_ID", "Cliente_ID", "Agencia_ID", "Demanda_uni_equil"}
        if not required.issubset(df.columns):
            raise ValueError("This does not look like the expected Grupo Bimbo sample.")
        df = df.copy()
        for c in required | {"Venta_uni_hoy", "Dev_uni_proxima", "Ruta_SAK"}:
            if c in df:
                df[c] = num(df[c])
        return df.dropna(subset=["Semana", "Demanda_uni_equil"]), ["Demanda_uni_equil"]
    df = df.copy()
    for c in ["fat_100g", "sugars_100g", "proteins_100g"]:
        if c in df:
            df[c] = num(df[c])
    return df, []


# ─────────────────────────────────────────────────────────────
# UI components
# ─────────────────────────────────────────────────────────────
def show_df(data, **kw):
    """Version-tolerant full-width dataframe."""
    try:
        st.dataframe(data, width="stretch", **kw)
    except TypeError:
        st.dataframe(data, use_container_width=True, **kw)


def show_chart(chart):
    st.altair_chart(chart.properties(width="container"))


def page_header(icon, title, subtitle):
    st.markdown(
        f"<div class='ph'><div><div class='ph-crumb'>Workspace / {title}</div><h1>{icon} {title}</h1><p>{subtitle}</p></div>"
        f"<div class='chip'><span class='dot'></span>{source}</div></div>", unsafe_allow_html=True)


def kpi(col, label, value, sub=""):
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{label}</div><div class='kpi-v'>{value}</div><div class='kpi-s'>{sub}</div></div>", unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f"<div class='sec-title'>{title}</div><div class='sec-sub'>{sub}</div>", unsafe_allow_html=True)


def needs_data(title, items):
    li = "".join(f"<li>{i}</li>" for i in items)
    st.markdown(f"<div class='empty'><b>{title}</b><ul>{li}</ul></div>", unsafe_allow_html=True)


def trend_chart(s, color=BRAND, height=280):
    d = s.rename("value").reset_index()
    d.columns = ["date", "value"]
    grad = alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0,
                        stops=[alt.GradientStop(color="white", offset=0), alt.GradientStop(color=color, offset=1)])
    base = alt.Chart(d).encode(x=alt.X("date:T", title=None), y=alt.Y("value:Q", title=None),
                               tooltip=[alt.Tooltip("date:T"), alt.Tooltip("value:Q", format=",.1f")])
    return (base.mark_area(opacity=.28, color=grad) + base.mark_line(color=color, strokeWidth=2)).properties(height=height).configure_view(strokeWidth=0).configure_axis(grid=True, gridColor="#EEF2EF", labelColor=MUTED, domain=False)


def bar_chart(s, horizontal=True, color=BRAND):
    d = s.rename("value").rename_axis("label").reset_index()
    d["label"] = d["label"].astype(str)
    h = max(180, 26 * len(d) + 20)
    if horizontal:
        enc = dict(x=alt.X("value:Q", title=None), y=alt.Y("label:N", sort="-x", title=None))
    else:
        enc = dict(x=alt.X("label:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("value:Q", title=None))
    ch = alt.Chart(d).mark_bar(color=color, cornerRadiusEnd=4).encode(tooltip=["label", alt.Tooltip("value:Q", format=",.1f")], **enc)
    return ch.properties(height=h if horizontal else 260).configure_view(strokeWidth=0).configure_axis(grid=False, labelColor=MUTED, domain=False)


def daily_series(target):
    return df.groupby("DEMAND_DATE")[target].sum(min_count=1).dropna().sort_index()


def choose_target(key):
    if not targets:
        st.warning("No recognised demand measure is available in this dataset.")
        return None
    return st.selectbox("Demand measure", targets, index=targets.index("TOTAL") if "TOTAL" in targets else 0, key=key)


# ─────────────────────────────────────────────────────────────
# Forecast model (cached)
# ─────────────────────────────────────────────────────────────
FEATURES = ["dow", "month", "lag1", "lag7", "roll7"]


def _frame(y):
    f = y.rename("y").to_frame()
    f["dow"], f["month"] = f.index.dayofweek, f.index.month
    f["lag1"], f["lag7"] = f.y.shift(1), f.y.shift(7)
    f["roll7"] = f.y.shift(1).rolling(7).mean()
    return f.dropna()


@st.cache_data(show_spinner="Training model…")
def run_forecast(daily, horizon):
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
    out = dict(mae=mean_absolute_error(test.y, pred), base=mean_absolute_error(test.y, test.lag7),
               test=pd.DataFrame({"Actual": test.y, "Predicted": pred}, index=test.index),
               importance=pd.Series(m.feature_importances_, index=FEATURES).sort_values(ascending=False), n_test=len(test))
    full = mk().fit(f[FEATURES], f.y)  # refit on all data for the forward forecast
    hist = list(y.ffill().values)
    dates, vals = [], []
    for i in range(1, horizon + 1):
        d = y.index[-1] + pd.Timedelta(days=i)
        x = pd.DataFrame([{"dow": d.dayofweek, "month": d.month, "lag1": hist[-1], "lag7": hist[-7], "roll7": float(np.mean(hist[-7:]))}])
        p = max(0.0, float(full.predict(x[FEATURES])[0]))
        hist.append(p); dates.append(d); vals.append(p)
    fc = pd.DataFrame({"date": dates, "value": vals})
    fc["lo"], fc["hi"] = (fc.value - 1.28 * resid).clip(lower=0), fc.value + 1.28 * resid
    out["forecast"] = fc
    return out


# ─────────────────────────────────────────────────────────────
# Sidebar & data loading
# ─────────────────────────────────────────────────────────────
NAV = [
    ("🏠", "Dashboard"), ("📈", "Demand forecasting"), ("📦", "Inventory"), ("🧾", "Suppliers & procurement"),
    ("♻️", "Food waste"), ("👥", "Customers"), ("🗺️", "Logistics & delivery"), ("🌍", "ESG & sustainability"), ("🔎", "Dataset explorer"),
]
with st.sidebar:
    st.markdown("<div class='brand'><div class='brand-mark'>🌿</div><div><div class='brand-name'>GreenPlate</div><div class='brand-sub'>Intelligence platform</div></div></div>", unsafe_allow_html=True)
    st.divider()
    nav = st.radio("Navigate", range(len(NAV)), format_func=lambda i: f"{NAV[i][0]}  {NAV[i][1]}", label_visibility="collapsed")
    st.divider()
    source = st.selectbox("Data source", list(SOURCES))
    filename, default_sep, description = SOURCES[source]
    st.caption(description)
    with st.expander("Use your own CSV"):
        upload = st.file_uploader("Replacement CSV", type=["csv"], label_visibility="collapsed")
        sep_choice = st.selectbox("Separator", [",", ";", "tab"], index=[",", ";", "tab"].index("tab" if default_sep == "\t" else default_sep))
    st.caption("Demo workspace · each module uses only the selected source.")

sep = "\t" if sep_choice == "tab" else sep_choice
try:
    raw = load_csv(filename, sep if upload is not None else default_sep, upload.getvalue() if upload is not None else None)
    df, targets = prepare(source, raw)
except FileNotFoundError:
    st.error(f"Cannot find {filename}. Upload a CSV in the sidebar or add the file next to app.py.")
    st.stop()
except Exception as e:
    st.error(f"Could not load this dataset: {e}")
    st.info("Check that the file matches the selected data source and separator.")
    st.stop()

# ─────────────────────────────────────────────────────────────
# Pages
# ─────────────────────────────────────────────────────────────
def page_dashboard():
    completeness = 100 * (1 - df.isna().sum().sum() / max(1, df.size))
    st.markdown(
        f"<div class='banner'><div><h1>See demand, waste and sustainability signals in one place.</h1>"
        f"<p>Review your data, test a forecast and find out what each module still needs before it can support a decision.</p></div>"
        f"<div class='banner-stat'><b>{len(df):,}</b><span>records in {source}</span></div></div>", unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    kpi(a, "Records", f"{len(df):,}", "Rows in the selected dataset")
    kpi(b, "Fields", f"{len(df.columns):,}", "Columns available")
    kpi(c, "Numeric measures", f"{len(df.select_dtypes(include=np.number).columns):,}", "Usable for analysis")
    kpi(d, "Completeness", f"{completeness:.1f}%", "Share of non-missing cells")
    st.write("")
    left, right = st.columns([1.5, 1], gap="large")
    with left, st.container(border=True):
        if source == "Restaurant demand (Germany)" and targets:
            m = "TOTAL" if "TOTAL" in targets else targets[0]
            section("Daily demand", f"{m} · last 90 days · {df.DEMAND_DATE.min():%d %b %Y} – {df.DEMAND_DATE.max():%d %b %Y} available")
            show_chart(trend_chart(daily_series(m).tail(90)))
        elif source == "Grupo Bimbo sales (Mexico)":
            section("Weekly adjusted demand", "Sum of Demanda_uni_equil by Semana")
            show_chart(bar_chart(df.groupby("Semana")["Demanda_uni_equil"].sum().sort_index(), horizontal=False))
        else:
            section("Product catalogue", "This source has no sales history. Explore packaging and nutrition fields under ESG & sustainability.")
    with right, st.container(border=True):
        section("Module readiness", "What the selected source can support")
        has_sales = source != "Open Food Facts products"
        rows = [("Demand forecasting", has_sales and source == "Restaurant demand (Germany)"), ("Inventory", has_sales),
                ("Suppliers & procurement", None), ("Food waste", False), ("Customers", source == "Grupo Bimbo sales (Mexico)"),
                ("Logistics", False), ("ESG & sustainability", source == "Open Food Facts products")]
        labels = {True: ("ok", "Ready"), False: ("warn", "Needs data"), None: ("ok", "Scenario tool")}
        html = "".join(f"<div class='row'><span>{n}</span><span class='tag tag-{labels[s][0]}'>{labels[s][1]}</span></div>" for n, s in rows)
        st.markdown(html, unsafe_allow_html=True)
    st.write("")
    mods = [("📈", "Demand forecasting", "Trends, a tested model and a 14-day outlook."), ("📦", "Inventory", "Safety-stock reference levels from demand variation."),
            ("🧾", "Suppliers & procurement", "Compare supplier offers you enter."), ("♻️", "Food waste", "Separate return signals from measured waste."),
            ("👥", "Customers", "Concentration and mix by customer ID."), ("🗺️", "Logistics & delivery", "Distribution signals and routing data gaps."),
            ("🌍", "ESG & sustainability", "Packaging and nutrition fields by product.")]
    for i in range(0, len(mods), 4):
        cols = st.columns(4, gap="medium")
        for col, (ic, t, s) in zip(cols, mods[i:i + 4]):
            col.markdown(f"<div class='mod'><div class='mod-i'>{ic}</div><b>{t}</b><span>{s}</span></div>", unsafe_allow_html=True)
            col.write("")


def page_forecast():
    page_header("📈", "Demand forecasting", "Explore demand patterns and test a forecasting model on held-out data.")
    if source == "Restaurant demand (Germany)":
        target = choose_target("t_fc")
        if not target:
            return
        daily = daily_series(target)
        tab1, tab2 = st.tabs(["History", "Forecast"])
        with tab1, st.container(border=True):
            section("Daily demand", "Confirm source units and definitions before operational use.")
            show_chart(trend_chart(daily))
        with tab2:
            horizon = st.slider("Forecast horizon (days)", 7, 28, 14)
            res = run_forecast(daily, horizon)
            if res is None:
                st.warning("At least 30 usable daily observations are needed for this model.")
                return
            a, b, c = st.columns(3)
            gain = 100 * (1 - res["mae"] / res["base"]) if res["base"] else 0
            kpi(a, "Model error (MAE)", f"{res['mae']:.2f}", "Chronological 20% holdout")
            kpi(b, "Same-weekday baseline", f"{res['base']:.2f}", "Demand one week earlier")
            kpi(c, "Improvement vs baseline", f"{gain:+.0f}%", f"{res['n_test']:,} test days")
            st.write("")
            with st.container(border=True):
                section("Outlook", "Dashed line is the forecast; the band is an approximate 80% range from holdout errors.")
                h = daily.tail(90).rename("value").reset_index(); h.columns = ["date", "value"]
                fc = res["forecast"]
                x = alt.X("date:T", title=None)
                band = alt.Chart(fc).mark_area(opacity=.2, color=ACCENT).encode(x=x, y=alt.Y("lo:Q", title=None), y2="hi:Q")
                ch = band + alt.Chart(h).mark_line(color=BRAND, strokeWidth=2).encode(x=x, y="value:Q") \
                    + alt.Chart(fc).mark_line(color=ACCENT, strokeWidth=2.5, strokeDash=[5, 4]).encode(x=x, y="value:Q", tooltip=["date:T", alt.Tooltip("value:Q", format=".1f")])
                show_chart(ch.properties(height=300).configure_view(strokeWidth=0).configure_axis(gridColor="#EEF2EF", labelColor=MUTED, domain=False))
            l, r = st.columns(2, gap="medium")
            with l, st.container(border=True):
                section("Test period: actual vs predicted")
                t = res["test"].reset_index().melt(res["test"].index.name or "index", var_name="Series", value_name="value")
                t.columns = ["date", "Series", "value"]
                show_chart(alt.Chart(t).mark_line().encode(x=alt.X("date:T", title=None), y=alt.Y("value:Q", title=None),
                           color=alt.Color("Series:N", scale=alt.Scale(range=[BRAND, ACCENT]), legend=alt.Legend(orient="top", title=None))).properties(height=240))
            with r, st.container(border=True):
                section("What drives the forecast", "Relative feature importance")
                names = {"lag1": "Yesterday", "lag7": "Same day last week", "roll7": "7-day average", "dow": "Day of week", "month": "Month"}
                show_chart(bar_chart(res["importance"].rename(index=names).round(3)).properties(height=240))
            st.caption("Performance on this dataset may not generalise to another restaurant.")
    elif source == "Grupo Bimbo sales (Mexico)":
        st.info("Weekly bakery sales sample, not restaurant daily sales. Consult the source documentation for week-code meaning.")
        l, r = st.columns(2, gap="medium")
        with l, st.container(border=True):
            section("Weekly adjusted demand")
            show_chart(trend_chart(df.groupby("Semana")["Demanda_uni_equil"].sum().sort_index()))
        with r, st.container(border=True):
            section("Top 15 products by adjusted demand")
            show_chart(bar_chart(df.groupby("Producto_ID")["Demanda_uni_equil"].sum().nlargest(15)))
    else:
        st.warning("Open Food Facts is a product catalogue, not a sales time series. Choose another source for forecasting.")


def page_inventory():
    page_header("📦", "Inventory", "Demand patterns as planning signals, not automatic order quantities.")
    if source == "Restaurant demand (Germany)" and targets:
        target = choose_target("t_inv")
        if target:
            daily = daily_series(target)
            c1, c2 = st.columns(2)
            window = c1.slider("Look-back window (days)", 7, min(90, max(8, len(daily))), min(28, len(daily)))
            svc = c2.selectbox("Target service level", ["90%", "95%", "97.5%", "99%"], index=1)
            z = {"90%": 1.2816, "95%": 1.6449, "97.5%": 1.96, "99%": 2.3263}[svc]
            recent = daily.tail(window)
            sd = recent.std() if len(recent) > 1 else 0.0
            a, b, c, d = st.columns(4)
            kpi(a, "Average daily demand", f"{recent.mean():.1f}", f"Last {window} days")
            kpi(b, "Peak day", f"{recent.max():.1f}")
            kpi(c, "Variation (std. dev.)", f"{sd:.1f}")
            kpi(d, "Reference level", f"{recent.mean() + z * sd:.1f}", f"Mean + {z:.2f}σ for one day")
            st.write("")
            l, r = st.columns([1.5, 1], gap="medium")
            with l, st.container(border=True):
                section("Daily demand")
                show_chart(trend_chart(daily))
            with r, st.container(border=True):
                section("Average by weekday", "Across the full history")
                prof = daily.groupby(daily.index.dayofweek).mean()
                prof.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][: len(prof)] if len(prof) == 7 else prof.index
                show_chart(bar_chart(prof.round(1), horizontal=False))
            st.caption("The reference level is a statistical signal. It ignores lead times, shelf life and order minimums.")
    elif source == "Grupo Bimbo sales (Mexico)":
        agg = {"adjusted_demand": ("Demanda_uni_equil", "sum")}
        if "Venta_uni_hoy" in df: agg["units_sold"] = ("Venta_uni_hoy", "sum")
        if "Dev_uni_proxima" in df: agg["returned_units"] = ("Dev_uni_proxima", "sum")
        s = df.groupby("Producto_ID").agg(**agg).sort_values("adjusted_demand", ascending=False).head(20)
        with st.container(border=True):
            section("Top 20 products", "Source demand and return fields, not stock on hand or verified waste.")
            show_df(s)
    else:
        st.warning("Product catalogue data has no stock-on-hand or replenishment records.")
    st.write("")
    needs_data("Needed for operational recommendations", ["Current stock and units", "Daily usage or sales by SKU or ingredient", "Supplier lead time and minimum order quantity", "Expiry dates and safety-stock policy"])


def page_suppliers():
    page_header("🧾", "Suppliers & procurement", "Compare supplier offers using values you enter.")
    st.warning("No supplied dataset contains verified supplier contracts, prices or lead-time performance. Every value below is your own scenario assumption.")
    with st.form("supplier_form"):
        l, r = st.columns(2, gap="large")
        with l:
            st.markdown("**Supplier A**")
            pa = st.number_input("Price per unit (€)", 0.0, value=2.5, step=.1, key="pa")
            la = st.number_input("Lead time (days)", 0, value=3, key="la")
            ra = st.slider("Reliability (%)", 0, 100, 95, key="ra")
        with r:
            st.markdown("**Supplier B**")
            pb = st.number_input("Price per unit (€)", 0.0, value=2.35, step=.1, key="pb")
            lb = st.number_input("Lead time (days)", 0, value=5, key="lb")
            rb = st.slider("Reliability (%)", 0, 100, 88, key="rb")
        qty = st.number_input("Quantity", 1, value=100, step=10)
        go = st.form_submit_button("Compare suppliers")
    if go:
        rows = [{"Supplier": n, "Purchase cost (€)": p * qty, "Cost per reliably delivered unit (€)": (p / (r / 100)) if r else np.nan, "Lead time (days)": l, "Reliability (%)": r}
                for n, p, l, r in [("A", pa, la, ra), ("B", pb, lb, rb)]]
        out = pd.DataFrame(rows)
        a, b = st.columns(2)
        cheap = out.loc[out["Purchase cost (€)"].idxmin(), "Supplier"]
        rel = out.loc[out["Reliability (%)"].idxmax(), "Supplier"]
        kpi(a, "Lowest purchase cost", f"Supplier {cheap}", "Before delivery, quality and contract terms")
        kpi(b, "Highest reliability", f"Supplier {rel}", "As entered")
        st.write("")
        show_df(out.round(2), hide_index=True)
        st.caption("Reliability-adjusted cost divides price by the entered reliability. It excludes delivery charges and other costs.")


def page_waste():
    page_header("♻️", "Food waste", "Separate demand and return signals from measured waste.")
    if source == "Grupo Bimbo sales (Mexico)" and {"Venta_uni_hoy", "Dev_uni_proxima"} <= set(df.columns):
        st.warning("Returned units are not proof that edible food was wasted.")
        sold, ret = df["Venta_uni_hoy"].sum(), df["Dev_uni_proxima"].sum()
        a, b, c = st.columns(3)
        kpi(a, "Units sold", f"{sold:,.0f}", "Source field")
        kpi(b, "Units returned", f"{ret:,.0f}", "Source field")
        kpi(c, "Return ratio", f"{100 * ret / sold:.1f}%" if sold else "N/A", "Returned ÷ sold")
        st.write("")
        x = df.groupby("Producto_ID").agg(sold=("Venta_uni_hoy", "sum"), returned=("Dev_uni_proxima", "sum"), adjusted_demand=("Demanda_uni_equil", "sum"))
        x["return_ratio_%"] = (100 * x.returned / x.sold.replace(0, np.nan)).round(1)
        l, r = st.columns([1, 1.2], gap="medium")
        with l, st.container(border=True):
            section("Top 15 products by returns")
            show_chart(bar_chart(x.returned.nlargest(15), color=ACCENT))
        with r, st.container(border=True):
            section("Product detail")
            show_df(x.sort_values("returned", ascending=False).head(15))
    elif source == "Restaurant demand (Germany)" and targets:
        target = choose_target("t_waste")
        if target:
            daily = daily_series(target)
            q = daily.quantile(.9)
            a, b = st.columns(2)
            kpi(a, "High-demand days", f"{int((daily > q).sum()):,}", "Above the 90th percentile")
            kpi(b, "90th-percentile demand", f"{q:.1f}")
            st.write("")
            with st.container(border=True):
                section("Daily demand", "Demand variation can guide production reviews, but it cannot quantify waste.")
                show_chart(trend_chart(daily))
    else:
        st.warning("Open Food Facts has no production, leftover, expiry or disposal quantities.")
    st.write("")
    needs_data("Needed to measure waste", ["Quantity produced or purchased", "Quantity sold or served", "Unsold edible quantity and reason", "Expired or discarded quantity and date", "Ingredient weights and unit costs"])


def page_customers():
    page_header("👥", "Customers", "Explore customer-level patterns where the data supports them.")
    if source == "Grupo Bimbo sales (Mexico)":
        x = df.groupby("Cliente_ID").agg(adjusted_demand=("Demanda_uni_equil", "sum"), records=("Producto_ID", "count"), unique_products=("Producto_ID", "nunique")).sort_values("adjusted_demand", ascending=False)
        top_share = 100 * x.adjusted_demand.head(max(1, len(x) // 10)).sum() / max(1, x.adjusted_demand.sum())
        a, b, c = st.columns(3)
        kpi(a, "Customer IDs", f"{len(x):,}")
        kpi(b, "Product IDs", f"{df['Producto_ID'].nunique():,}")
        kpi(c, "Demand from top 10% of customers", f"{top_share:.0f}%", "Concentration")
        st.write("")
        with st.container(border=True):
            section("Top 20 customer IDs", "IDs are source identifiers, not named people. Churn needs dated repeat purchases and an inactivity rule.")
            show_df(x.head(20))
    elif source == "Restaurant demand (Germany)":
        st.info("This source is product-category demand per day, not customer transactions. Churn and lifetime value cannot be estimated from it.")
    else:
        st.info("Open Food Facts describes products, not customer purchases.")
    st.write("")
    needs_data("Needed for customer analytics", ["Pseudonymous customer ID", "Dated purchases or subscriptions", "Order value and product mix", "Cancellation or inactivity definition"])


def page_logistics():
    page_header("🗺️", "Logistics & delivery", "Check distribution signals and the data gaps for route planning.")
    st.warning("None of the supplied datasets combines delivery coordinates, time windows, vehicle capacity and stop-level records, so real routes cannot be optimised.")
    if source == "Grupo Bimbo sales (Mexico)":
        a, b, c = st.columns(3)
        kpi(a, "Agencies", f"{df['Agencia_ID'].nunique():,}")
        kpi(b, "Route IDs", f"{df['Ruta_SAK'].nunique():,}" if "Ruta_SAK" in df else "Unavailable")
        kpi(c, "Customer IDs", f"{df['Cliente_ID'].nunique():,}")
        st.write("")
        with st.container(border=True):
            section("Top 20 agencies by demand", "Identifiers are not geographic coordinates.")
            show_chart(bar_chart(df.groupby("Agencia_ID")["Demanda_uni_equil"].sum().nlargest(20)))
    elif source == "Restaurant demand (Germany)":
        st.info("Daily category demand can help estimate workload, but it has no delivery locations or travel times.")
    else:
        st.info("Product catalogue fields do not describe delivery operations.")
    st.write("")
    needs_data("Needed for route optimisation", ["Delivery addresses or coordinates", "Orders and quantities per stop", "Delivery time windows", "Vehicle capacity and operating hours", "Travel-time matrix and depot location"])


def page_esg():
    page_header("🌍", "ESG & sustainability", "Inspect product-level packaging and nutrition fields.")
    if source == "Open Food Facts products":
        a, b, c = st.columns(3)
        kpi(a, "Products", f"{len(df):,}")
        kpi(b, "With packaging listed", f"{df['packaging'].notna().sum():,}" if "packaging" in df else "Unavailable")
        kpi(c, "With ingredients listed", f"{df['ingredients_text'].notna().sum():,}" if "ingredients_text" in df else "Unavailable")
        st.write("")
        if "packaging" in df:
            p = df["packaging"].dropna().astype(str).str.strip()
            p = p[p.ne("")].value_counts().head(15)
            if len(p):
                with st.container(border=True):
                    section("Most common packaging descriptions")
                    show_chart(bar_chart(p))
        cols = [c for c in ["product_name", "brands", "categories", "countries", "packaging", "ingredients_text", "fat_100g", "sugars_100g", "proteins_100g"] if c in df]
        with st.container(border=True):
            section("Product sample", "First 50 rows")
            show_df(df[cols].head(50))
        st.caption("This sample does not establish lifecycle impact, a company footprint or ESG-standard compliance. Missing packaging data is not evidence of sustainable packaging.")
    else:
        st.warning("This source has no company emissions, packaging lifecycle, energy use or verified sustainability indicators.")
    st.write("")
    needs_data("Needed for company ESG reporting", ["Electricity, heating and fuel use", "Purchased goods and packaging weights and materials", "Food waste by weight and disposal route", "Transport distance and fuel data", "Reporting boundaries, methods and source records"])


def page_explorer():
    page_header("🔎", "Dataset explorer", "Inspect columns and data quality.")
    a, b = st.columns(2)
    kpi(a, "Rows", f"{len(df):,}")
    kpi(b, "Columns", f"{len(df.columns):,}")
    st.write("")
    report = pd.DataFrame({"Column": df.columns, "Data type": [str(df[c].dtype) for c in df], "Missing values": [int(df[c].isna().sum()) for c in df],
                           "Missing (%)": [round(float(df[c].isna().mean() * 100), 2) for c in df], "Unique values": [int(df[c].nunique(dropna=True)) for c in df]})
    t1, t2 = st.tabs(["Column quality", "Data preview"])
    with t1:
        show_df(report, height=440)
        st.download_button("Download quality report", report.to_csv(index=False).encode("utf-8"), file_name="greenplate_data_quality_report.csv", mime="text/csv")
    with t2:
        show_df(df.head(20))


PAGES = [page_dashboard, page_forecast, page_inventory, page_suppliers, page_waste, page_customers, page_logistics, page_esg, page_explorer]
if nav == 0:
    st.write("")
PAGES[nav]()

st.markdown("<div class='foot'>Prototype: outputs are exploratory and depend on the selected sample. Validate definitions, units, completeness and model performance before making business decisions.</div>", unsafe_allow_html=True)
