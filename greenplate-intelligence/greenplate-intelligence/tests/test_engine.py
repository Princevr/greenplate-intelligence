"""Run: python tests/test_engine.py   (needs pandas, numpy, scikit-learn only)"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd

from core import engine as e

rng = np.random.default_rng(0)
days = pd.date_range("2023-01-01", periods=200)
rest = pd.DataFrame({"DEMAND_DATE": days.strftime("%d.%m.%Y"), "TOTAL": 100 + 20 * (days.dayofweek >= 4) + rng.normal(0, 5, 200),
                     "STEAK": rng.integers(5, 30, 200)})
bimbo = pd.DataFrame({"Semana": rng.integers(3, 10, 500), "Producto_ID": rng.integers(1, 40, 500), "Cliente_ID": rng.integers(1, 100, 500),
                      "Agencia_ID": rng.integers(1, 10, 500), "Demanda_uni_equil": rng.integers(0, 50, 500)})
off = pd.DataFrame({"product_name": ["a", "b"], "packaging": ["glass", None], "sugars_100g": ["3.5", "x"]})


def expect_error(fn):
    try:
        fn()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


for sep in [",", ";", "\t"]:  # delimiter auto-detection round trip
    df, used = e.read_csv_bytes(rest.to_csv(index=False, sep=sep).encode())
    assert used == sep and df.shape == rest.shape, sep
expect_error(lambda: e.read_csv_bytes(rest.to_csv(index=False, sep=";").encode(), sep=","))  # wrong manual separator
expect_error(lambda: e.read_csv_bytes(b"   "))  # empty file
assert any(l == "error" for l, _ in e.validate("restaurant", bimbo))
assert any(l == "error" for l, _ in e.validate("bimbo", rest))
d, t = e.prepare("restaurant", rest)
assert t == ["TOTAL", "STEAK"] and d.DEMAND_DATE.is_monotonic_increasing
assert e.prepare("bimbo", bimbo)[1] == ["Demanda_uni_equil"]
assert e.prepare("off", off)[0].sugars_100g.isna().sum() == 1
expect_error(lambda: e.prepare("restaurant", rest.drop(columns="DEMAND_DATE")))
res = e.run_forecast(e.daily_series(d, "TOTAL"), 14)
assert res and len(res["forecast"]) == 14 and (res["forecast"].lo <= res["forecast"].hi).all()
print("forecast MAE", round(res["mae"], 2), "| same-weekday baseline", round(res["base"], 2))
assert e.run_forecast(pd.Series(range(20), index=pd.date_range("2024-01-01", periods=20))) is None
assert len(e.quality_report(d)) == d.shape[1]
print("ALL ENGINE TESTS PASSED")
