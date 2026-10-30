# Healthcare cost regression

An educational medical-cost regression notebook. This repository currently contains exploratory analysis and a linear regression using age, BMI, and smoking status. It does not yet implement claims adjudication, RAG, agents, or a deployed API. The API, Docker, model, and training-script scaffolding is unfinished.

## Setup and checks

Use Python 3.10 or newer in a virtual environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install pandas numpy scikit-learn
python -m unittest discover -s tests -v
```

The test uses generated synthetic values, fits a regression with a negative intercept, and checks that the notebook helper matches the estimator's prediction. It guards against subtracting the intercept. The helper now delegates to `predict()` with named features.

## Notebook status

`src/medical-cost-personal-datasets.ipynb` retains its existing analysis. Its input path (`../input/insurance1/insurance.csv`) is environment-specific and must be configured before execution. The provenance and license of the existing CSV and notebook have not been established in this repository; verify them before reuse or redistribution. Existing material is preserved without asserting authorship or changing its license.

Saved outputs were cleared after the prediction fix. The full notebook has not been rerun; no validated predictive-performance claim is made. Its fit and score use the same data, so that score is not held-out generalization performance.

## Next milestone

Establish data provenance, add a reproducible train/test split and baseline comparison, and report held-out MAE/RMSE with dataset and environment details. Use synthetic data for integration tests. This educational project is not suitable for clinical, coverage, or pricing decisions.
