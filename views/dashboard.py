import numpy as np
import pandas as pd
import streamlit as st

from core import data, engine, theme
from core.theme import icon, kpi, section, show_chart, tag

ds = data.get_dataset()
df = ds.df
theme.page_header("Executive dashboard", "Your sustainable food operations at a glance, built only from the dataset you have selected.", "grid", ds.key)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
lines, chart, chart_title, chart_sub = [], None, "", ""
k = st.columns(4)

if ds.kind == "restaurant":
    m = "TOTAL" if "TOTAL" in ds.targets else ds.targets[0]
    s = engine.daily_series(df, m)
    delta = None
    if len(s) >= 14 and s.iloc[-14:-7].mean():
        delta = 100 * (s.tail(7).mean() / s.iloc[-14:-7].mean() - 1)
    kpi(k[0], "Days of history", f"{len(s):,}", f"{s.index.min():%d %b %Y} – {s.index.max():%d %b %Y}")
    kpi(k[1], f"Average daily {m}", f"{s.mean():,.1f}", "Across all days")
    kpi(k[2], "Last 7 days vs previous 7", f"{delta:+.1f}%" if delta is not None else "N/A", "Change in average daily demand")
    kpi(k[3], "Peak day", f"{s.max():,.0f}", f"{s.idxmax():%d %b %Y}")
    wd = s.groupby(s.index.dayofweek).mean()
    lines = [f"<b>{DAYS[int(wd.idxmax())]}</b> is the busiest weekday on average ({wd.max():,.1f} vs {wd.min():,.1f} on {DAYS[int(wd.idxmin())]}).",
             f"Demand on the top 10% of days is above <b>{s.quantile(.9):,.1f}</b>.",
             f"Recent 28-day average: <b>{s.tail(28).mean():,.1f}</b> (standard deviation {s.tail(28).std():,.1f})."]
    chart, chart_title, chart_sub = theme.trend_chart(s.tail(90)), "Daily demand", f"{m} · latest 90 days"
elif ds.kind == "bimbo":
    tot = df["Demanda_uni_equil"].sum()
    kpi(k[0], "Records", f"{len(df):,}", "Rows in the sample")
    kpi(k[1], "Products", f"{df['Producto_ID'].nunique():,}", "Unique product IDs")
    kpi(k[2], "Customers", f"{df['Cliente_ID'].nunique():,}", "Unique customer IDs")
    if {"Venta_uni_hoy", "Dev_uni_proxima"} <= set(df.columns) and df["Venta_uni_hoy"].sum():
        kpi(k[3], "Return ratio", f"{100 * df['Dev_uni_proxima'].sum() / df['Venta_uni_hoy'].sum():.1f}%", "Returned ÷ sold units")
    else:
        kpi(k[3], "Adjusted demand", f"{tot:,.0f}", "Total units")
    top = df.groupby("Producto_ID")["Demanda_uni_equil"].sum().nlargest(1)
    wk = df.groupby("Semana")["Demanda_uni_equil"].sum()
    lines = [f"Product <b>{int(top.index[0])}</b> accounts for {100 * top.iloc[0] / tot:.1f}% of adjusted demand." if tot else "No demand recorded.",
             f"Highest-demand week code: <b>{int(wk.idxmax())}</b> ({wk.max():,.0f} units)."]
    chart, chart_title, chart_sub = theme.bar_chart(wk.sort_index(), horizontal=False), "Weekly adjusted demand", "Sum of Demanda_uni_equil by Semana"
else:
    pk = df["packaging"].notna().mean() * 100 if "packaging" in df else None
    ing = df["ingredients_text"].notna().mean() * 100 if "ingredients_text" in df else None
    kpi(k[0], "Products", f"{len(df):,}", "Rows in the sample")
    kpi(k[1], "Packaging listed", f"{pk:.0f}%" if pk is not None else "N/A", "Share of products")
    kpi(k[2], "Ingredients listed", f"{ing:.0f}%" if ing is not None else "N/A", "Share of products")
    kpi(k[3], "Average sugars / 100 g", f"{df['sugars_100g'].mean():.1f} g" if "sugars_100g" in df and df["sugars_100g"].notna().any() else "N/A", "Where reported")
    if "packaging" in df:
        pc = df["packaging"].dropna().astype(str).str.strip()
        pc = pc[pc.ne("")].value_counts().head(8)
        if len(pc):
            lines = [f"Most common packaging description: <b>{pc.index[0]}</b> ({pc.iloc[0]:,} products)."]
            chart, chart_title, chart_sub = theme.bar_chart(pc), "Common packaging descriptions", "Top 8 by product count"

st.write("")
left, right = st.columns([1.6, 1], gap="large")
with left, st.container(border=True):
    if chart is not None:
        section(chart_title, chart_sub)
        show_chart(chart)
    else:
        section("No chart available", "This dataset has no field that supports a summary chart.")
with right, st.container(border=True):
    section("Module readiness", "What the selected dataset can support")
    st.markdown("".join(f"<div class='row'><span>{n}</span>{tag(lbl, tone)}</div>" for n, v in engine.READINESS.items() for tone, lbl in [v[ds.kind]]), unsafe_allow_html=True)

st.write("")
a, b, c = st.columns(3, gap="medium")
with a, st.container(border=True):
    section("Operational insights", "Calculated from the data")
    theme.insights(lines) if lines else st.caption("No insights available for this dataset.")
with b, st.container(border=True):
    section("Inventory indicators")
    if ds.kind == "restaurant":
        r = s.tail(28)
        st.metric("Reference level, next day", f"{r.mean() + 1.645 * (r.std() if len(r) > 1 else 0):,.1f}", help="Recent 28-day mean + 1.645 standard deviations (about 95% service level). A planning signal, not an order quantity.")
        st.caption("Stock-on-hand data is not available, so no reorder advice is given.")
    elif ds.kind == "bimbo" and "Dev_uni_proxima" in df:
        rt = df.groupby("Producto_ID")["Dev_uni_proxima"].sum().nlargest(3)
        st.markdown("**Highest-returns products**")
        st.markdown("".join(f"<div class='row'><span>Product {int(i)}</span><span>{v:,.0f} units</span></div>" for i, v in rt.items()), unsafe_allow_html=True)
    else:
        theme.needs_data("No inventory data", ["Stock on hand", "Daily usage per ingredient"])
with c, st.container(border=True):
    section("Sustainability overview")
    if ds.kind == "off":
        cols = [x for x in ["fat_100g", "sugars_100g", "proteins_100g"] if x in df]
        for x in cols:
            st.markdown(f"<div class='row'><span>Average {x.replace('_100g', '')} / 100 g</span><span>{df[x].mean():.1f} g</span></div>", unsafe_allow_html=True)
        st.page_link("views/esg.py", label="Open ESG workspace", icon=":material/arrow_forward:")
    else:
        theme.needs_data("Product sustainability data not loaded", ["Switch to Open Food Facts products to see packaging and nutrition fields"])
        st.page_link("views/data_management.py", label="Change dataset", icon=":material/database:")

st.markdown("<h3 style='margin-top:26px'>Dataset library</h3>", unsafe_allow_html=True)
st.caption("Bundled files, shown separately. They are never combined.")
stats = data.library_stats()
for col, (key, spec) in zip(st.columns(3, gap="medium"), engine.SOURCES.items()):
    st_ = stats[key]
    body = f"{st_[0]:,} rows · {st_[1]} columns" if st_ else "File not found"
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{key}</div><div class='kpi-s' style='margin:0 0 8px'>{spec['desc']}</div>{tag(body, 'ok' if st_ else 'warn')}</div>", unsafe_allow_html=True)

st.markdown("<h3 style='margin-top:26px'>Analytics workspaces</h3>", unsafe_allow_html=True)
mods = [("trend", "Demand forecasting", "views/forecasting.py"), ("box", "Inventory intelligence", "views/inventory.py"), ("list", "Supplier & procurement", "views/suppliers.py"),
        ("leaf", "Food-waste intelligence", "views/waste.py"), ("users", "Customer intelligence", "views/customers.py"), ("map", "Logistics & delivery", "views/logistics.py"),
        ("globe", "ESG & sustainability", "views/esg.py")]
for i in range(0, 7, 4):
    for col, (ic, t, path) in zip(st.columns(4, gap="medium"), mods[i:i + 4]):
        with col:
            tone, lbl = engine.READINESS[t][ds.kind]
            st.markdown(f"<div class='mod'><div class='mod-i'>{icon(ic, 20)}</div><b>{t}</b>{tag(lbl, tone)}</div>", unsafe_allow_html=True)
            st.page_link(path, label="Open workspace", icon=":material/arrow_forward:")
