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

## Runnable synthetic evaluation

```bash
python src/evaluate_synthetic.py > synthetic-evaluation.json
python -m unittest discover -s tests -v
```

This separate demonstration generates 500 synthetic rows with a seeded, invented linear relationship and noise. It trains on 400 rows, evaluates on 100 disjoint held-out rows, and compares linear regression with a training-mean baseline using MAE and RMSE. The JSON includes the seed, split indices, and Python/library versions for auditing. The test checks repeatability, split isolation, and baseline improvement on this deliberately simple synthetic problem.

This script does not read the existing CSV or execute the notebook. Synthetic results demonstrate the evaluation workflow only; they do not establish real-world healthcare accuracy. Exact dependency versions are recorded in each output but are not yet locked for cross-environment reproducibility.
