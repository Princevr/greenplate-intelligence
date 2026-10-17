import numpy as np
import pandas as pd
import streamlit as st

from core import data, theme
from core.theme import kpi, section, show_df

ds = data.get_dataset()
theme.page_header("Supplier & procurement intelligence", "Compare supplier offers using values you enter.", "list", ds.key)
st.warning("No supplied dataset contains verified supplier contracts, prices or lead-time performance. Every value below is your own scenario assumption.")
with st.form("supplier_form"):
    l, r = st.columns(2, gap="large")
    with l, st.container(border=True):
        st.markdown("**Supplier A**")
        pa = st.number_input("Price per unit (€)", 0.0, value=2.5, step=.1, key="pa")
        la = st.number_input("Lead time (days)", 0, value=3, key="la")
        ra = st.slider("Reliability (%)", 0, 100, 95, key="ra", help="Share of orders delivered complete and on time, as you estimate it.")
    with r, st.container(border=True):
        st.markdown("**Supplier B**")
        pb = st.number_input("Price per unit (€)", 0.0, value=2.35, step=.1, key="pb")
        lb = st.number_input("Lead time (days)", 0, value=5, key="lb")
        rb = st.slider("Reliability (%)", 0, 100, 88, key="rb", help="Share of orders delivered complete and on time, as you estimate it.")
    qty = st.number_input("Quantity", 1, value=100, step=10)
    go = st.form_submit_button("Compare suppliers")
if go:
    out = pd.DataFrame([{"Supplier": n, "Purchase cost (€)": p * qty, "Cost per reliably delivered unit (€)": p / (r / 100) if r else np.nan, "Lead time (days)": lt, "Reliability (%)": r}
                        for n, p, lt, r in [("A", pa, la, ra), ("B", pb, lb, rb)]])
    a, b = st.columns(2)
    kpi(a, "Lowest purchase cost", f"Supplier {out.loc[out['Purchase cost (€)'].idxmin(), 'Supplier']}", "Before delivery, quality and contract terms")
    kpi(b, "Highest reliability", f"Supplier {out.loc[out['Reliability (%)'].idxmax(), 'Supplier']}", "As entered")
    st.write("")
    show_df(out.round(2), hide_index=True)
    st.caption("Reliability-adjusted cost divides price by the entered reliability. It excludes delivery charges and other costs.")
