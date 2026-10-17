import streamlit as st

st.set_page_config(page_title="GreenPlate Intelligence", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

from core import data, theme  # noqa: E402  (must follow set_page_config)

theme.inject()
st.logo("assets/logo.svg", size="large")

pages = {
    "Overview": [
        st.Page("views/landing.py", title="Home", icon=":material/home:", default=True),
        st.Page("views/dashboard.py", title="Executive dashboard", icon=":material/space_dashboard:"),
    ],
    "Analytics": [
        st.Page("views/forecasting.py", title="Demand forecasting", icon=":material/trending_up:"),
        st.Page("views/inventory.py", title="Inventory", icon=":material/inventory_2:"),
        st.Page("views/suppliers.py", title="Suppliers & procurement", icon=":material/receipt_long:"),
        st.Page("views/waste.py", title="Food waste", icon=":material/recycling:"),
        st.Page("views/customers.py", title="Customers", icon=":material/groups:"),
        st.Page("views/logistics.py", title="Logistics & delivery", icon=":material/local_shipping:"),
        st.Page("views/esg.py", title="ESG & sustainability", icon=":material/eco:"),
    ],
    "Workspace": [
        st.Page("views/data_management.py", title="Data management", icon=":material/database:"),
    ],
}
nav = st.navigation(pages)

with st.sidebar:
    up = data.uploads().get(data.active_source())
    st.markdown(f"<div class='side-card'><b>Active dataset</b><span>{data.active_source()}{' · uploaded file' if up else ''}</span></div>", unsafe_allow_html=True)

nav.run()
