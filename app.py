import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

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
    border: 1px solid #e1e6e3;
    padding: 18px 14px;
    border-radius: 14px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.04);
    min-height: 120px;
}

[data-testid="stMetricLabel"] {
    font-size: 14px;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    font-size: 26px;
    font-weight: 600;
}

[data-testid="stMetricValue"] > div {
    overflow: visible;
    white-space: nowrap;
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

data = pd.read_csv("train.csv")
data["date"] = pd.to_datetime(data["date"])

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("## 🌱 GreenPlate")
st.sidebar.caption("Decision Intelligence Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Demand Forecasting",
        "Waste & Inventory Optimization",
        "Autonomous Actions"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### 📊 Dataset")
st.sidebar.caption(
    "Real-world food operations data from the Green AI Hub "
    "Reduce Foodwaste project."
)

st.sidebar.caption(
    "Sales, ordered and unsold values are scaled/anonymized."
)

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

    hero(
        "🌱 GreenPlate Intelligence",
        "Autonomous Decision Intelligence for Sustainable Food Operations"
    )

    # --------------------------------------------------------
    # STORE FILTER
    # --------------------------------------------------------

    stores = sorted(data["store"].dropna().unique())

    selected_store = st.selectbox(
        "🏪 Select Store",
        stores
    )

    filtered_data = data[
        data["store"] == selected_store
    ].copy()

    filtered_data = filtered_data.sort_values("date")

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    avg_sales = filtered_data["sales"].mean()
    avg_ordered = filtered_data["ordered"].mean()
    avg_unsold = filtered_data["unsold"].mean()

    available_days = len(filtered_data)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "📈 Avg. Sales Index",
        f"{avg_sales:.2f}"
    )

    c2.metric(
        "📦 Avg. Ordered Index",
        f"{avg_ordered:.2f}"
    )

    c3.metric(
        "♻️ Avg. Unsold Index",
        f"{avg_unsold:.2f}"
    )

    c4.metric(
        "📅 Observed Days",
        f"{available_days:,}"
    )

    st.caption(
        "Sales, ordered and unsold values are scaled/anonymized "
        "indices from the source dataset and should not be interpreted "
        "as physical units or euro values."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # SALES TREND
    # --------------------------------------------------------

    st.subheader("📈 Historical Sales Trend")

    sales_chart = (
        filtered_data[
            ["date", "sales"]
        ]
        .dropna()
        .set_index("date")
    )

    st.line_chart(
        sales_chart,
        use_container_width=True
    )

    st.caption(
        "Daily sales pattern for the selected store. "
        "Natural variation reflects real operational time-series data."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # ORDERED VS UNSOLD
    # --------------------------------------------------------

    st.subheader("📦 Ordering & Unsold Food")

    operations_chart = (
        filtered_data[
            ["date", "ordered", "unsold"]
        ]
        .dropna()
        .set_index("date")
    )

    if not operations_chart.empty:

        st.line_chart(
            operations_chart,
            use_container_width=True
        )

    else:

        st.info(
            "Ordered and unsold information is not available "
            "for this store."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # OPERATIONAL CONTEXT
    # --------------------------------------------------------

    st.subheader("🌦️ Operational Context")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🌡️ Avg. Temperature",
        f"{filtered_data['temperature_mean'].mean():.1f} °C"
    )

    col2.metric(
        "☀️ Avg. Sunshine",
        f"{filtered_data['sunshine_sum'].mean():.1f}"
    )

    col3.metric(
        "🌧️ Avg. Precipitation",
        f"{filtered_data['precipitation_sum'].mean():.1f}"
    )

    st.info(
        "💡 GreenPlate uses historical sales together with calendar "
        "and weather information to support demand forecasting and "
        "food-waste reduction decisions."
    )
# =========================================================
# DEMAND FORECASTING
# =========================================================

elif page == "Demand Forecasting":

    hero(
        "📈 Machine Learning Demand Forecasting",
        "Forecast sales demand using historical, calendar and weather data"
    )

    # --------------------------------------------------------
    # STORE SELECTION
    # --------------------------------------------------------

    stores = sorted(data["store"].dropna().unique())

    selected_store = st.selectbox(
        "🏪 Select Store",
        stores,
        key="forecast_store"
    )

    forecast_data = data[
        data["store"] == selected_store
    ].copy()

    forecast_data = forecast_data.sort_values("date")

    # --------------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------------

    forecast_data["day_of_week"] = (
        forecast_data["date"].dt.dayofweek
    )

    forecast_data["month"] = (
        forecast_data["date"].dt.month
    )

    forecast_data["day_of_year"] = (
        forecast_data["date"].dt.dayofyear
    )

    features = [
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
        "precipitation_sum"
    ]

    target = "sales"

   model_data = forecast_data[
    ["date"] + features + [target]
].copy()

# Convert all model features and target to numeric
for col in features + [target]:
    model_data[col] = pd.to_numeric(
        model_data[col],
        errors="coerce"
    )

# Remove rows that cannot be used by the ML model
model_data = model_data.dropna(
    subset=features + [target]
).copy()

    # --------------------------------------------------------
    # CHECK DATA
    # --------------------------------------------------------

    if len(model_data) < 30:

        st.warning(
            "Not enough observations are available for "
            "reliable model training for this store."
        )

    else:

        # ----------------------------------------------------
        # CHRONOLOGICAL TRAIN / TEST SPLIT
        # ----------------------------------------------------

        split_index = int(
            len(model_data) * 0.80
        )

        train_data = model_data.iloc[
            :split_index
        ].copy()

        test_data = model_data.iloc[
            split_index:
        ].copy()

        X_train = train_data[features]
        y_train = train_data[target]

        X_test = test_data[features]
        y_test = test_data[target]

        # ----------------------------------------------------
        # MACHINE LEARNING MODEL
        # ----------------------------------------------------

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=42,
            min_samples_leaf=2
        )

        model.fit(
            X_train,
            y_train
        )

        predictions = model.predict(
            X_test
        )

        # ----------------------------------------------------
        # MODEL METRICS
        # ----------------------------------------------------

        mae = mean_absolute_error(
            y_test,
            predictions
        )

        rmse = (
            (
                (y_test.values - predictions) ** 2
            ).mean()
        ) ** 0.5

        # MAPE is only calculated where actual sales
        # values are sufficiently far from zero.
        mape_mask = (
            abs(y_test.values) > 0.1
        )

        if mape_mask.sum() > 0:

            mape = (
                abs(
                    (
                        y_test.values[mape_mask]
                        - predictions[mape_mask]
                    )
                    / y_test.values[mape_mask]
                ).mean()
                * 100
            )

        else:

            mape = None

        # ----------------------------------------------------
        # MODEL SUMMARY
        # ----------------------------------------------------

        st.subheader("🧠 Forecast Model Performance")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Training Records",
            f"{len(train_data):,}"
        )

        c2.metric(
            "Test Records",
            f"{len(test_data):,}"
        )

        c3.metric(
            "MAE",
            f"{mae:.3f}"
        )

        c4.metric(
            "RMSE",
            f"{rmse:.3f}"
        )

        if mape is not None:

            st.caption(
                f"MAPE (excluding near-zero actual values): "
                f"{mape:.1f}%"
            )

        st.info(
            "The model is trained on the first 80% of observations "
            "and evaluated on the most recent 20%. This chronological "
            "split avoids randomly mixing earlier and later dates."
        )

        st.divider()

        # ----------------------------------------------------
        # ACTUAL VS PREDICTED
        # ----------------------------------------------------

        st.subheader(
            "📊 Actual vs Predicted Sales"
        )

        forecast_results = pd.DataFrame(
            {
                "date": test_data["date"].values,
                "Actual Sales": y_test.values,
                "Predicted Sales": predictions
            }
        )

        chart_data = (
            forecast_results
            .set_index("date")
        )

        st.line_chart(
            chart_data,
            use_container_width=True
        )

        st.caption(
            "The chart compares actual sales with GreenPlate's "
            "machine-learning predictions for the test period. "
            "Sales values are scaled/anonymized indices."
        )

        st.divider()

        # ----------------------------------------------------
        # RECENT FORECAST RESULTS
        # ----------------------------------------------------

        st.subheader(
            "🔎 Recent Forecast Results"
        )

        recent_forecasts = (
            forecast_results
            .tail(20)
            .copy()
        )

        recent_forecasts[
            "Forecast Error"
        ] = (
            recent_forecasts["Actual Sales"]
            - recent_forecasts["Predicted Sales"]
        ).abs()

        recent_forecasts[
            "Actual Sales"
        ] = recent_forecasts[
            "Actual Sales"
        ].round(2)

        recent_forecasts[
            "Predicted Sales"
        ] = recent_forecasts[
            "Predicted Sales"
        ].round(2)

        recent_forecasts[
            "Forecast Error"
        ] = recent_forecasts[
            "Forecast Error"
        ].round(2)

        st.dataframe(
            recent_forecasts.sort_values(
                "date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ----------------------------------------------------
        # FEATURE IMPORTANCE
        # ----------------------------------------------------

        st.subheader(
            "🔍 What Influences the Forecast?"
        )

        feature_importance = pd.DataFrame(
            {
                "Feature": features,
                "Importance": model.feature_importances_
            }
        ).sort_values(
            "Importance",
            ascending=False
        )

        st.dataframe(
            feature_importance,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Feature importance indicates which calendar and "
            "weather variables contributed most strongly to "
            "the Random Forest model's predictions."
        )

        st.divider()

        # ----------------------------------------------------
        # GREENPLATE INSIGHT
        # ----------------------------------------------------

        st.subheader(
            "🤖 GreenPlate Forecast Insight"
        )

        latest_actual = (
            forecast_results["Actual Sales"].iloc[-1]
        )

        latest_prediction = (
            forecast_results["Predicted Sales"].iloc[-1]
        )

        difference = (
            latest_prediction - latest_actual
        )

        if difference > mae:

            st.info(
                "📈 The latest predicted demand is above the "
                "observed sales level. GreenPlate recommends "
                "monitoring whether demand is increasing before "
                "adjusting future ordering decisions."
            )

        elif difference < -mae:

            st.warning(
                "📉 The latest predicted demand is below the "
                "observed sales level. Review recent demand "
                "patterns before reducing future order levels."
            )

        else:

            st.success(
                "✅ The latest prediction is reasonably close "
                "to the observed sales level based on the "
                "model's average absolute error."
            )

        st.caption(
            "This prototype demonstrates decision support rather "
            "than guaranteed future demand. Forecast accuracy can "
            "vary by store and time period."
        )
# =========================================================
# WASTE & INVENTORY OPTIMIZATION
# =========================================================

elif page == "Waste & Inventory Optimization":

    hero(
        "♻️ Waste & Overproduction Intelligence",
        "Analyze ordering, sales and unsold-food patterns to support waste reduction"
    )

    # --------------------------------------------------------
    # STORE SELECTION
    # --------------------------------------------------------

    stores = sorted(data["store"].dropna().unique())

    selected_store = st.selectbox(
        "🏪 Select Store",
        stores,
        key="waste_store"
    )

    waste_data = data[
        data["store"] == selected_store
    ].copy()

    waste_data = waste_data.sort_values("date")

    # Only use rows where operational data is available
    operations_data = waste_data.dropna(
        subset=["sales", "ordered", "unsold"]
    ).copy()

    if operations_data.empty:

        st.warning(
            "Ordered and unsold information is not available "
            "for this store."
        )

    else:

        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        avg_sales = operations_data["sales"].mean()
        avg_ordered = operations_data["ordered"].mean()
        avg_unsold = operations_data["unsold"].mean()

        observations = len(operations_data)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "📈 Avg. Sales Index",
            f"{avg_sales:.2f}"
        )

        col2.metric(
            "📦 Avg. Ordered Index",
            f"{avg_ordered:.2f}"
        )

        col3.metric(
            "♻️ Avg. Unsold Index",
            f"{avg_unsold:.2f}"
        )

        col4.metric(
            "📅 Observations",
            f"{observations:,}"
        )

        st.caption(
            "Sales, ordered and unsold values are scaled/anonymized "
            "indices from the source dataset. They should not be "
            "interpreted as physical product units."
        )

        st.divider()

        # ----------------------------------------------------
        # ORDERED VS SALES
        # ----------------------------------------------------

        st.subheader("📦 Ordered vs. Sales")

        order_sales_chart = (
            operations_data[
                ["date", "ordered", "sales"]
            ]
            .set_index("date")
        )

        st.line_chart(
            order_sales_chart,
            use_container_width=True
        )

        st.caption(
            "Comparing ordering and sales patterns can help identify "
            "periods of potential overproduction or under-ordering."
        )

        st.divider()

        # ----------------------------------------------------
        # UNSOLD TREND
        # ----------------------------------------------------

        st.subheader("♻️ Unsold Food Trend")

        unsold_chart = (
            operations_data[
                ["date", "unsold"]
            ]
            .set_index("date")
        )

        st.line_chart(
            unsold_chart,
            use_container_width=True
        )

        st.divider()

        # ----------------------------------------------------
        # RECENT OPERATIONAL ANALYSIS
        # ----------------------------------------------------

        st.subheader("🔎 Recent Operational Signals")

        recent = operations_data.tail(30).copy()

        recent["Order-Sales Gap"] = (
            recent["ordered"] - recent["sales"]
        )

        recent["Unsold Risk"] = recent["unsold"].apply(
            lambda x:
            "High"
            if x > operations_data["unsold"].quantile(0.75)
            else (
                "Medium"
                if x > operations_data["unsold"].median()
                else "Low"
            )
        )

        display_table = recent[
            [
                "date",
                "sales",
                "ordered",
                "unsold",
                "Order-Sales Gap",
                "Unsold Risk"
            ]
        ].copy()

        display_table.columns = [
            "Date",
            "Sales Index",
            "Ordered Index",
            "Unsold Index",
            "Order-Sales Gap",
            "Unsold Risk"
        ]

        st.dataframe(
            display_table.sort_values(
                "Date",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ----------------------------------------------------
        # GREENPLATE RECOMMENDATION
        # ----------------------------------------------------

        st.subheader("🤖 GreenPlate Decision Support")

        latest = operations_data.iloc[-1]

        high_unsold_threshold = (
            operations_data["unsold"].quantile(0.75)
        )

        if latest["unsold"] > high_unsold_threshold:

            st.warning(
                "⚠️ Elevated unsold-food signal detected. "
                "GreenPlate recommends reviewing the next ordering "
                "decision and recent demand patterns before increasing "
                "the order level."
            )

        elif latest["ordered"] > latest["sales"]:

            st.info(
                "📦 The latest ordering index is above the sales index. "
                "Monitor upcoming demand and unsold-food levels before "
                "adjusting future orders."
            )

        else:

            st.success(
                "✅ No elevated unsold-food signal is detected in the "
                "latest observation. Continue monitoring demand and "
                "ordering patterns."
            )

        st.caption(
            "GreenPlate recommendations shown here are decision-support "
            "signals for the academic prototype and do not automatically "
            "execute supplier orders."
        )

# =========================================================
# AUTONOMOUS ACTIONS
# =========================================================

elif page == "Autonomous Actions":

    hero(
        "🤖 GreenPlate Decision Center",
        "Review data-driven operational recommendations and controlled actions"
    )

    # --------------------------------------------------------
    # STORE SELECTION
    # --------------------------------------------------------

    stores = sorted(data["store"].dropna().unique())

    selected_store = st.selectbox(
        "🏪 Select Store",
        stores,
        key="action_store"
    )

    action_data = data[
        data["store"] == selected_store
    ].copy()

    action_data = action_data.sort_values("date")

    action_data = action_data.dropna(
        subset=["sales", "ordered", "unsold"]
    ).copy()

    if action_data.empty:

        st.warning(
            "Operational ordering and unsold-food data "
            "is not available for this store."
        )

    else:

        # ----------------------------------------------------
        # LATEST OBSERVATION
        # ----------------------------------------------------

        latest = action_data.iloc[-1]

        latest_date = latest["date"]

        sales_index = latest["sales"]
        ordered_index = latest["ordered"]
        unsold_index = latest["unsold"]

        median_unsold = action_data["unsold"].median()

        high_unsold = action_data[
            "unsold"
        ].quantile(0.75)

        # ----------------------------------------------------
        # CURRENT STATUS
        # ----------------------------------------------------

        st.subheader("📊 Latest Operational Status")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "📅 Latest Date",
            latest_date.strftime("%d %b %Y")
        )

        c2.metric(
            "📈 Sales Index",
            f"{sales_index:.2f}"
        )

        c3.metric(
            "📦 Ordered Index",
            f"{ordered_index:.2f}"
        )

        c4.metric(
            "♻️ Unsold Index",
            f"{unsold_index:.2f}"
        )

        st.caption(
            "Operational values are scaled/anonymized indices "
            "from the source dataset."
        )

        st.divider()

        # ----------------------------------------------------
        # DECISION ENGINE
        # ----------------------------------------------------

        st.subheader("🧠 GreenPlate Decision Engine")

        if unsold_index > high_unsold:

            decision = "Manager Review"
            risk = "High"

            st.error(
                "🔴 High unsold-food signal detected."
            )

            st.write(
                "GreenPlate recommends reviewing recent demand "
                "and reducing the next ordering level if the "
                "lower-demand pattern is expected to continue."
            )

        elif unsold_index > median_unsold:

            decision = "Monitor / Adjust"
            risk = "Medium"

            st.warning(
                "🟠 Moderate unsold-food signal detected."
            )

            st.write(
                "GreenPlate recommends monitoring upcoming "
                "demand before increasing the next order."
            )

        elif ordered_index > sales_index:

            decision = "Monitor Order Level"
            risk = "Medium"

            st.warning(
                "🟡 Ordering is currently above the sales index."
            )

            st.write(
                "Review recent demand and unsold-food patterns "
                "before increasing future orders."
            )

        else:

            decision = "Maintain Current Plan"
            risk = "Low"

            st.success(
                "🟢 No elevated operational risk signal detected."
            )

            st.write(
                "Current ordering and sales patterns do not "
                "trigger an adjustment recommendation."
            )

        st.divider()

        # ----------------------------------------------------
        # CONTROLLED ACTION
        # ----------------------------------------------------

        st.subheader("⚙️ Controlled Action")

        col1, col2 = st.columns(2)

        col1.metric(
            "Risk Level",
            risk
        )

        col2.metric(
            "Recommended Action",
            decision
        )

        if decision == "Manager Review":

            st.warning(
                "👤 Human approval required before any ordering "
                "adjustment is made."
            )

        elif decision == "Monitor / Adjust":

            st.info(
                "🔍 GreenPlate recommends monitoring the next "
                "demand period before adjusting the order level."
            )

        elif decision == "Monitor Order Level":

            st.info(
                "📦 GreenPlate recommends checking whether the "
                "current order level remains appropriate for "
                "expected demand."
            )

        else:

            st.success(
                "✅ Continue the current operational plan."
            )

        st.divider()

        # ----------------------------------------------------
        # DECISION TRANSPARENCY
        # ----------------------------------------------------

        st.subheader("🔎 Why did GreenPlate recommend this?")

        explanation = pd.DataFrame(
            {
                "Decision Factor": [
                    "Sales Index",
                    "Ordered Index",
                    "Unsold Index",
                    "Median Historical Unsold",
                    "High Unsold Threshold"
                ],
                "Value": [
                    round(sales_index, 2),
                    round(ordered_index, 2),
                    round(unsold_index, 2),
                    round(median_unsold, 2),
                    round(high_unsold, 2)
                ]
            }
        )

        st.dataframe(
            explanation,
            use_container_width=True,
            hide_index=True
        )

        st.info(
            "Prototype note: GreenPlate currently generates "
            "decision-support recommendations. It does not place "
            "supplier orders automatically. In a future production "
            "system, approved actions could be integrated with "
            "ERP or supplier-management systems."
        )
