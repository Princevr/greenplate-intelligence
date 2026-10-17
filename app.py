import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="GreenPlate Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DESIGN
# =========================================================

st.markdown("""
<style>
.stApp {
    background-color: #f7faf7;
}
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 2.5rem;
    max-width: 1500px;
}
h1, h2, h3 {
    color: #163b2c;
}
[data-testid="stSidebar"] {
    background-color: #eef7f0;
}
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #e1e8e3;
    padding: 16px;
    border-radius: 12px;
}
.hero {
    background: linear-gradient(135deg, #173f2d, #2e7d52);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    color: white;
    margin-bottom: 6px;
}
.hero p {
    font-size: 17px;
    margin: 0;
    opacity: .95;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_csv("train.csv")

    df.columns = df.columns.str.strip()

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in df.columns:
        if col not in ["date", "store"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    required = {"date", "store", "sales"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )

    return (
        df.dropna(subset=["date", "store", "sales"])
        .sort_values(["store", "date"])
    )


def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def available_cols(df, cols):
    return [col for col in cols if col in df.columns]


# =========================================================
# SIDEBAR AND NAVIGATION
# =========================================================

st.sidebar.markdown("## 🌱 GreenPlate Intelligence")
st.sidebar.caption("Automating Smarter, Sustainable Food Operations")

uploaded = st.sidebar.file_uploader(
    "Optional: Upload a compatible CSV",
    type=["csv"],
)

try:
    data = load_data(uploaded)
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.info(
        "Make sure train.csv is in the same GitHub repository "
        "folder as app.py."
    )
    st.stop()


store_labels = {
    "store_0": "GreenBite Munich",
    "store_1": "FreshTable Berlin",
    "store_2": "UrbanPlate Hamburg",
    "store_3": "EcoKitchen Frankfurt",
    "store_4": "FreshFork Cologne",
    "store_5": "GreenTable Stuttgart",
    "store_6": "UrbanBite Düsseldorf",
    "store_7": "EcoPlate Leipzig",
    "store_8": "GreenFork Dresden",
}

stores = sorted(data["store"].dropna().astype(str).unique())

selected_store = st.sidebar.selectbox(
    "Select Restaurant",
    stores,
    format_func=lambda x: store_labels.get(x, x),
)

pages = [
    "Dashboard",
    "1. Demand Forecasting",
    "2. Inventory Intelligence",
    "3. Supplier & Procurement Intelligence",
    "4. Food-Waste Intelligence",
    "5. Customer Intelligence",
    "6. Logistics & Delivery Optimisation",
    "7. ESG & Sustainability Reporting",
]

page = st.sidebar.radio("Seven Core Features", pages)

st.sidebar.divider()
st.sidebar.caption("Dataset: Green AI Hub food-operations data")
st.sidebar.caption(
    "Sales, ordered and unsold values are scaled/anonymized indices, "
    "not physical units or euro values."
)
st.sidebar.caption(
    "Restaurant names are presentation labels for anonymized store IDs."
)

d = (
    data[data["store"].astype(str) == selected_store]
    .copy()
    .sort_values("date")
)

if d.empty:
    st.error("No data is available for the selected restaurant.")
    st.stop()


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    hero(
        "🌱 GreenPlate Intelligence",
        "Decision Intelligence for Sustainable Food Operations",
    )

    st.write(
        "Explore the seven core modules. The current dataset supports "
        "sales, ordering, unsold-food, weather and calendar analysis. "
        "Other modules identify the additional data needed."
    )

    st.caption(
        f"Selected demo restaurant: "
        f"{store_labels.get(selected_store, selected_store)}. "
        "This is a presentation label, not a real-world identification."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Average Sales Index", f"{d['sales'].mean():.2f}")

    if "ordered" in d.columns:
        c2.metric("Average Ordered Index", f"{d['ordered'].mean():.2f}")
    else:
        c2.metric("Average Ordered Index", "Unavailable")

    if "unsold" in d.columns:
        c3.metric("Average Unsold Index", f"{d['unsold'].mean():.2f}")
    else:
        c3.metric("Average Unsold Index", "Unavailable")

    c4.metric("Observed Days", f"{d['date'].nunique():,}")

    st.info(
        "These are scaled/anonymized indices. They are not portions, "
        "kilograms, meals, euros or measured carbon emissions."
    )

    st.subheader("Historical Sales Trend")
    st.line_chart(
        d.set_index("date")[["sales"]],
        use_container_width=True,
    )

    if {"ordered", "unsold"}.issubset(d.columns):
        st.subheader("Ordering and Unsold-Food Trend")
        st.line_chart(
            d.set_index("date")[["ordered", "unsold"]],
            use_container_width=True,
        )

    st.subheader("Your Seven Core Features")

    st.markdown("""
    1. Demand Forecasting
    2. Inventory Intelligence
    3. Supplier & Procurement Intelligence
    4. Food-Waste Intelligence
    5. Customer Intelligence
    6. Logistics & Delivery Optimisation
    7. ESG & Sustainability Reporting
    """)


# =========================================================
# 1. DEMAND FORECASTING
# =========================================================

elif page == "1. Demand Forecasting":

    hero(
        "📈 Demand Forecasting",
        "Estimate next-day sales index using historical patterns",
    )

    st.subheader("Historical Sales")
    st.line_chart(
        d.set_index("date")[["sales"]],
        use_container_width=True,
    )

    f = d.copy()

    f["day_of_week"] = f["date"].dt.dayofweek
    f["month"] = f["date"].dt.month
    f["day_of_year"] = f["date"].dt.dayofyear

    f["lag_1"] = f["sales"].shift(1)
    f["lag_7"] = f["sales"].shift(7)
    f["rolling_7"] = f["sales"].shift(1).rolling(7).mean()

    candidates = [
        "day_of_week",
        "month",
        "day_of_year",
        "is_state_holiday",
        "is_school_holiday",
        "is_special_day",
        "temperature_max",
        "temperature_min",
        "temperature_mean",
        "sunshine_sum",
        "precipitation_sum",
        "lag_1",
        "lag_7",
        "rolling_7",
    ]

    features = available_cols(f, candidates)

    model_data = f[["date"] + features + ["sales"]].copy()

    for col in features + ["sales"]:
        model_data[col] = pd.to_numeric(
            model_data[col], errors="coerce"
        )

    needed_lags = [
        col for col in ["lag_1", "lag_7", "rolling_7"]
        if col in model_data.columns
    ]

    model_data = model_data.dropna(
        subset=["sales"] + needed_lags
    )

    for col in features:
        if model_data[col].isna().any():
            median = model_data[col].median()
            model_data[col] = model_data[col].fillna(
                0 if pd.isna(median) else median
            )

    if len(model_data) < 30 or not features:

        st.warning(
            "There are not enough complete observations to train "
            "and evaluate this model for the selected restaurant."
        )

    else:

        split = int(len(model_data) * 0.80)

        train = model_data.iloc[:split]
        test = model_data.iloc[split:]

        if train.empty or test.empty:

            st.warning(
                "There are not enough observations for a "
                "chronological train/test split."
            )

        else:

            model = RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                min_samples_leaf=2,
                n_jobs=-1,
            )

            model.fit(train[features], train["sales"])

            pred = model.predict(test[features])

            mae = mean_absolute_error(test["sales"], pred)

            baseline = np.repeat(
                train["sales"].iloc[-1],
                len(test),
            )

            baseline_mae = mean_absolute_error(
                test["sales"], baseline
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("Test MAE", f"{mae:.3f}")
            c2.metric("Baseline MAE", f"{baseline_mae:.3f}")

            improvement = (
                (baseline_mae - mae) / baseline_mae * 100
                if baseline_mae else None
            )

            c3.metric(
                "Change vs Baseline",
                f"{improvement:.1f}%"
                if improvement is not None else "N/A",
            )

            comparison = pd.DataFrame(
                {
                    "Actual Index": test["sales"].values,
                    "Predicted Index": pred,
                },
                index=test["date"],
            )

            st.subheader("Actual vs Predicted")
            st.line_chart(
                comparison,
                use_container_width=True,
            )

            st.caption(
                "Evaluation uses the final 20% of observations "
                "as a chronological test period. This does not "
                "prove generalisation to other datasets."
            )

            latest = f.iloc[-1]
            next_date = latest["date"] + pd.Timedelta(days=1)

            next_row = {}

            for feature in features:

                if feature == "day_of_week":
                    value = next_date.dayofweek

                elif feature == "month":
                    value = next_date.month

                elif feature == "day_of_year":
                    value = next_date.dayofyear

                elif feature == "lag_1":
                    value = f["sales"].iloc[-1]

                elif feature == "lag_7":
                    value = (
                        f["sales"].iloc[-7]
                        if len(f) >= 7
                        else f["sales"].iloc[-1]
                    )

                elif feature == "rolling_7":
                    value = f["sales"].tail(7).mean()

                else:
                    value = latest.get(feature, np.nan)

                    if pd.isna(value):
                        value = model_data[feature].median()

                next_row[feature] = value

            next_x = pd.DataFrame(
                [next_row],
                columns=features,
            )

            forecast = model.predict(next_x)[0]

            st.subheader("Next-Day Forecast")

            c1, c2 = st.columns(2)

            c1.metric(
                "Forecast Date",
                next_date.strftime("%d %b %Y"),
            )

            c2.metric(
                "Predicted Sales Index",
                f"{forecast:.2f}",
            )

            st.info(
                "Future weather and special-day fields use the latest "
                "available values when future values are unknown. "
                "The forecast is an index, not a physical quantity."
            )


# =========================================================
# 2. INVENTORY INTELLIGENCE
# =========================================================

elif page == "2. Inventory Intelligence":

    hero(
        "📦 Inventory Intelligence",
        "Review ordering and unsold-food signals to support stock planning",
    )

    if "ordered" not in d.columns or "unsold" not in d.columns:

        st.warning(
            "This dataset needs ordered and unsold columns for this analysis."
        )

    else:

        recent = d.tail(min(28, len(d)))

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Recent Ordered Index",
            f"{recent['ordered'].mean():.2f}",
        )

        c2.metric(
            "Recent Sales Index",
            f"{recent['sales'].mean():.2f}",
        )

        c3.metric(
            "Recent Unsold Index",
            f"{recent['unsold'].mean():.2f}",
        )

        st.line_chart(
            recent.set_index("date")[["ordered", "sales", "unsold"]],
            use_container_width=True,
        )

        st.caption(
            "Values are scaled/anonymized indices. They do not "
            "represent actual on-hand stock or stockout quantities."
        )

        if (
            recent["ordered"].mean() > recent["sales"].mean()
            and recent["unsold"].mean() > d["unsold"].mean()
        ):

            st.warning(
                "Review signal: recent ordering is above recent sales "
                "and recent unsold index is above the full-period average. "
                "Check inventory records before changing orders."
            )

        else:

            st.info(
                "No combined ordering/unsold signal was triggered. "
                "This does not prove inventory is optimal."
            )


# =========================================================
# 3. SUPPLIER & PROCUREMENT INTELLIGENCE
# =========================================================

elif page == "3. Supplier & Procurement Intelligence":

    hero(
        "🚚 Supplier & Procurement Intelligence",
        "Compare supplier details and review purchase decisions",
    )

    st.warning(
        "The current dataset does not contain supplier records, prices, "
        "lead times, minimum order quantities or delivery reliability. "
        "The form below uses illustrative inputs, not actual supplier data."
    )

    with st.form("supplier_demo_form"):

        st.subheader("Enter Illustrative Supplier Details")

        supplier = st.text_input(
            "Supplier Name",
            "Demo Supplier A",
        )

        unit_price = st.number_input(
            "Unit Price (€)",
            min_value=0.0,
            value=2.50,
            step=0.10,
        )

        lead_time = st.number_input(
            "Lead Time (Days)",
            min_value=0,
            value=3,
            step=1,
        )

        reliability = st.slider(
            "On-Time Delivery Rate (%)",
            min_value=0,
            max_value=100,
            value=95,
        )

        quantity = st.number_input(
            "Planned Quantity (Units)",
            min_value=0,
            value=100,
            step=10,
        )

        submitted = st.form_submit_button(
            "Review Illustrative Purchase"
        )

    if submitted:

        st.subheader("Illustrative Review")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Supplier",
            supplier or "Not provided",
        )

        c2.metric(
            "Estimated Purchase Cost",
            f"€{unit_price * quantity:,.2f}",
        )

        c3.metric(
            "Entered On-Time Rate",
            f"{reliability}%",
        )

        st.write(f"Entered lead time: **{lead_time} days**.")

        st.caption(
            "These values are entered by the user. They are not "
            "sourced from the Green AI Hub dataset. Compare verified "
            "supplier records before making a purchasing decision."
        )


# =========================================================
# 4. FOOD-WASTE INTELLIGENCE
# =========================================================

elif page == "4. Food-Waste Intelligence":

    hero(
        "♻️ Food-Waste Intelligence",
        "Explore unsold-food patterns and identify periods for review",
    )

    if "unsold" not in d.columns or "ordered" not in d.columns:

        st.warning(
            "The selected dataset does not contain both ordered and unsold fields."
        )

    else:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average Sales Index",
            f"{d['sales'].mean():.2f}",
        )

        c2.metric(
            "Average Ordered Index",
            f"{d['ordered'].mean():.2f}",
        )

        c3.metric(
            "Average Unsold Index",
            f"{d['unsold'].mean():.2f}",
        )

        st.subheader("Sales, Ordering and Unsold Trend")

        st.line_chart(
            d.set_index("date")[["sales", "ordered", "unsold"]],
            use_container_width=True,
        )

        recent = d.tail(min(28, len(d)))

        recent_unsold = recent["unsold"].mean()
        full_unsold = d["unsold"].mean()

        st.subheader("Review Signal")

        if recent_unsold > full_unsold:

            st.warning(
                "Recent unsold-food index is above the selected "
                "restaurant's full-period average. Review demand, "
                "ordering, calendar and weather before adjusting orders."
            )

        else:

            st.success(
                "Recent unsold-food index is not above the full-period "
                "average. Continue monitoring trends."
            )

        st.caption(
            "This analysis uses anonymized/scaled indices. It does not "
            "calculate kilograms, meals or monetary waste."
        )


# =========================================================
