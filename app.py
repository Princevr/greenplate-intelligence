
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="GreenPlate Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Branding ----------
st.markdown("""
<style>
.stApp { background: #f6f8f5; }
[data-testid="stSidebar"] {
    background: #102e26;
}
[data-testid="stSidebar"] * {
    color: #f3faf5 !important;
}
.brand {
    font-size: 25px;
    font-weight: 750;
    color: #176b4d;
    letter-spacing: -0.7px;
}
.subtitle { color: #68776f; font-size: 14px; }
.hero {
    padding: 26px;
    border-radius: 18px;
    background: linear-gradient(120deg, #103b2e, #287653);
    color: white;
    margin-bottom: 22px;
}
.hero h1 { color: white; margin-bottom: 5px; }
.hero p { color: #e2f2e8; }
.metric-card {
    background: white;
    border: 1px solid #e4ebe5;
    border-radius: 14px;
    padding: 18px;
    min-height: 110px;
}
.metric-label { color: #64746b; font-size: 13px; }
.metric-value { color: #163e30; font-size: 25px; font-weight: 700; }
.section-note {
    padding: 12px 15px;
    background: #edf5ef;
    border-radius: 10px;
    color: #285640;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Dataset loading ----------
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"

DATASETS = {
    "Restaurant demand data": [
        ROOT / "data_preprocessed (1)(1).csv",
        DATA_DIR / "data_preprocessed (1)(1).csv",
    ],
    "Grupo Bimbo sales sample": [
        ROOT / "train_sample_30k.csv",
        DATA_DIR / "train_sample_30k.csv",
    ],
    "Open Food Facts sample": [
        ROOT / "open_food_facts_sample(1).csv",
        DATA_DIR / "open_food_facts_sample(1).csv",
    ],
}

@st.cache_data(show_spinner=False)
def load_csv(path_string):
    path = Path(path_string)
    # Detect comma or semicolon separators automatically.
    try:
        df = pd.read_csv(path, sep=None, engine="python", nrows=100000)
        if len(df.columns) == 1:
            df = pd.read_csv(path, sep=";", nrows=100000)
        return df
    except Exception:
        return pd.read_csv(path, sep=";", nrows=100000)

def find_dataset(label):
    for path in DATASETS[label]:
        if path.exists():
            try:
                return load_csv(str(path)), path.name
            except Exception:
                continue
    return None, None

def numeric_columns(df):
    return list(df.select_dtypes(include="number").columns)

def date_columns(df):
    found = []
    for col in df.columns:
        if any(word in str(col).lower()
               for word in ["date", "day", "time", "month", "year"]):
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().sum() > 0:
                found.append(col)
    return found

def show_metric(label, value, help_text=None):
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if help_text:
        st.caption(help_text)

def show_data_notice(df, source_name):
    st.markdown(
        f'<div class="section-note">Dataset: <b>{source_name}</b> '
        f'· {len(df):,} rows · {len(df.columns):,} columns. '
        'Results depend on the fields available in this dataset.</div>',
        unsafe_allow_html=True,
    )

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🌿 GreenPlate")
    st.caption("Sustainable food operations")
    st.divider()

    page = st.radio(
        "WORKSPACE",
        [
            "Executive Dashboard",
            "Demand Forecasting",
            "Inventory Intelligence",
            "Supplier & Procurement",
            "Food-Waste Intelligence",
            "Customer Intelligence",
            "Logistics & Delivery",
            "ESG Reporting",
            "Data Management",
        ],
    )

    st.divider()
    st.caption("AUTONOMOUS DECISION INTELLIGENCE")
    st.caption("Demo environment · Sample datasets")

# ---------- Header ----------
st.markdown(
    '<div class="brand">GreenPlate Intelligence</div>'
    '<div class="subtitle">Automating smarter, sustainable food operations</div>',
    unsafe_allow_html=True,
)
st.write("")

# Dataset selection is kept on Data Management, not cluttering the dashboard.
if "dataset_label" not in st.session_state:
    st.session_state.dataset_label = "Grupo Bimbo sales sample"

if page == "Data Management":
    st.title("Data Management")
    st.write("Manage the sample data used by your analytics workspace.")

    selected = st.selectbox(
        "Active dataset",
        list(DATASETS.keys()),
        index=list(DATASETS.keys()).index(st.session_state.dataset_label),
    )
    st.session_state.dataset_label = selected

    df, source_name = find_dataset(selected)

    st.subheader("Available datasets")
    for label in DATASETS:
        data, filename = find_dataset(label)
        if data is not None:
            st.success(f"{label}: {filename} · {len(data):,} rows")
        else:
            st.warning(f"{label}: file not found in the repository")

    st.subheader("Upload a temporary CSV")
    upload = st.file_uploader("Choose a CSV file", type=["csv"])
    if upload is not None:
        try:
            uploaded_df = pd.read_csv(upload, sep=None, engine="python")
            st.session_state.uploaded_data = uploaded_df
            st.session_state.uploaded_name = upload.name
            st.success("File loaded for this session.")
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")

    if "uploaded_data" in st.session_state:
        if st.checkbox("Use uploaded dataset for this session"):
            df = st.session_state.uploaded_data
            source_name = st.session_state.uploaded_name

    if df is not None:
        show_data_notice(df, source_name)
        st.write("**Data preview**")
        st.dataframe(df.head(20), use_container_width=True)
        st.write("**Column summary**")
        summary = pd.DataFrame({
            "Column": df.columns,
            "Data type": [str(t) for t in df.dtypes],
            "Missing values": [int(df[c].isna().sum()) for c in df.columns],
            "Unique values": [int(df[c].nunique()) for c in df.columns],
        })
        st.dataframe(summary, use_container_width=True)
    st.stop()

# Load selected data for the rest of the application.
df, source_name = find_dataset(st.session_state.dataset_label)

if "uploaded_data" in st.session_state:
    df = st.session_state.uploaded_data
    source_name = st.session_state.uploaded_name

if df is None:
    st.warning("The selected dataset could not be found.")
    st.info("Open Data Management to check available files or upload a CSV.")
    st.stop()

nums = numeric_columns(df)
dates = date_columns(df)
show_data_notice(df, source_name)
st.write("")

# ---------- Executive Dashboard ----------
if page == "Executive Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Smarter decisions. Less waste.</h1>
        <p>One workspace to explore demand, inventory, procurement,
        customers, logistics and sustainability performance.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_metric("Records analysed", f"{len(df):,}")
    with c2:
        show_metric("Data fields", f"{len(df.columns):,}")
    with c3:
        show_metric("Numeric fields", f"{len(nums):,}")
    with c4:
        missing = int(df.isna().sum().sum())
        show_metric("Missing values", f"{missing:,}")

    st.subheader("Explore your operational data")
    st.write("Select a module from the sidebar to investigate the available data.")

    if nums:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Numeric data overview**")
            chosen = st.selectbox("Choose a measure", nums, key="dash_measure")
            st.bar_chart(df[chosen].dropna().head(30))
        with col2:
            st.markdown("**Data quality**")
            missing_by_col = df.isna().sum().sort_values(ascending=False).head(12)
            st.bar_chart(missing_by_col)

    st.subheader("Analytics workspace")
    modules = [
        ("Demand Forecasting", "Explore demand patterns and indicative projections."),
        ("Inventory Intelligence", "Review available numeric measures and stock-related fields."),
        ("Supplier & Procurement", "Review supplier data when supplier-level fields are available."),
        ("Food-Waste Intelligence", "Explore waste data when actual waste measurements are available."),
        ("Customer Intelligence", "Explore customer behaviour when customer-level history is available."),
        ("Logistics & Delivery", "Review delivery and route data when those fields are available."),
        ("ESG Reporting", "Inspect product, packaging and sustainability-related fields."),
    ]
    for left in range(0, len(modules), 2):
        cols = st.columns(2)
        for j, (name, description) in enumerate(modules[left:left + 2]):
            with cols[j]:
                st.markdown(f"**{name}**")
                st.caption(description)

# ---------- Demand Forecasting ----------
elif page == "Demand Forecasting":
    st.title("Demand Forecasting")
    st.write("Explore historical measures and generate a simple indicative baseline.")
    if not nums:
        st.warning("No numeric columns are available for analysis.")
    else:
        measure = st.selectbox("Measure to analyse", nums)
        values = pd.to_numeric(df[measure], errors="coerce").dropna()
        a, b, c = st.columns(3)
        with a:
            show_metric("Observations", f"{len(values):,}")
        with b:
            show_metric("Average", f"{values.mean():,.2f}")
        with c:
            show_metric("Median", f"{values.median():,.2f}")

        st.subheader("Observed values")
        st.line_chart(values.reset_index(drop=True).head(200))

        window = st.slider("Baseline window (observations)", 3, 30, 7)
        if len(values) >= window:
            baseline = values.tail(window).mean()
            st.metric("Indicative baseline", f"{baseline:,.2f}")
            st.caption("This is a trailing-average baseline, not a validated machine-learning forecast.")

        if dates:
            date_col = st.selectbox("Date field (optional)", dates)
            temp = df[[date_col, measure]].copy()
            temp[date_col] = pd.to_datetime(temp[date_col], errors="coerce")
            temp[measure] = pd.to_numeric(temp[measure], errors="coerce")
            temp = temp.dropna().sort_values(date_col)
            if not temp.empty:
                st.subheader("Measure over time")
                st.line_chart(temp.set_index(date_col)[measure].resample("D").mean())

# ---------- Inventory Intelligence ----------
elif page == "Inventory Intelligence":
    st.title("Inventory Intelligence")
    st.write("Review numeric measures that may support stock planning.")
    if nums:
        measure = st.selectbox("Choose an inventory-related measure", nums)
        values = pd.to_numeric(df[measure], errors="coerce").dropna()
        a, b, c = st.columns(3)
        with a:
            show_metric("Average", f"{values.mean():,.2f}")
        with b:
            show_metric("Minimum", f"{values.min():,.2f}")
        with c:
            show_metric("Maximum", f"{values.max():,.2f}")
        st.subheader("Distribution")
        st.bar_chart(values.value_counts().sort_index().head(40))
    else:
        st.warning("No numeric fields are available.")
    st.info("Stock-on-hand, reorder points and lead times are required for genuine replenishment recommendations.")

# ---------- Supplier & Procurement ----------
elif page == "Supplier & Procurement":
    st.title("Supplier & Procurement Intelligence")
    st.write("Assess whether your dataset supports supplier performance analysis.")
    matches = [c for c in df.columns if any(
        term in str(c).lower()
        for term in ["supplier", "vendor", "purchase", "lead_time", "delivery_time", "cost"]
    )]
    if matches:
        st.success("Potential procurement fields found.")
        st.dataframe(df[matches].head(50), use_container_width=True)
    else:
        st.warning("No clear supplier, vendor or procurement fields were detected.")
        st.write("Add supplier identity, purchase cost, order quantities, lead times and delivery performance to enable supplier comparisons.")
    st.caption("No real supplier ranking is generated from unrelated sales data.")

# ---------- Food-Waste Intelligence ----------
elif page == "Food-Waste Intelligence":
    st.title("Food-Waste Intelligence")
    st.write("Explore waste measurements and potential data gaps.")
    waste_cols = [c for c in df.columns if any(
        term in str(c).lower()
        for term in ["waste", "discard", "spoil", "expired", "food_loss"]
    )]
    if waste_cols:
        st.success("Potential waste-related fields found.")
        st.dataframe(df[waste_cols].describe(include="all").T, use_container_width=True)
    else:
        st.warning("This dataset does not appear to contain direct food-waste measurements.")
        st.write("Demand or sales data alone cannot establish how much food was wasted.")
        st.write("To measure waste, record discarded quantity, reason, date and product.")
    if nums:
        st.subheader("Available numeric indicators")
        st.write(", ".join(map(str, nums[:20])))

# ---------- Customer Intelligence ----------
elif page == "Customer Intelligence":
    st.title("Customer Intelligence")
    st.write("Check whether customer-level behavioural analysis is possible.")
    customer_cols = [c for c in df.columns if any(
        term in str(c).lower()
        for term in ["customer", "client", "user_id", "customer_id", "churn", "order_date"]
    )]
    if customer_cols:
        st.success("Potential customer-related fields found.")
        st.dataframe(df[customer_cols].head(50), use_container_width=True)
    else:
        st.warning("No clear customer identifier or customer history was detected.")
        st.write("Customer churn and retention require repeated customer transactions over time.")
    st.caption("This page does not claim to predict churn without suitable historical data.")

# ---------- Logistics & Delivery ----------
elif page == "Logistics & Delivery":
    st.title("Logistics & Delivery Optimisation")
    st.write("Check for delivery, route and transport information.")
    route_cols = [c for c in df.columns if any(
        term in str(c).lower()
        for term in ["route", "distance", "delivery", "latitude", "longitude",
                     "latitude", "longitude", "fuel", "vehicle", "transport"]
    )]
    if route_cols:
        st.success("Potential logistics fields found.")
        st.dataframe(df[route_cols].head(50), use_container_width=True)
    else:
        st.warning("No clear route or delivery fields were detected.")
        st.write("Route optimisation requires locations, delivery stops, distances or travel times.")
    st.caption("No optimised route or carbon saving is claimed from sales-only data.")

# ---------- ESG Reporting ----------
elif page == "ESG Reporting":
    st.title("ESG & Sustainability Reporting")
    st.write("Explore fields that may support environmental and packaging reporting.")
    esg_cols = [c for c in df.columns if any(
        term in str(c).lower()
        for term in ["packaging", "plastic", "carbon", "co2", "emission",
                     "sustain", "recycl", "material", "energy", "nutrition"]
    )]
    if esg_cols:
        st.success("Potential product or sustainability fields found.")
        st.dataframe(df[esg_cols].head(50), use_container_width=True)
    else:
        st.warning("No direct ESG or carbon-footprint fields were detected.")
        st.write("Actual emissions reporting requires suitable activity data and documented emission factors.")
    st.caption("Product attributes are not the same as verified environmental impact.")

# ---------- Footer ----------
st.divider()
st.caption(
    "GreenPlate Intelligence · Demonstration platform · "
    "Insights depend on data availability and have not been independently validated."
)
