import streamlit as st

from core import data, engine, theme
from core.theme import icon

theme.hide_sidebar()
st.markdown(f"<div class='lp-nav'><div class='lp-brand'><div class='lp-mark'>{icon('leaf', 20)}</div>GreenPlate Intelligence</div>"
            f"<div class='chip'><span class='dot'></span>Sustainable food operations</div></div>", unsafe_allow_html=True)
st.markdown("<div class='lp-hero'><h1>Plan demand, cut guesswork, report sustainability with confidence.</h1>"
            "<p>GreenPlate brings demand forecasting, inventory signals, supplier comparison and product sustainability data into one workspace for food businesses. "
            "Every figure comes from the data you load, and anything the data cannot support is clearly marked.</p>"
            "<div class='pill-row'><span class='chip'>7 analytics modules</span><span class='chip'>CSV upload with validation</span><span class='chip'>Tested forecasting model</span></div></div>", unsafe_allow_html=True)
st.write("")
c1, c2, _ = st.columns([1, 1, 3])
if c1.button("Open dashboard", type="primary"):
    st.switch_page("views/dashboard.py")
if c2.button("Manage data"):
    st.switch_page("views/data_management.py")

# Live preview from the bundled restaurant file, if present
try:
    spec = engine.SOURCES["Restaurant demand (Germany)"]
    p = data.find_file(spec["file"])
    raw, _ = data._load_path(str(p), p.stat().st_mtime, spec["sep"])
    df, targets = engine.prepare("restaurant", raw)
    m = "TOTAL" if "TOTAL" in targets else targets[0]
    with st.container(border=True):
        theme.section("Live preview", f"Daily {m} demand from the bundled restaurant dataset, last 90 days.")
        theme.show_chart(theme.trend_chart(engine.daily_series(df, m).tail(90), height=220))
except Exception:
    pass

st.markdown("<h2 class='lp-h2'>Seven modules, one workspace</h2><div class='lp-sub'>Each module works from the dataset you select and says plainly when it needs more data.</div>", unsafe_allow_html=True)
mods = [("trend", "Demand forecasting", "Trends, a holdout-tested model and a short outlook."), ("box", "Inventory intelligence", "Reference levels from demand variation."),
        ("list", "Supplier & procurement", "Compare offers you enter side by side."), ("leaf", "Food-waste intelligence", "Return and demand signals, separated from measured waste."),
        ("users", "Customer intelligence", "Concentration and mix by customer ID."), ("map", "Logistics & delivery", "Distribution signals and routing data gaps."),
        ("globe", "ESG & sustainability", "Packaging and nutrition fields by product.")]
for i in range(0, 7, 4):
    for col, (ic, t, s) in zip(st.columns(4, gap="medium"), mods[i:i + 4]):
        col.markdown(f"<div class='mod'><div class='mod-i'>{icon(ic, 20)}</div><b>{t}</b><span>{s}</span></div>", unsafe_allow_html=True)
    st.write("")

st.markdown("<h2 class='lp-h2'>How it works</h2>", unsafe_allow_html=True)
for col, (t, s) in zip(st.columns(3, gap="medium"), [
        ("1. Load your data", "Choose a bundled dataset or upload a CSV. GreenPlate detects the delimiter and checks the columns."),
        ("2. Explore each module", "Filter by date, product or week, then review charts, KPIs and tables."),
        ("3. Validate before acting", "Model error is shown next to a simple baseline so you can judge whether to trust a forecast.")]):
    col.markdown(f"<div class='step'><b>{t}</b><span>{s}</span></div>", unsafe_allow_html=True)

st.markdown("<h2 class='lp-h2'>Honest by design</h2>", unsafe_allow_html=True)
for col, (t, s) in zip(st.columns(3, gap="medium"), [
        ("No invented results", "GreenPlate never shows savings, waste reduction or carbon figures that your data does not contain."),
        ("Datasets stay separate", "Restaurant demand, bakery sales and product catalogue data are never merged."),
        ("Clear data gaps", "Where a feature needs stock, route or waste records, you see exactly what to provide.")]):
    col.markdown(f"<div class='step'><b>{t}</b><span>{s}</span></div>", unsafe_allow_html=True)
st.markdown("<div class='foot'>GreenPlate Intelligence · prototype. Outputs are exploratory and depend on the data provided.</div>", unsafe_allow_html=True)
