"""Regression test for the notebook prediction helper; uses synthetic data only."""
import json
from pathlib import Path
import unittest
import pandas as pd
from sklearn.linear_model import LinearRegression

class PredictionTests(unittest.TestCase):
    def test_helper_matches_estimator_with_negative_intercept(self):
        notebook = json.loads((Path(__file__).resolve().parents[1] / "src/medical-cost-personal-datasets.ipynb").read_text())
        source = next("".join(c["source"]) for c in notebook["cells"] if "def calc_insurance" in "".join(c.get("source", [])))
        X = pd.DataFrame([[20,20,0],[30,20,0],[20,30,0],[20,20,1],[30,30,1]], columns=["age","bmi","smoker_yes"])
        y = 100*X.age + 200*X.bmi + 1000*X.smoker_yes - 5000
        model = LinearRegression().fit(X,y)
        self.assertLess(model.intercept_, 0)
        namespace = {"pd": pd, "X": X, "linreg": model}
        exec(source, namespace)
        expected = model.predict(pd.DataFrame([[36,24,0]], columns=X.columns))[0]
        self.assertAlmostEqual(namespace["calc_insurance"](36,24,0), expected)
        self.assertAlmostEqual(expected, 3400)

if __name__ == "__main__":
    unittest.main()
