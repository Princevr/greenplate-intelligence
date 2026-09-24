import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np
# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="GreenPlate Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f7faf7;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
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
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    }

    .hero {
        background: linear-gradient(
            135deg,
            #173f2d,
            #2e7d52
        );
        padding: 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 28px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 5px;
    }

    .hero p {
        font-size: 18px;
        margin-bottom: 0px;
        opacity: 0.9;
    }

    .section-card {
        background-color: white;
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #e5ebe7;
        margin-bottom: 18px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.03);
    }

    .status-good {
        padding: 15px;
        border-radius: 12px;
        background-color: #e8f5ec;
        border-left: 5px solid #2e7d52;
        margin-bottom: 10px;
    }

    .status-warning {
        padding: 15px;
        border-radius: 12px;
        background-color: #fff7df;
        border-left: 5px solid #dba514;
        margin-bottom: 10px;
    }

    .status-danger {
        padding: 15px;
        border-radius: 12px;
        background-color: #fdeaea;
        border-left: 5px solid #c84d4d;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df.columns = df.columns.str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    numeric_cols = [
        "sales", "ordered", "unsold", "temperature_max",
        "temperature_min", "temperature_mean", "sunshine_sum",
        "precipitation_sum", "is_state_holiday",
        "is_school_holiday", "is_special_day"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["date", "store", "sales"]).sort_values(["store", "date"])

data = load_data()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🌱 GreenPlate")
st.sidebar.caption("Decision Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Demand Forecasting", "Waste & Overproduction", "Autonomous Actions"]
)

st.sidebar.divider()
st.sidebar.markdown("### 📊 Dataset")
st.sidebar.caption("Real-world food-operations data from the Green AI Hub Reduce Foodwaste project.")
st.sidebar.caption("Sales, ordered and unsold values are scaled/anonymized indices.")

# =========================================================
# HELPER: HERO
# =========================================================

def hero(title, subtitle):

    st.markdown(
        f"""
        <div class="hero">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":
    hero("🌱 GreenPlate Intelligence",
         "Decision Intelligence for Sustainable Food Operations")

    stores = sorted(data["store"].dropna().astype(str).unique())
    selected_store = st.selectbox("🏪 Select Store", stores, key="dashboard_store")
    d = data[data["store"].astype(str) == selected_store].copy().sort_values("date")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📈 Avg. Sales Index", f"{d['sales'].mean():.2f}")
    c2.metric("📦 Avg. Ordered Index", f"{d['ordered'].mean():.2f}")
    c3.metric("♻️ Avg. Unsold Index", f"{d['unsold'].mean():.2f}")
    c4.metric("🗓️ Observed Days", f"{d['date'].nunique():,}")

    st.caption("Sales, ordered and unsold values are scaled/anonymized indices from the source dataset and are not physical units or euro values.")
    st.divider()
    st.subheader("📈 Historical Sales Trend")
    st.line_chart(d.set_index("date")[["sales"]], use_container_width=True)

    st.divider()
    st.subheader("📦 Ordering & Unsold Food")
    st.line_chart(d.set_index("date")[["ordered", "unsold"]], use_container_width=True)

    st.divider()
    st.subheader("🌦️ Operational Context")
    w1, w2, w3 = st.columns(3)
    w1.metric("🌡️ Avg. Temperature", f"{d['temperature_mean'].mean():.1f} °C" if "temperature_mean" in d else "N/A")
    w2.metric("☀️ Avg. Sunshine", f"{d['sunshine_sum'].mean():.1f}" if "sunshine_sum" in d else "N/A")
    w3.metric("🌧️ Avg. Precipitation", f"{d['precipitation_sum'].mean():.1f}" if "precipitation_sum" in d else "N/A")
    st.info("GreenPlate uses historical sales together with calendar and weather information to support demand forecasting and food-waste reduction decisions.")

# =========================================================
# DEMAND FORECASTING
# =========================================================

elif page == "Demand Forecasting":
    hero("📈 Machine Learning Demand Forecasting",
         "Forecast sales demand using historical, calendar and weather data")

    stores = sorted(data["store"].dropna().astype(str).unique())
    selected_store = st.selectbox("🏪 Select Store", stores, key="forecast_store")
    f = data[data["store"].astype(str) == selected_store].copy().sort_values("date")

    st.subheader("Historical Sales")
    st.line_chart(f.set_index("date")[["sales"]], use_container_width=True)

    f["day_of_week"] = f["date"].dt.dayofweek
    f["month"] = f["date"].dt.month
    f["day_of_year"] = f["date"].dt.dayofyear
    f["lag_1"] = f["sales"].shift(1)
    f["lag_7"] = f["sales"].shift(7)
    f["rolling_7"] = f["sales"].shift(1).rolling(7).mean()

    candidates = [
        "day_of_week", "month", "day_of_year", "is_state_holiday",
        "is_school_holiday", "is_special_day", "temperature_max",
        "temperature_min", "temperature_mean", "sunshine_sum",
        "precipitation_sum", "lag_1", "lag_7", "rolling_7"
    ]
    features = [x for x in candidates if x in f.columns]
    model_data = f[["date"] + features + ["sales"]].copy()

    for col in features + ["sales"]:
        model_data[col] = pd.to_numeric(model_data[col], errors="coerce")
   # Keep rows with valid sales and lag features
model_data = model_data.dropna(
    subset=["sales", "lag_1", "lag_7", "rolling_7"]
).copy()

# Fill missing predictor values instead of deleting observations
for col in features:
    if model_data[col].isna().any():
        median_value = model_data[col].median()

        if pd.isna(median_value):
            median_value = 0

        model_data[col] = model_data[col].fillna(median_value)
    if len(model_data) < 30:
        st.warning("Not enough complete observations are available for reliable model training for this store.")
    else:
        split = int(len(model_data) * 0.80)
        train = model_data.iloc[:split]
        test = model_data.iloc[split:]

        X_train, y_train = train[features], train["sales"]
        X_test, y_test = test[features], test["sales"]

        model = RandomForestRegressor(
            n_estimators=300, random_state=42,
            min_samples_leaf=2, n_jobs=-1
        )
        model.fit(X_train, y_train)
        pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, pred)
        baseline = np.repeat(y_train.iloc[-1], len(y_test))
        baseline_mae = mean_absolute_error(y_test, baseline)

        st.subheader("🤖 Model Performance")
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE", f"{mae:.3f}")
        m2.metric("Naive Baseline MAE", f"{baseline_mae:.3f}")
        improvement = ((baseline_mae - mae) / baseline_mae * 100) if baseline_mae else None
        m3.metric("Improvement vs Baseline", f"{improvement:.1f}%" if improvement is not None else "N/A")

        comparison = pd.DataFrame({
            "Date": test["date"].values,
            "Actual Sales": y_test.values,
            "Predicted Sales": pred
        })
        st.subheader("Actual vs Predicted Sales")
        st.line_chart(comparison.set_index("Date"), use_container_width=True)
        st.caption("The final 20% of observations are used as a chronological test period.")

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
                value = f["sales"].iloc[-7] if len(f) >= 7 else f["sales"].iloc[-1]
            elif feature == "rolling_7":
                value = f["sales"].tail(7).mean()
            else:
                value = latest.get(feature, np.nan)
                if pd.isna(value):
                    value = model_data[feature].median()
            next_row[feature] = value

        next_x = pd.DataFrame([next_row], columns=features)
        next_prediction = model.predict(next_x)[0]

        st.subheader("🔮 Next-Day Sales Forecast")
        n1, n2 = st.columns(2)
        n1.metric("Forecast Date", next_date.strftime("%d %b %Y"))
        n2.metric("Predicted Sales Index", f"{next_prediction:.2f}")
        st.info("Prototype forecast: future weather and special-day inputs use the latest available values unless already known.")

# =========================================================
# WASTE & OVERPRODUCTION
# =========================================================

elif page == "Waste & Overproduction":
    hero("♻️ Waste & Overproduction Intelligence",
         "Analyze ordering, sales and unsold-food patterns to support waste reduction")

    stores = sorted(data["store"].dropna().astype(str).unique())
    selected_store = st.selectbox("🏪 Select Store", stores, key="waste_store")
    d = data[data["store"].astype(str) == selected_store].copy().sort_values("date")
    d = d.dropna(subset=["sales", "ordered", "unsold"]).copy()

    if d.empty:
        st.warning("This store does not contain enough ordered/unsold observations for this analysis.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg. Sales Index", f"{d['sales'].mean():.2f}")
        c2.metric("Avg. Ordered Index", f"{d['ordered'].mean():.2f}")
        c3.metric("Avg. Unsold Index", f"{d['unsold'].mean():.2f}")
        c4.metric("Latest Unsold Index", f"{d['unsold'].iloc[-1]:.2f}")

        st.caption("These are anonymized/scaled source values. The analysis compares patterns rather than physical quantities.")
        st.divider()
        st.subheader("📊 Sales, Ordered & Unsold Trend")
        st.line_chart(d.set_index("date")[["sales", "ordered", "unsold"]], use_container_width=True)

        d["unsold_7d_avg"] = d["unsold"].rolling(7).mean()
        st.subheader("♻️ Unsold-Food Pattern")
        st.line_chart(d.set_index("date")[["unsold", "unsold_7d_avg"]], use_container_width=True)

        recent = d.tail(min(28, len(d)))
        recent_unsold = recent["unsold"].mean()
        historical_unsold = d["unsold"].mean()

        st.subheader("🤖 GreenPlate Recommendation")
        if recent_unsold > historical_unsold and recent["ordered"].mean() > recent["sales"].mean():
            st.warning("Recent unsold-food levels are above the historical average while ordering is also above sales. Review upcoming order levels before approval.")
        elif recent_unsold > historical_unsold:
            st.warning("Recent unsold-food levels are above the historical average. Review demand, calendar and weather conditions before adjusting orders.")
        else:
            st.success("Recent unsold-food levels are not above the historical average. Continue monitoring before changing ordering levels.")

# =========================================================
# AUTONOMOUS ACTIONS
# =========================================================

elif page == "Autonomous Actions":
    hero("🤖 Controlled Decision Center",
         "Review automatically generated operational recommendations before execution")

    stores = sorted(data["store"].dropna().astype(str).unique())
    selected_store = st.selectbox("🏪 Select Store", stores, key="action_store")
    d = data[data["store"].astype(str) == selected_store].copy().sort_values("date")
    d = d.dropna(subset=["sales", "ordered", "unsold"]).copy()

    if d.empty:
        st.warning("No complete sales, ordered and unsold observations are available for this store.")
    else:
        recent = d.tail(min(28, len(d)))
        historical_unsold = d["unsold"].mean()
        recent_unsold = recent["unsold"].mean()
        recent_sales = recent["sales"].mean()
        recent_ordered = recent["ordered"].mean()

        if recent_unsold > historical_unsold and recent_ordered > recent_sales:
            decision = "Review / Reduce Upcoming Order"
            status = "Manager Approval Required"
            explanation = "Recent unsold-food levels are above the historical average and recent ordering is above sales."
            card_class = "status-warning"
        elif recent_unsold > historical_unsold:
            decision = "Monitor Unsold-Food Risk"
            status = "Review Recommended"
            explanation = "Recent unsold-food levels are above the store's historical average."
            card_class = "status-warning"
        else:
            decision = "Maintain Current Plan"
            status = "No Intervention Required"
            explanation = "Recent unsold-food levels are not above the store's historical average."
            card_class = "status-good"

        st.subheader("⚡ Current Recommendation")
        st.markdown(
            f"""<div class="{card_class}">
            <b>{decision}</b><br>
            Store: {selected_store}<br>
            Status: {status}<br>
            {explanation}
            </div>""",
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Recent Avg. Sales Index", f"{recent_sales:.2f}")
        c2.metric("Recent Avg. Ordered Index", f"{recent_ordered:.2f}")
        c3.metric("Recent Avg. Unsold Index", f"{recent_unsold:.2f}")

        st.subheader("📋 Decision Evidence")
        cols = ["date", "sales", "ordered", "unsold"]
        cols += [x for x in ["temperature_mean", "sunshine_sum", "precipitation_sum", "is_special_day"] if x in recent.columns]
        st.dataframe(recent[cols].tail(14), use_container_width=True, hide_index=True)

        st.divider()
        st.info("Prototype note: GreenPlate currently generates controlled decision recommendations only. In a real deployment, approved actions could be transmitted to ERP, inventory or supplier systems through APIs after authorization.")
