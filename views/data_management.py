import streamlit as st

from core import data, engine, theme
from core.theme import kpi, section, show_df, tag

keys = list(engine.SOURCES)
ds, err = data.try_get_dataset()
theme.page_header("Data management", "Choose the active dataset, upload a replacement CSV and check data quality.", "db", data.active_source())


def _pick():
    st.session_state["source"] = st.session_state["_source_widget"]


tab1, tab2, tab3 = st.tabs(["Dataset", "Preview", "Quality"])

with tab1:
    l, r = st.columns([1, 1], gap="large")
    with l, st.container(border=True):
        section("Active dataset", "Every module reads from this dataset. Datasets are never combined.")
        st.selectbox("Dataset", keys, index=keys.index(data.active_source()), key="_source_widget", on_change=_pick)
        spec = engine.SOURCES[data.active_source()]
        st.caption(spec["desc"])
        if err:
            st.error(err)
        else:
            a, b = st.columns(2)
            kpi(a, "Rows", f"{len(ds.df):,}", ds.origin)
            kpi(b, "Columns", f"{ds.df.shape[1]:,}", f"Separator: {'tab' if ds.sep == chr(9) else ds.sep}")
            for lvl, msg in engine.validate(ds.kind, ds.df):
                (st.warning if lvl == "warning" else st.error)(msg)
        if data.uploads().get(data.active_source()):
            if st.button("Revert to bundled file"):
                data.uploads().pop(data.active_source(), None)
                st.rerun()
    with r, st.container(border=True):
        section("Upload a replacement CSV", "Replaces the bundled file for the selected dataset in this session only.")
        up = st.file_uploader("CSV file", type=["csv"], label_visibility="collapsed")
        sep_label = st.selectbox("Separator", list(engine.SEPARATORS), help="Auto-detect checks the header line for comma, semicolon or tab.")
        if up is not None:
            raw_bytes = up.getvalue()
            try:
                raw, used = engine.read_csv_bytes(raw_bytes, sep=engine.SEPARATORS[sep_label], default_sep=spec["sep"])
                issues = engine.validate(spec["kind"], raw)
                st.markdown(f"Detected **{len(raw):,} rows**, **{raw.shape[1]} columns**, separator **{'tab' if used == chr(9) else used}**.")
                for lvl, msg in issues:
                    (st.warning if lvl == "warning" else st.error)(msg)
                if not any(l == "error" for l, _ in issues):
                    if st.button("Use this file", type="primary"):
                        data.uploads()[data.active_source()] = dict(name=up.name, bytes=raw_bytes, sep=engine.SEPARATORS[sep_label])
                        st.rerun()
                else:
                    st.caption("This file does not match the selected dataset. Choose the matching dataset above or fix the columns.")
            except ValueError as e:
                st.error(str(e))

with tab2:
    if err:
        st.info("Fix the dataset above to see a preview.")
    else:
        n = st.slider("Rows to show", 10, 200, 25, step=5)
        show_df(ds.df.head(n))

with tab3:
    if err:
        st.info("Fix the dataset above to see quality indicators.")
    else:
        df = ds.df
        comp = 100 * (1 - df.isna().sum().sum() / max(1, df.size))
        dups = int(df.duplicated().sum())
        sparse = int((df.isna().mean() > .5).sum())
        k = st.columns(4)
        kpi(k[0], "Completeness", f"{comp:.1f}%", "Non-missing cells")
        kpi(k[1], "Duplicate rows", f"{dups:,}", f"{100 * dups / max(1, len(df)):.1f}% of rows")
        kpi(k[2], "Mostly-empty columns", f"{sparse}", "More than 50% missing")
        kpi(k[3], "Numeric columns", f"{df.select_dtypes('number').shape[1]}", f"of {df.shape[1]}")
        st.write("")
        rep = engine.quality_report(df)
        show_df(rep, height=420, hide_index=True)
        st.download_button("Download quality report", rep.to_csv(index=False).encode(), "greenplate_data_quality_report.csv", "text/csv")
