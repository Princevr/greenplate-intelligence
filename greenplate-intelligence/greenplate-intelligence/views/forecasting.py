import altair as alt
import pandas as pd
import streamlit as st

from core import data, engine, theme
from core.theme import MUTED, SAFFRON, EMERALD, bar_chart, kpi, section, show_chart, trend_chart

ds = data.get_dataset()
theme.page_header("Demand forecasting", "Explore demand patterns and test a forecasting model against held-out data.", "trend", ds.key)


@st.cache_data(show_spinner="Training model…")
def _forecast(daily, horizon):
    return engine.run_forecast(daily, horizon)


if ds.kind == "restaurant":
    c1, c2 = st.columns(2)
    with c1:
        target = data.choose_target(ds, "fc_t")
    with c2:
        df = data.date_filter(ds.df, "fc_d")
    data.empty_guard(df, "dates")
    daily = engine.daily_series(df, target)
    tab1, tab2 = st.tabs(["History", "Forecast"])
    with tab1, st.container(border=True):
        section("Daily demand", "Confirm source units and definitions before operational use.")
        show_chart(trend_chart(daily))
    with tab2:
        horizon = st.slider("Forecast horizon (days)", 7, 28, 14)
        res = _forecast(daily, horizon)
        if res is None:
            st.warning("At least 30 usable daily observations are needed. Widen the date range.")
            st.stop()
        gain = 100 * (1 - res["mae"] / res["base"]) if res["base"] else 0
        a, b, c = st.columns(3)
        kpi(a, "Model error (MAE)", f"{res['mae']:.2f}", "Chronological 20% holdout")
        kpi(b, "Same-weekday baseline", f"{res['base']:.2f}", "Demand one week earlier")
        kpi(c, "Difference vs baseline", f"{gain:+.0f}%", f"{res['n_test']:,} test days. Positive means lower error.")
        st.write("")
        with st.container(border=True):
            section("Outlook", "Dashed line is the forecast. The band is an approximate 80% range based on holdout errors.")
            h = daily.tail(90).rename("value").reset_index(); h.columns = ["date", "value"]
            fc = res["forecast"]
            x = alt.X("date:T", title=None)
            ch = (alt.Chart(fc).mark_area(opacity=.2, color=SAFFRON).encode(x=x, y=alt.Y("lo:Q", title=None), y2="hi:Q")
                  + alt.Chart(h).mark_line(color=EMERALD, strokeWidth=2).encode(x=x, y="value:Q")
                  + alt.Chart(fc).mark_line(color=SAFFRON, strokeWidth=2.5, strokeDash=[5, 4]).encode(x=x, y="value:Q", tooltip=["date:T", alt.Tooltip("value:Q", format=".1f")]))
            show_chart(theme._clean(ch.properties(height=300)))
        l, r = st.columns(2, gap="medium")
        with l, st.container(border=True):
            section("Test period", "Actual versus predicted")
            t = res["test"].copy(); t.index.name = "date"
            t = t.reset_index().melt("date", var_name="Series", value_name="value")
            show_chart(theme._clean(alt.Chart(t).mark_line().encode(x=alt.X("date:T", title=None), y=alt.Y("value:Q", title=None),
                       color=alt.Color("Series:N", scale=alt.Scale(range=[EMERALD, SAFFRON]), legend=alt.Legend(orient="top", title=None))).properties(height=240)))
        with r, st.container(border=True):
            section("What drives the forecast", "Relative feature importance")
            names = {"lag1": "Yesterday", "lag7": "Same day last week", "roll7": "7-day average", "dow": "Day of week", "month": "Month"}
            show_chart(bar_chart(res["importance"].rename(index=names).round(3), height=240))
        st.caption("Results are specific to this dataset and may not generalise to another restaurant.")
elif ds.kind == "bimbo":
    st.info("This is a weekly bakery sales sample, not restaurant daily sales. Consult the source documentation for what the week codes mean.")
    df = data.week_filter(ds.df, "fc_w")
    data.empty_guard(df, "weeks")
    l, r = st.columns(2, gap="medium")
    with l, st.container(border=True):
        section("Weekly adjusted demand")
        show_chart(bar_chart(df.groupby("Semana")["Demanda_uni_equil"].sum().sort_index(), horizontal=False))
    with r, st.container(border=True):
        section("Top 15 products by adjusted demand")
        show_chart(bar_chart(df.groupby("Producto_ID")["Demanda_uni_equil"].sum().nlargest(15)))
    theme.needs_data("Needed for a daily forecast", ["Dated sales history (daily or weekly with real dates)", "Enough history to hold out a test period"])
else:
    theme.needs_data("This dataset is a product catalogue, not a sales time series", ["Dated sales or demand records", "Select a demand dataset in Data Management"])
