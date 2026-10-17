import streamlit as st

from core import data, theme
from core.theme import kpi, section, show_df

ds = data.get_dataset()
theme.page_header("Customer intelligence", "Explore customer-level patterns where the data supports them.", "users", ds.key)

if ds.kind == "bimbo":
    df = data.week_filter(ds.df, "c_w")
    data.empty_guard(df, "weeks")
    x = df.groupby("Cliente_ID").agg(adjusted_demand=("Demanda_uni_equil", "sum"), records=("Producto_ID", "count"), unique_products=("Producto_ID", "nunique")).sort_values("adjusted_demand", ascending=False)
    tot = x.adjusted_demand.sum()
    share = 100 * x.adjusted_demand.head(max(1, len(x) // 10)).sum() / tot if tot else 0
    a, b, c = st.columns(3)
    kpi(a, "Customer IDs", f"{len(x):,}")
    kpi(b, "Product IDs", f"{df['Producto_ID'].nunique():,}")
    kpi(c, "Demand from top 10% of customers", f"{share:.0f}%", "Concentration")
    st.write("")
    n = st.slider("Customers to show", 10, 100, 20, step=10)
    with st.container(border=True):
        section("Top customer IDs", "IDs are source identifiers, not named people. Churn needs dated repeat purchases and an inactivity rule.")
        show_df(x.head(n))
elif ds.kind == "restaurant":
    theme.needs_data("This dataset is product-category demand per day, not customer transactions", ["Churn and lifetime value cannot be estimated from these fields"])
else:
    theme.needs_data("Open Food Facts describes products, not customer purchases", ["Select a dataset with customer identifiers in Data Management"])
st.write("")
theme.needs_data("Needed for customer analytics", ["Pseudonymous customer ID", "Dated purchases or subscriptions", "Order value and product mix", "Cancellation or inactivity definition"])
