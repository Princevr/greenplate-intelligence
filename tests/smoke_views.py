"""Headless smoke test: runs every view with a lightweight fake `streamlit` and synthetic CSVs.

It checks that pages execute without exceptions for each dataset kind (including a missing-file
case). It does NOT render anything, so visual QA must still be done in a real browser.
Run:  python tests/smoke_views.py   (needs pandas, numpy, scikit-learn; streamlit/altair are stubbed)
"""
import pathlib
import runpy
import sys
import tempfile
import types
from unittest.mock import MagicMock

import numpy as np
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Stop(Exception):
    pass


class _Box:
    """Stands in for a column / container / tab: usable as a context manager and as an st-like object."""
    def __init__(self, st): self._st = st
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def __getattr__(self, name): return getattr(self._st, name)


class FakeSt(types.ModuleType):
    def __init__(self):
        super().__init__("streamlit")
        self.session_state = {}
        self.calls = []

    def _ctx(self):
        return _Box(self)

    def container(self, *a, **k): return self._ctx()
    def form(self, *a, **k): return self._ctx()
    def expander(self, *a, **k): return self._ctx()
    def spinner(self, *a, **k): return self._ctx()
    def columns(self, spec, **k): return [self._ctx() for _ in range(spec if isinstance(spec, int) else len(spec))]
    def tabs(self, labels): return [self._ctx() for _ in labels]
    def stop(self): raise Stop()
    def rerun(self): raise Stop()
    def selectbox(self, label, options, index=0, **k): return list(options)[index]
    def multiselect(self, label, options, default=None, **k): return list(default or [])
    def slider(self, label, mn=0, mx=100, value=None, **k): return value if value is not None else mn
    def number_input(self, label, min_value=None, max_value=None, value=None, **k): return value if value is not None else (min_value or 0)
    def date_input(self, label, value=None, **k): return value
    def text_input(self, *a, **k): return ""
    def file_uploader(self, *a, **k): return None
    def button(self, *a, **k): return False
    def form_submit_button(self, *a, **k): return False
    def cache_data(self, *a, **k): return a[0] if a and callable(a[0]) else (lambda f: f)
    def __getattr__(self, name):  # markdown, error, dataframe, metric, page_link, ...
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: self.calls.append((name, a))


def make_data(folder):
    rng = np.random.default_rng(1)
    d = pd.date_range("2023-01-01", periods=240)
    pd.DataFrame({"DEMAND_DATE": d.strftime("%d.%m.%Y"), "TOTAL": 100 + 15 * (d.dayofweek >= 4) + rng.normal(0, 4, 240), "STEAK": rng.integers(3, 30, 240)}) \
        .to_csv(folder / "data_preprocessed (1)(1).csv", sep=";", index=False)
    pd.DataFrame({"Semana": rng.integers(3, 10, 800), "Producto_ID": rng.integers(1, 40, 800), "Cliente_ID": rng.integers(1, 120, 800), "Agencia_ID": rng.integers(1, 12, 800),
                  "Ruta_SAK": rng.integers(1, 30, 800), "Demanda_uni_equil": rng.integers(0, 60, 800), "Venta_uni_hoy": rng.integers(0, 70, 800),
                  "Dev_uni_proxima": rng.integers(0, 8, 800)}).to_csv(folder / "train_sample_30k.csv", index=False)
    pd.DataFrame({"product_name": ["Oat milk", "Rice", "Jam"], "brands": ["A", "B", "C"], "categories": ["x", "y", "z"], "packaging": ["glass", None, "plastic, glass"],
                  "ingredients_text": ["oats", "rice", None], "sugars_100g": [3.5, 0.1, 55], "fat_100g": [1.5, 0.3, 0.1], "proteins_100g": [1, 7, 0.4]}) \
        .to_csv(folder / "open_food_facts_sample(1).csv", index=False)


def run_all(folder, label, expect_stop_ok=False):
    fake = FakeSt()
    sys.modules["streamlit"] = fake
    sys.modules["altair"] = MagicMock()
    for m in [m for m in sys.modules if m.startswith("core")]:
        del sys.modules[m]
    sys.path.insert(0, str(ROOT))
    from core import data, engine
    data.ROOT = folder
    data.Path.cwd = classmethod(lambda cls: folder)  # keep lookups inside the temp folder
    failures = 0
    for source in engine.SOURCES:
        for view in sorted((ROOT / "views").glob("*.py")):
            fake.session_state.clear()
            fake.session_state["source"] = source
            try:
                runpy.run_path(str(view), run_name="__view__")
                status = "ok"
            except Stop:
                status = "stopped (handled)" if expect_stop_ok else "STOPPED UNEXPECTEDLY"
                failures += not expect_stop_ok
            except Exception as e:  # noqa: BLE001
                status = f"ERROR {type(e).__name__}: {e}"
                failures += 1
            if status not in ("ok",) or "-v" in sys.argv:
                print(f"[{label}] {source:32s} {view.name:22s} {status}")
    return failures


with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    make_data(tmp)
    bad = run_all(tmp, "data present")
    empty = pathlib.Path(tempfile.mkdtemp())
    bad += run_all(empty, "files missing", expect_stop_ok=True)
print("SMOKE TEST FAILURES:", bad)
sys.exit(1 if bad else 0)
