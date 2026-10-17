import numpy as np
import streamlit as st

from core import data, engine, theme
from core.theme import bar_chart, kpi, section, show_chart, show_df, trend_chart

ds = data.get_dataset()
theme.page_header("Food-waste intelligence", "Separate demand and return signals from measured waste.", "leaf", ds.key)

if ds.kind == "bimbo" and {"Venta_uni_hoy", "Dev_uni_proxima"} <= set(ds.df.columns):
    st.warning("Returned units are not proof that edible food was wasted.")
    df = data.week_filter(ds.df, "w_w")
    data.empty_guard(df, "weeks")
    sold, ret = df["Venta_uni_hoy"].sum(), df["Dev_uni_proxima"].sum()
    a, b, c = st.columns(3)
    kpi(a, "Units sold", f"{sold:,.0f}", "Source field")
    kpi(b, "Units returned", f"{ret:,.0f}", "Source field")
    kpi(c, "Return ratio", f"{100 * ret / sold:.1f}%" if sold else "N/A", "Returned ÷ sold")
    x = df.groupby("Producto_ID").agg(sold=("Venta_uni_hoy", "sum"), returned=("Dev_uni_proxima", "sum"), adjusted_demand=("Demanda_uni_equil", "sum"))
    x["return_ratio_%"] = (100 * x.returned / x.sold.replace(0, np.nan)).round(1)
    st.write("")
    l, r = st.columns([1, 1.2], gap="medium")
    with l, st.container(border=True):
        section("Top 15 products by returns")
        show_chart(bar_chart(x.returned.nlargest(15), color=theme.SAFFRON))
    with r, st.container(border=True):
        section("Product detail")
        show_df(x.sort_values("returned", ascending=False).head(15))
elif ds.kind == "restaurant":
    c1, c2 = st.columns(2)
    with c1:
        target = data.choose_target(ds, "w_t")
    with c2:
        df = data.date_filter(ds.df, "w_d")
    data.empty_guard(df, "dates")
    daily = engine.daily_series(df, target)
    q = daily.quantile(.9)
    a, b = st.columns(2)
    kpi(a, "High-demand days", f"{int((daily > q).sum()):,}", "Above the 90th percentile")
    kpi(b, "90th-percentile demand", f"{q:,.1f}")
    st.write("")
    with st.container(border=True):
        section("Daily demand", "Demand variation can guide production reviews, but it cannot quantify waste.")
        show_chart(trend_chart(daily))
else:
    theme.needs_data("This dataset has no production, leftover, expiry or disposal quantities", ["Select a dataset with sales and returns in Data Management"])
st.write("")
theme.needs_data("Needed to measure waste", ["Quantity produced or purchased", "Quantity sold or served", "Unsold edible quantity and reason", "Expired or discarded quantity and date", "Ingredient weights and unit costs"])
