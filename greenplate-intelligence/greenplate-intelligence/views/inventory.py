import streamlit as st

from core import data, engine, theme
from core.theme import bar_chart, kpi, section, show_chart, show_df, trend_chart

ds = data.get_dataset()
theme.page_header("Inventory intelligence", "Use demand patterns as planning signals, not automatic order quantities.", "box", ds.key)

if ds.kind == "restaurant":
    c1, c2 = st.columns(2)
    with c1:
        target = data.choose_target(ds, "inv_t")
    with c2:
        df = data.date_filter(ds.df, "inv_d")
    data.empty_guard(df, "dates")
    daily = engine.daily_series(df, target)
    c3, c4 = st.columns(2)
    window = c3.slider("Look-back window (days)", 7, max(8, min(90, len(daily))), min(28, max(7, len(daily))))
    svc = c4.selectbox("Target service level", ["90%", "95%", "97.5%", "99%"], index=1)
    z = {"90%": 1.2816, "95%": 1.6449, "97.5%": 1.96, "99%": 2.3263}[svc]
    rec = daily.tail(window)
    sd = rec.std() if len(rec) > 1 else 0.0
    k = st.columns(4)
    kpi(k[0], "Average daily demand", f"{rec.mean():,.1f}", f"Last {len(rec)} days")
    kpi(k[1], "Peak day", f"{rec.max():,.1f}")
    kpi(k[2], "Variation (std. dev.)", f"{sd:,.1f}")
    kpi(k[3], "Reference level", f"{rec.mean() + z * sd:,.1f}", f"Mean + {z:.2f} σ for one day")
    st.write("")
    l, r = st.columns([1.5, 1], gap="medium")
    with l, st.container(border=True):
        section("Daily demand")
        show_chart(trend_chart(daily))
    with r, st.container(border=True):
        section("Average by weekday", "Across the selected range")
        wd = daily.groupby(daily.index.dayofweek).mean().round(1)
        wd.index = [["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i] for i in wd.index]
        show_chart(bar_chart(wd, horizontal=False))
    st.caption("The reference level is a statistical signal. It ignores lead times, shelf life and order minimums.")
elif ds.kind == "bimbo":
    df = data.week_filter(ds.df, "inv_w")
    data.empty_guard(df, "weeks")
    agg = {"adjusted_demand": ("Demanda_uni_equil", "sum")}
    if "Venta_uni_hoy" in df: agg["units_sold"] = ("Venta_uni_hoy", "sum")
    if "Dev_uni_proxima" in df: agg["returned_units"] = ("Dev_uni_proxima", "sum")
    summ = df.groupby("Producto_ID").agg(**agg).sort_values("adjusted_demand", ascending=False)
    n = st.slider("Products to show", 5, 50, 20)
    with st.container(border=True):
        section("Top products", "Source demand and return fields. These are not stock on hand or verified waste.")
        show_df(summ.head(n))
else:
    theme.needs_data("This dataset has no stock or replenishment records", ["Select a demand dataset in Data Management"])
st.write("")
theme.needs_data("Needed for operational recommendations", ["Current stock and units", "Daily usage or sales by SKU or ingredient", "Supplier lead time and minimum order quantity", "Expiry dates and safety-stock policy"])
