# Modernization Roadmap

This document is a practical audit and staged execution plan for the `modernize-analysis-layer` branch of `mmollomb/racing_data`.

It is intentionally focused on sequencing future work so that larger, more material Codex tasks can be completed with less prompt churn and less accidental rework.

The branch state described here was verified locally with:

```cmd
.venv\Scripts\activate
python -m pytest
```

and currently passes `48` modern tests on this branch.

## Status update

The roadmap has partly been executed since this document was first written.

Current verified branch state now includes:

- `python -m pytest` passes `48` modern tests
- `examples/build_feature_table.py` generates a deterministic local feature table with `race_key`
- `examples/train_baseline_model.py` generates a race-aware baseline report grouped by `race_key`
- the bundled sample input now represents one same-race field with six runners
- the local report includes leakage exclusion, grouped rankings, and a small evaluation summary when current-race results are present

The remaining roadmap stages beyond the current MVP still apply for future work, especially batch input support, schema versioning, CI automation, and any eventual adapter decision.

## 1. Current project audit

### Repository and branch status

- Upstream repository: `predictive-punter/racing_data` (`origin`)
- Active fork: `mmollomb/racing_data` (`personal`)
- Active working branch: `modernize-analysis-layer`
- Branch purpose: keep the original racing domain model intact where possible, while isolating and modernizing the Windows-safe analysis/entity layer before attempting deeper ingestion or infrastructure work

### What currently exists

- `modern_tests/`
  Purpose: a Windows-safe modern test suite that exercises the analysis/entity layer without relying on the legacy scraper/database stack.

- `pyproject.toml`
  Purpose: modern packaging metadata plus pytest configuration so `python -m pytest` runs only `modern_tests` by default.

- `examples/build_feature_table.py`
  Purpose: a local-file feature-table generator that constructs in-memory `Meet`, `Race`, `Horse`, `Performance`, `PerformanceList`, and `Runner` objects, then emits a model-style feature CSV without using the legacy `Provider`, scraper, database, or ingestion path.

- `data/examples/sample_runner_history.csv`
  Purpose: example input data representing runner/race/performance history rows for multiple runners.

- `data/examples/runner_features.csv`
  Purpose: generated example output showing the current feature schema emitted by the local feature-table generator.

- `README.rst`
  Purpose: still contains the original package usage documentation, but now also includes modernization notes describing the branch focus, the modern test entry point, and the local feature-table example.

- `MODERNIZATION_NOTES.md`
  Purpose: branch-local status notes for the current modernization baseline, including what has been proven to work, which edge cases are covered by modern tests, and which package-level cleanups were made because tests exposed brittle behavior.

- `.travis.yml` and `tox.ini`
  Purpose: legacy CI/test automation configuration from the original project. These files still exist, but they target the old dependency stack and older Python versions, so they are not currently the verified automation path for the modernization branch.

### Known legacy areas intentionally avoided for now

- `racing_data.Provider`
- scraper integration
- database integration
- ingestion workflows
- `cache_requests`
- `redislite`
- the original `tests/` suite
- the older tox/Travis workflow tied to the original dependency model

### What has been modernized so far

- Modern packaging/test entrypoint through `pyproject.toml`
- Windows-safe `modern_tests` coverage for the core analysis/entity layer
- Small package-code cleanups only where tests exposed real issues
- Verified behavior for `Entity`, `Performance`, `Runner`, and `PerformanceList` analysis properties
- A reusable local-file feature-table example with:
  - default CLI paths
  - explicit `--input` / `--output` support
  - multiple-runner sample input
  - richer model-ready feature columns generated from existing in-memory analysis properties

### What has not yet been modernized

- A replacement for the legacy Provider/scraper/database stack
- Any real external racing-data adapter
- Input schema validation for the CSV feature generator
- Batch input processing
- A canonical feature schema contract
- Model training workflows
- Evaluation/backtesting workflows
- Export workflows beyond CSV
- A verified modern CI pipeline
- Packaging/documentation for normal end-user operation

## 2. Current working capabilities

The repo can currently do the following:

- instantiate `racing_data` entity objects entirely in memory
- calculate `Runner`, `Horse`, `Performance`, and `PerformanceList` analysis properties without the legacy scraper/database path
- run Windows-safe modern tests via `python -m pytest`
- generate a local model-style feature table from CSV input
- run the local feature generator with default paths:
  - `python examples\build_feature_table.py`
- run the local feature generator with explicit paths:
  - `python examples\build_feature_table.py --input data\examples\sample_runner_history.csv --output data\examples\runner_features.csv`
- produce a feature table with multiple runner rows from a local sample CSV
- emit richer model-ready columns such as:
  - career rates and totals
  - recent-form aggregates
  - track/distance/jockey-conditioned win percentages
  - safe optional values from current and previous performances

## 3. Current limitations

- This is not yet a full ingestion system.
- There is no production scraper/database replacement yet.
- There is no real external racing-data adapter yet.
- There is no dedicated schema-validation layer for CSV inputs yet.
- There is no repeatable batch production workflow yet.
- There is no model training/evaluation workflow yet.
- There is no packaged CLI distribution for normal user installation.
- There is no verified modern CI workflow for the current branch’s `.venv` + `pyproject.toml` + `modern_tests` path.
- Legacy tests still depend on the outdated Provider/scraper/database stack and problematic Windows dependencies.
- The example generator is still sample-data centric and not yet a hardened production feature pipeline.
- Output schema exists in practice, but it is not yet documented as a canonical versioned contract.
- Real-data source, licensing, and operational concerns have not yet been addressed.

## 4. Sequential modernization stages

### Stage 1: Stabilize analysis-layer baseline

Stage name:
Stage 1: Stabilize analysis-layer baseline

Purpose:
Lock down the current Windows-safe entity/analysis behavior so future tasks do not accidentally regress the proven baseline.

Material deliverable:
A stable branch where `python -m pytest` runs `modern_tests` only, branch notes reflect the current passing state, and the core analysis properties are documented as the supported baseline.

Files likely changed:
`modern_tests/*`, `pyproject.toml`, `README.rst`, `MODERNIZATION_NOTES.md`, small targeted package files only if tests expose real issues.

Checks to build into the stage:
- `git status`
- activate `.venv`
- `python -m pytest`
- targeted diffs only

Common hurdles:
Legacy tests running by accident, wrong interpreter, and accidental changes outside the analysis layer.

How to avoid wasting prompts:
Require file allow-lists and insist on package-code edits only when a failing test proves they are necessary.

Definition of done:
The analysis/entity layer is documented, tested, and stable on Windows through the modern suite.

What final looks like:
Future tasks can safely assume the baseline works and do not need to rediscover how to run or verify it.

### Stage 2: Turn local feature example into a reusable feature-table generator

Stage name:
Stage 2: Turn local feature example into a reusable feature-table generator

Purpose:
Move the example from a single fixed demo toward a practical local tool that transforms runner-history CSV data into model-ready feature tables.

Material deliverable:
A script that supports default and explicit input/output paths, multiple runners, and richer feature columns using existing analysis properties.

Files likely changed:
`examples/build_feature_table.py`, `data/examples/sample_runner_history.csv`, `data/examples/runner_features.csv`, `README.rst`.

Checks to build into the stage:
- `python examples\build_feature_table.py`
- `python examples\build_feature_table.py --input ... --output ...`
- `python -m pytest`

Common hurdles:
Hard-coded paths, fragile CSV assumptions, and example-only changes accidentally leaking into package code.

How to avoid wasting prompts:
Keep changes confined to the example script and generated example data until the generator’s local contract is stable.

Definition of done:
The local feature generator can be run repeatedly with predictable CSV input/output behavior.

What final looks like:
The example script is usable as the seed of a small feature-engineering pipeline rather than a one-off demo.

### Stage 3: Add input schema validation and clear errors

Stage name:
Stage 3: Add input schema validation and clear errors

Purpose:
Make invalid input fail clearly and early rather than producing confusing runtime errors or silently bad outputs.

Material deliverable:
Validation for required columns, empty files, malformed dates, and bad numeric values, with readable error messages.

Files likely changed:
`examples/build_feature_table.py`, new example-focused tests if added later, `README.rst` if CLI error behavior needs documenting.

Checks to build into the stage:
- valid sample run
- malformed header run
- missing-column run
- empty-file run
- `python -m pytest`

Common hurdles:
Validation rules growing ad hoc, unclear required-column sets, and platform-specific path issues.

How to avoid wasting prompts:
Define the required CSV contract before coding and add explicit failure examples in the task prompt.

Definition of done:
Bad input is rejected with deterministic, human-readable errors and valid input still works unchanged.

What final looks like:
The feature generator becomes safe enough for repeated use by someone who did not author the script.

### Stage 4: Expand model-ready feature columns

Stage name:
Stage 4: Expand model-ready feature columns

Purpose:
Expose more of the existing analysis-layer signal in the generated feature table without changing package behavior.

Material deliverable:
A larger, documented output schema including career, recent-form, contextual, and current-run features.

Files likely changed:
`examples/build_feature_table.py`, `data/examples/runner_features.csv`, `README.rst` if output description needs updating.

Checks to build into the stage:
- regenerate output
- inspect headers
- `python -m pytest`

Common hurdles:
Inconsistent feature naming, leakage-prone columns, and optional values causing crashes.

How to avoid wasting prompts:
Use only existing `Runner`, `Performance`, and `PerformanceList` properties first; postpone invented formulas until there is a schema review.

Definition of done:
The generated CSV contains materially richer model-ready columns with blanks for unavailable values.

What final looks like:
The local feature table is meaningfully useful as a modelling input dataset.

### Stage 5: Add repeatable tests for the local feature generator

Stage name:
Stage 5: Add repeatable tests for the local feature generator

Purpose:
Stop the example generator from becoming a moving target by locking in its CLI behavior, required schema, and representative outputs.

Material deliverable:
Focused tests for generator execution, headers, row counts, and failure cases.

Files likely changed:
New `modern_tests` module(s), possibly small helper fixtures, maybe `README.rst` if command expectations need clarification.

Checks to build into the stage:
- `python -m pytest`
- direct script runs
- output header assertions

Common hurdles:
Tests that are too brittle on formatting or platform-specific path rendering.

How to avoid wasting prompts:
Assert stable contract elements like headers and row counts, not incidental formatting details.

Definition of done:
The generator’s behavior is covered by automated tests and future changes are cheaper to verify.

What final looks like:
Example-pipeline work can proceed with confidence instead of re-checking the whole script manually every time.

### Stage 6: Support multiple input files or batch folders

Stage name:
Stage 6: Support multiple input files or batch folders

Purpose:
Move from single-file processing to repeatable batch generation for local modelling experiments.

Material deliverable:
CLI support for multiple files or an input directory, plus deterministic output conventions.

Files likely changed:
`examples/build_feature_table.py`, possibly `README.rst`, maybe example batch fixtures if added.

Checks to build into the stage:
- single-file mode still works
- batch mode works
- predictable output locations
- `python -m pytest`

Common hurdles:
Ambiguous output naming, accidental overwrites, and inconsistent merge behavior.

How to avoid wasting prompts:
Decide early whether batch mode means “concatenate into one table” or “emit one output per input”.

Definition of done:
The generator can process more than one input source in a repeatable way.

What final looks like:
Local experiments can scale beyond toy one-file examples without hand-editing commands.

### Stage 7: Define a canonical racing feature schema

Stage name:
Stage 7: Define a canonical racing feature schema

Purpose:
Create one documented contract for column names, meanings, nullability, and modelling assumptions.

Material deliverable:
A schema document describing every emitted feature, expected type, missing-value behavior, and leakage notes.

Files likely changed:
`docs/*`, `README.rst` optionally, maybe the example script if column names are normalized.

Checks to build into the stage:
- schema matches actual output
- no duplicate or ambiguous feature names
- `python -m pytest`

Common hurdles:
Feature naming drift, undocumented assumptions, and accidental mixing of pre-race and post-race signals.

How to avoid wasting prompts:
Freeze naming and semantics in docs before adding many more columns.

Definition of done:
The output table has an explicit, reviewable schema that future tasks can target.

What final looks like:
Any future modelling or adapter work can build against one clear feature contract.

### Stage 8: Add export formats for modelling, such as CSV first, optional Parquet later

Stage name:
Stage 8: Add export formats for modelling, such as CSV first, optional Parquet later

Purpose:
Make the generator more useful for downstream tooling without overcomplicating the branch too early.

Material deliverable:
Stable CSV export plus optional additional format support, likely behind explicit CLI flags.

Files likely changed:
`examples/build_feature_table.py`, documentation, optional dependency config only if explicitly chosen later.

Checks to build into the stage:
- CSV path still works
- optional format path is explicit
- outputs are readable and schema-consistent
- `python -m pytest`

Common hurdles:
Premature dependency bloat and platform-specific file support issues.

How to avoid wasting prompts:
Keep CSV as the default and add optional formats only when there is a clear downstream use case.

Definition of done:
The tool can emit a stable modelling dataset in at least one strongly supported format and optionally more.

What final looks like:
Users can choose an output format that fits their local analysis stack without changing the underlying feature logic.

### Stage 9: Add a basic model-training example using generated features

Stage name:
Stage 9: Add a basic model-training example using generated features

Purpose:
Show an end-to-end local workflow from feature generation to a simple train/evaluate cycle.

Material deliverable:
A small modelling example that loads generated features, trains a baseline model, and emits simple metrics.

Files likely changed:
New `examples/` or `docs/` files, optional sample model artifacts, possibly `README.rst`.

Checks to build into the stage:
- feature table loads successfully
- training example runs end to end
- metrics are emitted
- `python -m pytest`

Common hurdles:
Target leakage, tiny-sample overfitting, dependency sprawl, and poorly defined labels.

How to avoid wasting prompts:
Start with a tiny explicit baseline model and document exactly which columns are excluded to avoid leakage.

Definition of done:
A user can produce features and train a simple local model with one documented workflow.

What final looks like:
The repo becomes a genuine modelling sandbox instead of only a feature-calculation sandbox.

### Stage 10: Add evaluation/backtesting-style outputs

Stage name:
Stage 10: Add evaluation/backtesting-style outputs

Purpose:
Move from “the model runs” to “the model can be judged”.

Material deliverable:
Basic evaluation outputs such as holdout metrics, ranked predictions, or simple strategy-style summaries.

Files likely changed:
New example scripts or docs, maybe example output artifacts, optional test coverage.

Checks to build into the stage:
- evaluation runs on generated features
- outputs are deterministic enough for review
- `python -m pytest`

Common hurdles:
Leakage, misleading metrics, non-repeatable splits, and overclaiming model quality.

How to avoid wasting prompts:
Define the evaluation target and split strategy before coding.

Definition of done:
The modelling example reports understandable metrics or backtest-style summaries from a reproducible workflow.

What final looks like:
Users can compare feature or modelling changes using the same evaluation path.

### Stage 11: Decide whether to modernize Provider/database layer or replace it with a new adapter interface

Stage name:
Stage 11: Decide whether to modernize Provider/database layer or replace it with a new adapter interface

Purpose:
Make a conscious architecture decision before spending prompts on high-effort infrastructure work.

Material deliverable:
A documented decision memo comparing “modernize existing Provider path” versus “introduce a new adapter interface”.

Files likely changed:
`docs/*`, maybe diagrams or comparison tables, maybe no code at all.

Checks to build into the stage:
- explicit tradeoff analysis
- migration cost estimate
- dependency risk analysis

Common hurdles:
Half-modernizing the old stack and ending up with two brittle systems instead of one clear path.

How to avoid wasting prompts:
Require a decision artifact before any real adapter or Provider rewrite begins.

Definition of done:
There is a clear go-forward architecture decision for data acquisition/storage responsibilities.

What final looks like:
Future prompts stop debating direction and start implementing against a chosen integration strategy.

### Stage 12: Add real-data adapter only after local pipeline is stable

Stage name:
Stage 12: Add real-data adapter only after local pipeline is stable

Purpose:
Connect the stable local feature pipeline to a real source only after input validation, schema, and outputs are settled.

Material deliverable:
A separate real-data adapter path that converts source data into the canonical feature-generator input schema.

Files likely changed:
New adapter modules, docs, optional config, possibly separate example inputs/outputs.

Checks to build into the stage:
- local CSV workflow still works
- adapter output matches canonical schema
- `python -m pytest`

Common hurdles:
Licensing issues, scraping fragility, provider assumptions, and Windows-incompatible dependencies returning too early.

How to avoid wasting prompts:
Keep the adapter boundary explicit: real-data tasks should produce canonical input, not re-entangle the generator with ingestion logic.

Definition of done:
Real source data can feed the local feature pipeline through a clear adapter interface.

What final looks like:
The project can move beyond hand-prepared CSVs without collapsing back into the old coupled architecture.

### Stage 13: Add CI/check automation

Stage name:
Stage 13: Add CI/check automation

Purpose:
Automate the verified modernization workflow so regressions are caught before manual review.

Material deliverable:
A modern CI configuration for branch-relevant checks such as `.venv`-equivalent installs, `python -m pytest`, and example command smoke tests.

Files likely changed:
CI config files, docs, maybe minimal helper scripts.

Checks to build into the stage:
- install
- `python -m pytest`
- local feature generator smoke test

Common hurdles:
Accidentally reviving the legacy tox/Travis dependency matrix instead of the modernization branch workflow.

How to avoid wasting prompts:
Start with a tiny CI workflow that mirrors the exact commands already verified locally.

Definition of done:
The branch has an automated check path aligned with the current modernization reality.

What final looks like:
Routine validation stops depending on manual Codex runs alone.

### Stage 14: Package or document the repo for normal use

Stage name:
Stage 14: Package or document the repo for normal use

Purpose:
Turn the branch from an internal modernization track into something a normal user can install, run, and understand.

Material deliverable:
Clear install/run docs, possibly packaged CLI entry points, example workflows, and operational guidance.

Files likely changed:
`README.rst`, packaging config, docs, optional CLI wrappers.

Checks to build into the stage:
- install works from clean environment
- documented commands match actual behavior
- `python -m pytest`

Common hurdles:
Docs drifting from reality and overpromising features that only exist as experiments.

How to avoid wasting prompts:
Document only verified workflows and keep “example”, “sandbox”, and “production-ready” labels explicit.

Definition of done:
A new user can install the repo, generate features, and understand the current maturity level without tribal knowledge.

What final looks like:
The repo has a coherent public-facing workflow instead of a set of branch-local experiments.

## 5. Hurdle catalogue

| Hurdle | Risk | Symptom | Prevention/check to build into future prompts | Recovery action |
|---|---|---|---|---|
| Wrong Python interpreter used instead of `.venv` | Commands pass or fail inconsistently | Missing packages such as `pytz`, different pytest behavior | Always activate `.venv` before Python commands and state that explicitly in the prompt | Re-run with `.venv\Scripts\Activate.ps1`; do not assume global Python matches |
| `cache_requests` / `redislite` failure on Windows | Legacy stack blocks progress | Install failures or broken tests on Windows | Explicitly forbid touching legacy stack unless the task is about it | Return to `modern_tests` and local-file workflows; defer legacy stack work |
| Legacy tests accidentally running | False failures and wasted debugging | `tests/` failures or dependency blow-ups | Keep `python -m pytest` through `pyproject.toml`; call out that only `modern_tests` should run | Stop, confirm `pyproject.toml`, rerun `python -m pytest` in `.venv` |
| Malformed CSV headers | Generator reads wrong fields or crashes | Key errors or blank output columns | Add validation for required headers before parsing rows | Print a clear required-column error and stop |
| Missing required columns | Incomplete features or runtime errors | `KeyError` or silent blanks in critical fields | Define required schema and validate before row processing | Report missing column names and exit non-zero |
| Empty CSV | No useful output or confusing crash | Index errors or empty output | Check for zero input rows explicitly | Exit with a clear message like “input file contains no data rows” |
| Date parsing failures | Incorrect joins and broken temporal logic | `ValueError` on parse or wrong date order | Validate date columns with clear expected format | Report offending row/column and stop |
| Numeric parsing failures | Broken math or misleading blanks | `ValueError` on float/int conversion | Validate numeric columns and distinguish required vs optional numeric fields | Report row/column/value and exit or blank only where optional |
| Missing values | Crashes in optional analysis fields | `TypeError` or incomplete output | Prefer existing properties that already tolerate `None`; serialize blanks for unavailable values | Add safe `None` handling in example code, not package code unless tests justify it |
| Output file overwritten unexpectedly | Loss of prior artifacts | Existing file silently replaced | Add explicit overwrite policy or output naming strategy in future stages | Restore from git or regenerate; later add `--force` or timestamp strategy |
| Generated CSV changing unexpectedly | Schema drift breaks downstream work | Header/order/value surprises | Add generator tests for header contract and sample output shape | Review diff, revert unintended columns, update schema docs deliberately |
| Package code changed accidentally during example-only tasks | Scope creep and risk to baseline | Unexpected diffs under `racing_data/` | Use strict allowed-file lists in every prompt | Revert unapproved package edits before continuing |
| Too much broad refactoring | High review cost and hidden regressions | Large diffs across unrelated files | Instruct Codex to avoid broad refactors and preserve existing behavior | Reset scope, keep only minimal targeted changes |
| Git branch mismatch | Work lands on the wrong branch | `git status` shows unexpected branch | Always run `git status` and `git branch --show-current` at task start | Switch intentionally or stop and ask before continuing |
| Uncommitted changes before starting | Hard-to-review mixed diffs | Dirty working tree at task start | Require `git status` before changes | Decide whether to pause, commit, or isolate work before proceeding |
| Push to wrong remote | Changes go to the wrong repository | Unexpected remote branch update | Check upstream with `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` | Push the correct branch to the correct remote after verifying |
| Codex modifies unrelated files | Review noise and merge risk | Extra files in `git diff` | Restrict allowed files and inspect `git diff` before commit | Unstage/revert unrelated files and continue only with intended changes |
| Path differences between Windows and POSIX | Commands or path resolution break | File not found errors across shells | Resolve paths relative to repo root and support absolute paths explicitly | Normalize paths and retest on the intended shell |
| Line-ending warnings | Noisy diffs and confusion | LF/CRLF warnings during git add | Expect warnings on Windows and avoid treating them as functional failures | Confirm content diff is correct; keep moving unless content changed unexpectedly |
| Long-running or stuck verification | Wasted prompt budget and incomplete state | Commands hang or time out | Use bounded commands and explicit smoke tests | Interrupt, narrow the command, and rerun with a clearer scope |
| Model leakage risk later when training | Inflated metrics and bad decisions | Suspiciously strong model performance | Separate pre-race features from post-race outcome fields before modelling | Remove leakage columns and rerun evaluation |
| Confusing feature names | Downstream misuse of columns | Ambiguous or overlapping feature semantics | Define a canonical schema with names, types, and meaning | Rename deliberately and regenerate example outputs |
| Real-data licensing/source issues later | Legal and operational risk | Source cannot be used or redistributed safely | Audit terms before adding a real-data adapter | Pause adapter work until source/legal constraints are documented |

## 6. Standard prompt guardrails for all future Codex tasks

### Default Codex guardrails

- check `git status` before changes
- confirm the current branch before editing
- modify only the listed files
- preserve existing behavior unless the task explicitly changes it
- do not touch Provider/scraper/database/cache_requests/redislite unless the task is specifically about them
- use `.venv` when running Python commands
- run the task-specific command checks requested by the prompt
- run `python -m pytest`
- show `git diff`
- commit only if checks pass
- push only after commit succeeds
- final response must include:
  - working tree status
  - commit hash
  - test results
  - commands run
  - files changed
  - whether package behavior changed

## 7. Stage-specific prompt templates

### Stage 3 validation prompt

Goal:
Add robust input validation to the local feature generator without changing package behavior.

Task:
Update the feature generator so malformed CSV input fails with clear, explicit errors for missing columns, empty files, bad dates, and bad numeric values.

Allowed files:
`examples/build_feature_table.py`, `README.rst` if validation behavior needs documenting, generator-focused test files only if explicitly requested.

Forbidden files:
`racing_data/*`, `MODERNIZATION_NOTES.md`, `pyproject.toml`, Provider/scraper/database files, legacy tests.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- `python examples\build_feature_table.py`
- invalid-input smoke tests
- `python -m pytest`
- `git diff`

Commit message:
`Add input validation to feature table generator`

Final response requirements:
Report working tree status, commit hash, validation scenarios checked, pytest result, files changed, and whether package behavior changed.

### Stage 4 richer feature columns prompt

Goal:
Expand the local feature table using existing analysis properties.

Task:
Add new model-ready columns to the generated feature CSV using existing `Runner`, `Performance`, and `PerformanceList` properties, with blanks for unavailable values.

Allowed files:
`examples/build_feature_table.py`, generated example CSVs, `README.rst` only if output description needs a small update.

Forbidden files:
Package code, tests unless explicitly requested, Provider/scraper/database files, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- `python examples\build_feature_table.py`
- `python examples\build_feature_table.py --input ... --output ...`
- `python -m pytest`
- `git diff`

Commit message:
`Add richer model-ready feature columns`

Final response requirements:
Report working tree status, commit hash, pytest result, commands run, output row count, new columns added, files changed, and whether package behavior changed.

### Stage 5 tests for feature generator prompt

Goal:
Make the local feature generator repeatable and regression-resistant.

Task:
Add focused tests for the generator’s CLI behavior, row count, schema headers, and safe handling of representative missing-value cases.

Allowed files:
`modern_tests/*`, helper fixtures if needed, `examples/build_feature_table.py` only if a failing test proves a bug, `README.rst` only if needed.

Forbidden files:
Package code unless tests justify it, legacy tests, Provider/scraper/database files, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- generator smoke commands
- `python -m pytest`
- `git diff`

Commit message:
`Add tests for feature table generator`

Final response requirements:
Report working tree status, commit hash, tests added, pytest result, files changed, and whether package behavior changed.

### Stage 6 batch input prompt

Goal:
Support repeatable multi-file or folder-based feature generation.

Task:
Extend the generator to accept multiple input files or an input directory while preserving current single-file behavior.

Allowed files:
`examples/build_feature_table.py`, example inputs/outputs, `README.rst`, test files if requested.

Forbidden files:
Package code, legacy tests, Provider/scraper/database files, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- single-file run
- batch-mode run
- `python -m pytest`
- `git diff`

Commit message:
`Add batch input support to feature generator`

Final response requirements:
Report working tree status, commit hash, batch behavior, pytest result, files changed, and whether package behavior changed.

### Stage 7 schema prompt

Goal:
Define and document the canonical feature schema for local modelling work.

Task:
Create or update docs that define column names, meanings, types, null handling, and leakage notes for the feature table.

Allowed files:
`docs/*`, `README.rst`, example output references if needed.

Forbidden files:
Package code, test files unless explicitly requested, Provider/scraper/database files, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- `python examples\build_feature_table.py`
- `python -m pytest`
- `git diff`

Commit message:
`Document canonical feature schema`

Final response requirements:
Report working tree status, commit hash, schema scope, pytest result, files changed, and whether package behavior changed.

### Stage 9 basic model example prompt

Goal:
Add a small, documented modelling example using generated features.

Task:
Create a baseline training example that consumes the generated feature table, excludes leakage-prone columns, trains a simple model, and emits basic metrics.

Allowed files:
`examples/*`, `docs/*`, `README.rst`, optional small sample outputs.

Forbidden files:
Package code unless explicitly justified, Provider/scraper/database files, legacy tests, `MODERNIZATION_NOTES.md`, `pyproject.toml` unless dependency/config changes are explicitly in scope.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- feature generation command
- model training example command
- `python -m pytest`
- `git diff`

Commit message:
`Add baseline model training example`

Final response requirements:
Report working tree status, commit hash, model command result, metrics emitted, pytest result, files changed, and whether package behavior changed.

### Stage 10 evaluation/backtesting prompt

Goal:
Add a reproducible evaluation path for the local modelling workflow.

Task:
Create an evaluation or backtesting example that uses generated features and emits basic metrics or ranked output summaries without overclaiming production performance.

Allowed files:
`examples/*`, `docs/*`, optional evaluation outputs, `README.rst` if needed.

Forbidden files:
Package code unless explicitly in scope, Provider/scraper/database files, legacy tests, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `.venv\Scripts\activate`
- feature generation command
- evaluation command
- `python -m pytest`
- `git diff`

Commit message:
`Add evaluation workflow example`

Final response requirements:
Report working tree status, commit hash, evaluation outputs, pytest result, files changed, and whether package behavior changed.

### Stage 11 adapter decision prompt

Goal:
Choose the long-term data-acquisition architecture before coding it.

Task:
Produce a decision memo comparing “modernize existing Provider/database path” against “introduce a new adapter interface”, including migration cost, dependency risk, Windows compatibility, and recommended next step.

Allowed files:
`docs/*`, optional `README.rst` cross-reference only if needed.

Forbidden files:
Package code, example data, tests, Provider/scraper/database implementation files, `MODERNIZATION_NOTES.md`, `pyproject.toml`.

Verification commands:
- `git status`
- `git diff`

Commit message:
`Add provider versus adapter decision memo`

Final response requirements:
Report working tree status, commit hash, recommendation chosen, files changed, and whether package behavior changed.

## 8. Final target vision

### Level A: Local feature-engineering tool

Fully operational at Level A means:

- a user supplies CSV input
- the script validates the input schema before processing
- the script outputs a model-ready feature table with a documented schema
- tests pass consistently on the modernization branch
- CLI usage is documented clearly for default and explicit paths

### Level B: Modelling sandbox

Fully operational at Level B means:

- generated feature tables can feed a documented model-training example
- the workflow emits basic metrics
- leakage-prone fields are excluded or clearly marked
- assumptions are documented
- users can compare feature/schema changes with repeatable evaluation outputs

### Level C: Production-ready racing data system

Fully operational at Level C means:

- a real ingestion adapter exists
- storage decisions are explicit and supported
- input/output validation is built in
- feature generation is repeatable
- model training and evaluation workflows are documented
- runs are repeatable end to end
- CI checks guard the verified workflows
- the operational workflow is documented for normal users

## 9. Immediate next best steps

1. Add schema validation and explicit CSV error handling
   This is the fastest way to turn the current generator from “works on the sample” into a safer reusable tool.

2. Add repeatable automated tests for the feature generator
   This will make future feature/schema changes much cheaper because the generator contract will stop depending on manual inspection.

3. Define the canonical feature schema and leakage policy
   This matters before any modelling work so the project can separate pre-race features from post-race outcomes and avoid building on unstable column semantics.
