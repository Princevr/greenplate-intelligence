"""Streamlit-facing data layer: active dataset, cached loading, shared filters."""
from pathlib import Path
from types import SimpleNamespace

import streamlit as st

from . import engine
from .theme import icon

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = next(iter(engine.SOURCES))


def find_file(name):
    for base in (ROOT, Path.cwd()):
        p = base / name
        if p.exists():
            return p
    return None


@st.cache_data(show_spinner="Reading file…")
def _load_path(path_str, mtime, default_sep):
    return engine.read_csv_bytes(Path(path_str).read_bytes(), default_sep=default_sep)


def active_source():
    return st.session_state.get("source", DEFAULT_SOURCE)


def uploads():
    return st.session_state.setdefault("uploads", {})


def try_get_dataset():
    """Return (dataset, None) or (None, error_message). Never stops the page."""
    key = active_source()
    spec = engine.SOURCES[key]
    up = uploads().get(key)
    try:
        if up:
            raw, sep = engine.read_csv_bytes(up["bytes"], sep=up.get("sep"), default_sep=spec["sep"])
            origin = f"Uploaded file: {up['name']}"
        else:
            p = find_file(spec["file"])
            if p is None:
                return None, f"The file \u201c{spec['file']}\u201d was not found next to app.py. Add it to the project folder or upload a replacement."
            raw, sep = _load_path(str(p), p.stat().st_mtime, spec["sep"])
            origin = spec["file"]
        df, targets = engine.prepare(spec["kind"], raw)
    except Exception as e:
        return None, str(e)
    return SimpleNamespace(key=key, kind=spec["kind"], df=df, targets=targets, desc=spec["desc"], origin=origin, sep=sep), None


def get_dataset():
    """Load the active dataset or stop the page with a helpful message."""
    ds, err = try_get_dataset()
    if err:
        st.error(f"Could not load \u201c{active_source()}\u201d: {err}")
        st.page_link("views/data_management.py", label="Fix this in Data Management", icon=":material/database:")
        st.stop()
    return ds


def library_stats():
    """Row/column counts of the bundled files (each kept separate)."""
    out = {}
    for key, spec in engine.SOURCES.items():
        p = find_file(spec["file"])
        if p is None:
            out[key] = None
            continue
        try:
            raw, _ = _load_path(str(p), p.stat().st_mtime, spec["sep"])
            out[key] = (len(raw), raw.shape[1])
        except Exception:
            out[key] = None
    return out


def choose_target(ds, key):
    if not ds.targets:
        st.warning("No recognised demand measure is available in this dataset.")
        return None
    return st.selectbox("Demand measure", ds.targets, index=ds.targets.index("TOTAL") if "TOTAL" in ds.targets else 0, key=key)


def date_filter(df, key):
    """Date-range filter for restaurant data. Returns the filtered frame."""
    lo, hi = df.DEMAND_DATE.min().date(), df.DEMAND_DATE.max().date()
    r = st.date_input("Date range", (lo, hi), min_value=lo, max_value=hi, key=key)
    if isinstance(r, (tuple, list)) and len(r) == 2:
        return df[(df.DEMAND_DATE.dt.date >= r[0]) & (df.DEMAND_DATE.dt.date <= r[1])]
    return df


def week_filter(df, key):
    weeks = sorted(df["Semana"].dropna().unique().tolist())
    chosen = st.multiselect("Weeks (Semana)", weeks, default=weeks, key=key)
    return df[df["Semana"].isin(chosen)] if chosen else df.iloc[0:0]


def empty_guard(df, what="data"):
    if df.empty:
        st.info(f"No {what} match the current filters. Widen the selection to continue.")
        st.stop()
