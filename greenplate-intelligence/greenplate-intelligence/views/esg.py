import streamlit as st

from core import data, theme
from core.theme import bar_chart, kpi, section, show_chart, show_df

ds = data.get_dataset()
theme.page_header("ESG & sustainability reporting", "Inspect product-level packaging and nutrition fields.", "globe", ds.key)

if ds.kind == "off":
    df = ds.df
    q = st.text_input("Filter products", placeholder="Search name, brand or category", help="Case-insensitive match on product_name, brands and categories.")
    if q:
        cols = [c for c in ["product_name", "brands", "categories"] if c in df]
        mask = False
        for c in cols:
            mask = mask | df[c].astype(str).str.contains(q, case=False, na=False, regex=False)
        df = df[mask] if cols else df
    data.empty_guard(df, "products")
    a, b, c = st.columns(3)
    kpi(a, "Products", f"{len(df):,}")
    kpi(b, "With packaging listed", f"{df['packaging'].notna().sum():,}" if "packaging" in df else "Unavailable")
    kpi(c, "With ingredients listed", f"{df['ingredients_text'].notna().sum():,}" if "ingredients_text" in df else "Unavailable")
    st.write("")
    if "packaging" in df:
        p = df["packaging"].dropna().astype(str).str.strip()
        p = p[p.ne("")].value_counts().head(15)
        if len(p):
            with st.container(border=True):
                section("Most common packaging descriptions")
                show_chart(bar_chart(p))
    cols = [c for c in ["product_name", "brands", "categories", "countries", "packaging", "ingredients_text", "fat_100g", "sugars_100g", "proteins_100g"] if c in df]
    with st.container(border=True):
        section("Product sample", "First 50 matching rows")
        show_df(df[cols].head(50))
    st.caption("This sample does not establish lifecycle impact, a company footprint or ESG-standard compliance. Missing packaging data is not evidence of sustainable packaging.")
else:
    theme.needs_data("This dataset has no product packaging or company sustainability fields", ["Select Open Food Facts products in Data Management"])
st.write("")
theme.needs_data("Needed for company ESG reporting", ["Electricity, heating and fuel use", "Purchased goods and packaging weights and materials", "Food waste by weight and disposal route", "Transport distance and fuel data", "Reporting boundaries, methods and source records"])
