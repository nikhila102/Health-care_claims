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

## Retrieval evaluation

From the repository root run `python -m src.evaluate_retrieval`. Run metric checks with `python -m unittest discover -s tests -p test_retrieval_metrics.py -v`.

Six authored synthetic queries cover direct matches, a paraphrase, and unsupported questions. Relevant source IDs are explicit in `src/evaluate_retrieval.py`. Recall@2 and MRR@2 are averaged over four answerable queries; abstention rate is averaged over two unanswerable queries. Per-query retrieved and relevant IDs are included for inspection. This tiny developer-authored set is not an independent benchmark.

On November 4, 2026, the unchanged lexical retriever scored recall@2 = 0.75, MRR@2 = 0.75, and unanswerable abstention = 0.5 on this set. It missed the submission-tracking paraphrase and returned irrelevant passages for a dental-coverage question because of shared words. Three metric tests passed using hand-calculated ranking and abstention expectations. The full existing suite was not rerun. These results identify limitations rather than establishing healthcare readiness. 

Compare the original lexical baseline with an optional filter for common words and policy boilerplate by running `python -m src.evaluate_retrieval --compare`. Try the filter interactively with `python src/retrieve_demo.py --ignore-common "Does the policy cover dental implants?"`.

On the same six synthetic queries, the filter raised unsupported-question abstention from 1/2 to 2/2. Recall@2 and MRR@2 stayed at 0.75. The submission-tracking paraphrase still missed. The filter was developed using these cases, so the comparison is diagnostic. Eight retrieval and metric tests passed locally on November 5, 2026.

### Fresh synthetic challenge queries

Run `python -m src.evaluate_retrieval --compare --split challenge` from the repository root. The challenge split adds six answerable and four unsupported queries written after the filter was fixed. It includes paraphrases and unsupported requests with words shared by relevant policy passages.

| Mode | Recall@2 | MRR@2 | Unsupported questions correctly declined |
| --- | ---: | ---: | ---: |
| Baseline | 4/6 | 4/6 | 0/4 |
| Common-term filter | 3/6 | 3/6 | 1/4 |

The filter reduced some irrelevant matches but also lost one relevant match on these examples. Treat this small authored set as a diagnostic. Both split commands were checked for repeatable JSON, expected case counts, disjoint query text, and valid source labels.

### Configurable ranking cutoff

Use `python -m src.evaluate_retrieval --compare --split challenge --k 1` to evaluate only the first retrieved passage. The default cutoff remains 2. The evaluation API rejects non-integer, boolean, zero, and negative cutoffs before calling retrieval. The CLI requires a positive integer.

On November 7, 2026, all 15 repository unittest checks passed together in the available environment, including hand-calculated rank-sensitive metric checks and the notebook prediction regression check. The challenge comparison CLI also ran successfully with `--k 1`. Clean dependency installation and execution of the full notebook remain pending.

## Clean environment verification

Run `python scripts/verify_clean.py` from a checkout with Python and venv support. The script creates a temporary isolated environment, installs `requirements.txt`, runs `pip check`, executes all unittest checks, then runs the retrieval challenge comparison and synthetic regression demo. Failed commands stop verification and return a nonzero exit status. The temporary environment is cleaned up afterward. Package installation requires network access or a populated pip cache.

This complete command passed on November 8, 2026 with Python 3.12 on Linux, including all 15 tests and both evaluation entry points. Earlier notes about pending clean installation describe historical checks. Other Python versions and operating systems remain unverified, and full notebook execution remains pending.
