# Healthcare cost regression

An educational medical-cost regression notebook. This repository currently contains exploratory analysis and a linear regression using age, BMI, and smoking status. It does not yet implement claims adjudication, RAG, agents, or a deployed API. The API, Docker, model, and training-script scaffolding is unfinished.

## Setup and checks

Use Python 3.11 or newer in a virtual environment (dependency compatibility varies by platform):

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The test uses generated synthetic values, fits a regression with a negative intercept, and checks that the notebook helper matches the estimator's prediction. It guards against subtracting the intercept. The helper now delegates to `predict()` with named features.

## Notebook status

`src/medical-cost-personal-datasets.ipynb` retains its existing analysis. Its input path (`../input/insurance1/insurance.csv`) is environment-specific and must be configured before execution. The provenance and license of the existing CSV and notebook have not been established in this repository; verify them before reuse or redistribution. Existing material is preserved without asserting authorship or changing its license.

Saved outputs were cleared after the prediction fix. The full notebook has not been rerun; no validated predictive-performance claim is made. Its fit and score use the same data, so that score is not held-out generalization performance.

## Next milestone

Establish data provenance for the existing CSV before using it for held-out evaluation. The separate synthetic evaluation below already demonstrates a train/test split and baseline comparison. Use synthetic data for integration tests. This educational project is not suitable for clinical, coverage, or pricing decisions.

## Runnable synthetic evaluation

```bash
python src/evaluate_synthetic.py > synthetic-evaluation.json
python -m unittest discover -s tests -v
```

This separate demonstration generates 500 synthetic rows with a seeded, invented linear relationship and noise. It trains on 400 rows, evaluates on 100 disjoint held-out rows, and compares linear regression with a training-mean baseline using MAE and RMSE. The JSON includes the seed, split indices, and Python/library versions for auditing. The test checks repeatability, split isolation, and baseline improvement on this deliberately simple synthetic problem.

This script does not read the existing CSV or execute the notebook. Synthetic results demonstrate the evaluation workflow only; they do not establish real-world healthcare accuracy. Exact dependency versions are recorded in each output. `requirements.txt` pins the tested dependency snapshot, including transitive dependencies; it is not a hash-locked or platform-independent environment. A clean installation of these pins has not yet been verified.

## Validation status

Both unittest checks passed together in the available development environment on November 1, 2026. This checks the notebook prediction helper and the synthetic evaluation, not execution of the full notebook. The dependency pins reflect that environment; clean-environment installation and cross-platform compatibility remain to be checked. No external datasets, credentials, or paid services are required for these tests.

## Experiment CLI

Run a repeatable experiment with a chosen seed and save its report:

```bash
python src/evaluate_synthetic.py --seed 7 --output experiment-seed7.json
```

`--seed` defaults to 42 and must be nonnegative. Without `--output`, JSON is printed to stdout. Output files are created exclusively: an existing file raises an error and is preserved. Choose another filename for each experiment. The destination directory must already exist. Different seeds change both synthetic data and the split; comparing seeds measures this toy simulation's sensitivity, not real-world model reliability.

Three CLI tests passed locally on November 2, 2026: JSON/seed handling, negative-seed rejection, and protection of an existing output file. The full test suite and a clean dependency installation were not rerun in that check.

## Offline retrieval foundation

```bash
python src/retrieve_demo.py "appeal denial"
python -m unittest discover -s tests -p test_retrieval.py -v
```

The retrieval demo uses only Python's standard library and three explicitly invented policy passages embedded in the source. It ranks term-frequency vectors by cosine similarity and returns source IDs, text, and scores; zero-overlap queries return an empty list. Stable source IDs provide a foundation for future answer citations. These are fictional examples, not insurance guidance or employer documents.

This is a lexical retrieval baseline, not a complete RAG system: it has no LLM, embeddings, clinical knowledge, or coverage decision logic. Positive word overlap alone does not establish relevance. Four tests and a CLI smoke check passed locally on November 3, 2026; the three known-query examples are smoke fixtures, not an independent retrieval benchmark. The existing regression suite and clean dependency installation were not rerun for this addition. Next: add a separate retrieval evaluation set and measure ranking/abstention before integrating generation.
