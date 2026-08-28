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

data = pd.read_csv("greenplate_restaurant_data_v2.csv")
data["Date"] = pd.to_datetime(data["Date"])

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

restaurant = st.sidebar.selectbox(
    "Select Restaurant",
    data["Restaurant_Name"].unique()
)

filtered_data = data[
    data["Restaurant_Name"] == restaurant
].copy()

st.sidebar.divider()

st.sidebar.caption(
    "Prototype based on synthetic restaurant operational data."
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

    total_units_sold = filtered_data["Units_Sold"].sum()
    total_demand = filtered_data["Customer_Demand"].sum()
    total_lost_sales = filtered_data["Lost_Sales"].sum()
    total_waste = filtered_data["Waste_Units"].sum()
    total_waste_cost = filtered_data["Waste_Cost_EUR"].sum()
    total_revenue = filtered_data["Revenue_EUR"].sum()
    avg_service_level = filtered_data["Service_Level_Pct"].mean()

    st.subheader("Business Performance")

    col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Customer Demand",
    f"{total_demand/1000:.1f}K units"
)

    col2.metric(
        "Units Sold",
        f"{total_units_sold:,.0f}"
    )

    col3.metric(
        "Lost Sales",
        f"{total_lost_sales:,.0f} units"
    )

    col4.metric(
    "Revenue",
    f"€{total_revenue/1000:.1f}K"
)
    col5, col6, col7 = st.columns(3)

    col5.metric(
        "Food Waste",
        f"{total_waste:,.0f} units"
    )

    col6.metric(
        "Waste Cost",
        f"€{total_waste_cost:,.2f}"
    )

    col7.metric(
        "Service Level",
        f"{avg_service_level:.2f}%"
    )

    st.divider()

    st.subheader("📈 Customer Demand Trend")

    demand_by_date = (
        filtered_data
        .groupby("Date")["Customer_Demand"]
        .sum()
        .reset_index()
    )

    st.line_chart(
        demand_by_date,
        x="Date",
        y="Customer_Demand"
    )

    st.subheader("🛒 Sales Trend")

    sales_by_date = (
        filtered_data
        .groupby("Date")["Units_Sold"]
        .sum()
        .reset_index()
    )

    st.line_chart(
        sales_by_date,
        x="Date",
        y="Units_Sold"
    )

    st.subheader("♻️ Food Waste Trend")

    waste_by_date = (
        filtered_data
        .groupby("Date")["Waste_Units"]
        .sum()
        .reset_index()
    )

    st.line_chart(
        waste_by_date,
        x="Date",
        y="Waste_Units"
    )

    st.divider()

    latest_date = filtered_data["Date"].max()

    latest_inventory = filtered_data[
        filtered_data["Date"] == latest_date
    ][
        [
            "Product",
            "Closing_Stock",
            "Safety_Stock",
            "Recommended_Order",
            "Autonomous_Decision",
            "Service_Level_Pct"
        ]
    ]

    st.subheader("📦 Current Inventory")

    st.dataframe(
        latest_inventory,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# DEMAND FORECASTING
# =========================================================

elif page == "Demand Forecasting":

    hero(
        "📈 Machine Learning Demand Forecasting",
        "Predict future customer demand using historical operational data"
    )

    product = st.selectbox(
        "Select Product",
        filtered_data["Product"].unique()
    )

    product_data = filtered_data[
        filtered_data["Product"] == product
    ].copy()

    product_data = product_data.sort_values("Date")

    st.subheader(
        f"Historical Customer Demand — {product}"
    )

    st.line_chart(
        product_data[
            [
                "Date",
                "Customer_Demand"
            ]
        ].set_index("Date")
    )

    # -----------------------------------------------------
    # FEATURE ENGINEERING
    # -----------------------------------------------------

    product_data["DayOfWeek"] = (
        product_data["Date"].dt.dayofweek
    )

    product_data["Month"] = (
        product_data["Date"].dt.month
    )

    product_data["Lag_1"] = (
        product_data["Customer_Demand"].shift(1)
    )

    product_data["Lag_7"] = (
        product_data["Customer_Demand"].shift(7)
    )

    product_data["Rolling_7"] = (
        product_data["Customer_Demand"]
        .shift(1)
        .rolling(window=7)
        .mean()
    )

    model_data = product_data.dropna().copy()

    features = [
        "DayOfWeek",
        "Month",
        "Temperature_C",
        "Is_Weekend",
        "Promotion",
        "Lag_1",
        "Lag_7",
        "Rolling_7"
    ]

    X = model_data[features]
    y = model_data["Customer_Demand"]

    split_index = int(
        len(model_data) * 0.8
    )

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    non_zero = y_test != 0

    if non_zero.sum() > 0:

        mape = (
            abs(
                (
                    y_test[non_zero]
                    -
                    predictions[non_zero]
                )
                /
                y_test[non_zero]
            )
            .mean()
            * 100
        )

    else:

        mape = 0

    st.subheader("🤖 Model Performance")

    col1, col2 = st.columns(2)

    col1.metric(
        "Mean Absolute Error",
        f"{mae:.2f} units"
    )

    col2.metric(
        "MAPE",
        f"{mape:.2f}%"
    )

    comparison = pd.DataFrame(
        {
            "Date":
                model_data["Date"].iloc[
                    split_index:
                ],

            "Actual Demand":
                y_test.values,

            "Predicted Demand":
                predictions
        }
    )

    st.subheader(
        "Actual vs Predicted Demand"
    )

    st.line_chart(
        comparison.set_index("Date")
    )

    # -----------------------------------------------------
    # NEXT-DAY FORECAST
    # -----------------------------------------------------

    latest_row = product_data.iloc[-1]

    next_date = (
        latest_row["Date"]
        + pd.Timedelta(days=1)
    )

    lag_1 = product_data[
        "Customer_Demand"
    ].iloc[-1]

    lag_7 = product_data[
        "Customer_Demand"
    ].iloc[-7]

    rolling_7 = (
        product_data[
            "Customer_Demand"
        ]
        .tail(7)
        .mean()
    )

    next_day_data = pd.DataFrame(
        {
            "DayOfWeek": [
                next_date.dayofweek
            ],

            "Month": [
                next_date.month
            ],

            "Temperature_C": [
                latest_row["Temperature_C"]
            ],

            "Is_Weekend": [
                1
                if next_date.dayofweek >= 5
                else 0
            ],

            "Promotion": [0],

            "Lag_1": [lag_1],

            "Lag_7": [lag_7],

            "Rolling_7": [rolling_7]
        }
    )

    next_prediction = max(
        0,
        round(
            model.predict(
                next_day_data
            )[0]
        )
    )

    current_stock = latest_row[
        "Closing_Stock"
    ]

    safety_stock = max(
        5,
        round(
            next_prediction * 0.25
        )
    )

    recommended_order = max(
        0,
        next_prediction
        + safety_stock
        - current_stock
    )

    st.subheader("🔮 Next-Day Decision")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Predicted Demand",
        f"{next_prediction} units"
    )

    col2.metric(
        "Current Stock",
        f"{current_stock:.0f} units"
    )

    col3.metric(
        "Safety Stock",
        f"{safety_stock} units"
    )

    col4.metric(
        "Recommended Order",
        f"{recommended_order:.0f} units"
    )

    st.subheader(
        "🤖 GreenPlate Decision"
    )

    required_stock = (
        next_prediction
        + safety_stock
    )

    excess_stock = (
        current_stock
        - required_stock
    )

    if recommended_order > 50:

        st.warning(
            f"Manager review required. "
            f"Recommended order: "
            f"{recommended_order:.0f} units."
        )

    elif recommended_order > 0:

        st.success(
            f"Auto-order approved: "
            f"{recommended_order:.0f} units "
            f"of {product}."
        )

    elif excess_stock > next_prediction:

        st.error(
            f"Overstock risk detected. "
            f"Current stock exceeds the expected "
            f"requirement by {excess_stock:.0f} units. "
            f"Reduce or stop the next order."
        )

    else:

        st.success(
            "Inventory is sufficient. "
            "No purchasing action required."
        )

# =========================================================
# WASTE & INVENTORY OPTIMIZATION
# =========================================================

elif page == "Waste & Inventory Optimization":

    hero(
        "♻️ Waste & Inventory Optimization",
        "Identify shortages, overstock and potential food-waste risk"
    )

    latest_date = filtered_data["Date"].max()

    latest_data = filtered_data[
        filtered_data["Date"] == latest_date
    ].copy()

    avg_demand = (
        filtered_data
        .groupby("Product")["Customer_Demand"]
        .mean()
    )

    avg_waste = (
        filtered_data
        .groupby("Product")["Waste_Units"]
        .mean()
    )

    results = []

    for _, row in latest_data.iterrows():

        product = row["Product"]
        current_stock = row["Closing_Stock"]

        expected_demand = round(
            avg_demand.get(
                product,
                0
            )
        )

        safety_stock = max(
            5,
            round(
                expected_demand * 0.25
            )
        )

        required_stock = (
            expected_demand
            + safety_stock
        )

        excess_stock = max(
            0,
            current_stock
            - required_stock
        )

        shortage = max(
            0,
            required_stock
            - current_stock
        )

        historical_waste = round(
            avg_waste.get(
                product,
                0
            ),
            1
        )

        if excess_stock > expected_demand:

            waste_risk = "High"

        elif excess_stock > (
            expected_demand * 0.30
        ):

            waste_risk = "Medium"

        else:

            waste_risk = "Low"

        if shortage > 50:

            action = "Manager Review"

        elif shortage > 0:

            action = "Auto-Order"

        elif waste_risk == "High":

            action = "Reduce / Stop Order"

        elif waste_risk == "Medium":

            action = "Monitor Inventory"

        else:

            action = "No Action"

        results.append(
            {
                "Product": product,
                "Current Stock": current_stock,
                "Expected Demand": expected_demand,
                "Safety Stock": safety_stock,
                "Required Stock": required_stock,
                "Excess Stock": excess_stock,
                "Shortage": shortage,
                "Historical Waste": historical_waste,
                "Waste Risk": waste_risk,
                "GreenPlate Action": action
            }
        )

    optimization = pd.DataFrame(
        results
    )

    high_risk = (
        optimization["Waste Risk"]
        == "High"
    ).sum()

    medium_risk = (
        optimization["Waste Risk"]
        == "Medium"
    ).sum()

    total_excess = optimization[
        "Excess Stock"
    ].sum()

    total_shortage = optimization[
        "Shortage"
    ].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "High Waste Risk",
        high_risk
    )

    col2.metric(
        "Medium Waste Risk",
        medium_risk
    )

    col3.metric(
        "Excess Inventory",
        f"{total_excess:.0f} units"
    )

    col4.metric(
        "Stock Shortage",
        f"{total_shortage:.0f} units"
    )

    st.divider()

    st.subheader(
        "📦 Product-Level Analysis"
    )

    st.dataframe(
        optimization,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "🤖 GreenPlate Recommendations"
    )

    for _, row in optimization.iterrows():

        action = row[
            "GreenPlate Action"
        ]

        if action == "Reduce / Stop Order":

            st.error(
                f"{row['Product']}: "
                f"High overstock risk. "
                f"Reduce or stop the next supplier order."
            )

        elif action == "Monitor Inventory":

            st.warning(
                f"{row['Product']}: "
                f"Moderate overstock. Monitor closely."
            )

        elif action == "Auto-Order":

            st.success(
                f"{row['Product']}: "
                f"Auto-order {row['Shortage']:.0f} units."
            )

        elif action == "Manager Review":

            st.warning(
                f"{row['Product']}: "
                f"Manager approval required for "
                f"{row['Shortage']:.0f} units."
            )

        else:

            st.info(
                f"{row['Product']}: "
                f"No action required."
            )

# =========================================================
# AUTONOMOUS ACTIONS
# =========================================================

elif page == "Autonomous Actions":

    hero(
        "🤖 Autonomous Actions Center",
        "Review GreenPlate's automatically generated operational decisions"
    )

    latest_date = filtered_data["Date"].max()

    latest_data = filtered_data[
        filtered_data["Date"] == latest_date
    ].copy()

    avg_demand = (
        filtered_data
        .groupby("Product")["Customer_Demand"]
        .mean()
    )

    actions = []

    for _, row in latest_data.iterrows():

        product = row["Product"]

        current_stock = row[
            "Closing_Stock"
        ]

        expected_demand = round(
            avg_demand.get(
                product,
                0
            )
        )

        safety_stock = max(
            5,
            round(
                expected_demand * 0.25
            )
        )

        required_stock = (
            expected_demand
            + safety_stock
        )

        difference = (
            required_stock
            - current_stock
        )

        if difference > 50:

            action = "Manager Review"
            quantity = difference
            status = "Pending Approval"

        elif difference > 0:

            action = "Auto-Order"
            quantity = difference
            status = "Auto Approved"

        elif current_stock > (
            required_stock
            + expected_demand
        ):

            action = "Reduce / Stop Order"
            quantity = 0
            status = "Automatic Recommendation"

        else:

            action = "No Action"
            quantity = 0
            status = "Inventory Healthy"

        actions.append(
            {
                "Product": product,
                "Expected Demand": expected_demand,
                "Current Stock": current_stock,
                "Safety Stock": safety_stock,
                "Action": action,
                "Quantity": max(
                    0,
                    round(quantity)
                ),
                "Status": status
            }
        )

    actions_df = pd.DataFrame(
        actions
    )

    auto_orders = (
        actions_df["Action"]
        == "Auto-Order"
    ).sum()

    manager_reviews = (
        actions_df["Action"]
        == "Manager Review"
    ).sum()

    reduced_orders = (
        actions_df["Action"]
        == "Reduce / Stop Order"
    ).sum()

    healthy_inventory = (
        actions_df["Action"]
        == "No Action"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Auto Orders",
        auto_orders
    )

    col2.metric(
        "Manager Reviews",
        manager_reviews
    )

    col3.metric(
        "Orders Reduced",
        reduced_orders
    )

    col4.metric(
        "Healthy Inventory",
        healthy_inventory
    )

    st.divider()

    st.subheader(
        "⚡ Decision Queue"
    )

    st.dataframe(
        actions_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader(
        "Autonomous Decision Log"
    )

    for _, row in actions_df.iterrows():

        if row["Action"] == "Auto-Order":

            st.markdown(
                f"""
                <div class="status-good">
                <b>✅ {row['Product']}</b><br>
                Auto-order <b>{row['Quantity']} units</b><br>
                Status: {row['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )

        elif row["Action"] == "Manager Review":

            st.markdown(
                f"""
                <div class="status-warning">
                <b>⚠️ {row['Product']}</b><br>
                Proposed order: <b>{row['Quantity']} units</b><br>
                Status: {row['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )

        elif row["Action"] == "Reduce / Stop Order":

            st.markdown(
                f"""
                <div class="status-danger">
                <b>🛑 {row['Product']}</b><br>
                Overstock detected.<br>
                Recommendation: Reduce or stop next supplier order.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="status-good">
                <b>✔ {row['Product']}</b><br>
                Inventory level is healthy.<br>
                No action required.
                </div>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.info(
        "Prototype note: GreenPlate currently simulates autonomous "
        "decision execution. In a real deployment, approved actions "
        "could be transmitted to ERP, inventory and supplier systems "
        "through APIs."
    )
