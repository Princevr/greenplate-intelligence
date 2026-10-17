import streamlit as st

from core import data, theme
from core.theme import bar_chart, kpi, section, show_chart

ds = data.get_dataset()
theme.page_header("Logistics & delivery optimisation", "Check distribution signals and the data gaps for route planning.", "map", ds.key)
st.warning("None of the supplied datasets combines delivery coordinates, time windows, vehicle capacity and stop-level records, so real routes cannot be optimised.")

if ds.kind == "bimbo":
    df = ds.df
    a, b, c = st.columns(3)
    kpi(a, "Agencies", f"{df['Agencia_ID'].nunique():,}")
    kpi(b, "Route IDs", f"{df['Ruta_SAK'].nunique():,}" if "Ruta_SAK" in df else "Unavailable", "Column Ruta_SAK" if "Ruta_SAK" in df else "Column not in file")
    kpi(c, "Customer IDs", f"{df['Cliente_ID'].nunique():,}")
    st.write("")
    n = st.slider("Agencies to show", 5, 40, 20)
    with st.container(border=True):
        section("Top agencies by adjusted demand", "Identifiers are not geographic coordinates.")
        show_chart(bar_chart(df.groupby("Agencia_ID")["Demanda_uni_equil"].sum().nlargest(n)))
elif ds.kind == "restaurant":
    theme.needs_data("Daily category demand can estimate workload, not routes", ["It has no delivery locations or travel times"])
else:
    theme.needs_data("Product catalogue fields do not describe delivery operations", ["Select a dataset with agency or route identifiers"])
st.write("")
theme.needs_data("Needed for route optimisation", ["Delivery addresses or coordinates", "Orders and quantities per stop", "Delivery time windows", "Vehicle capacity and operating hours", "Travel-time matrix and depot location"])
