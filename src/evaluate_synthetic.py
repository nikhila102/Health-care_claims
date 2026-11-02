"""Reproducible synthetic-only regression evaluation. No patient data or services."""
import argparse
import json
from pathlib import Path
import platform
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

def evaluate(seed=42):
    rng = np.random.default_rng(seed)
    X = pd.DataFrame({
        "age": rng.integers(18, 80, 500),
        "bmi": rng.uniform(18, 40, 500),
        "smoker_yes": rng.integers(0, 2, 500),
    })
    # Deliberately simple invented relationship; not a medical cost model.
    y = 100*X.age + 200*X.bmi + 1000*X.smoker_yes + rng.normal(0, 300, 500)
    train, test = train_test_split(np.arange(len(X)), test_size=0.2, random_state=seed)
    metrics = {}
    for name, model in [("mean_baseline", DummyRegressor()), ("linear_regression", LinearRegression())]:
        model.fit(X.iloc[train], y.iloc[train])
        predictions = model.predict(X.iloc[test])
        metrics[name] = {
            "mae": float(mean_absolute_error(y.iloc[test], predictions)),
            "rmse": float(np.sqrt(mean_squared_error(y.iloc[test], predictions))),
        }
    return {
        "data": "generated synthetic demonstration; no real-world validity",
        "seed": seed, "train_rows": len(train), "test_rows": len(test),
        "train_indices": train.tolist(), "test_indices": test.tolist(),
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "sklearn": sklearn.__version__},
        "metrics": metrics,
    }

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42, help="Nonnegative random seed")
    parser.add_argument("--output", type=Path, help="Save JSON to a new file; refuses overwrites")
    args = parser.parse_args(argv)
    if args.seed < 0:
        parser.error("--seed must be nonnegative")
    report = json.dumps(evaluate(args.seed), indent=2, allow_nan=False) + "\n"
    if args.output:
        # Exclusive creation avoids silently replacing a previous experiment.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(report)
    else:
        print(report, end="")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
