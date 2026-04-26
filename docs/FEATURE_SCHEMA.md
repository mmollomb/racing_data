# Feature Schema

This document defines the current output contract for the local MVP feature generator on the `modernize-analysis-layer` branch.

- generator: `examples/build_feature_table.py`
- sample input: `data/examples/sample_runner_history.csv`
- sample output: `data/examples/runner_features.csv`
- report consumer: `examples/train_baseline_model.py`

The local MVP is intentionally file-based. It does not depend on live scraping, MongoDB, `Provider`, `cache_requests`, or `redislite`.

## Leakage policy

Columns classified as `outcome/target/leakage` must not be used as model inputs for pre-race ranking.

They may be used only for:

- evaluation
- reporting
- sanity checks
- explicitly target-oriented experiments

The current default safe modelling set excludes:

- `starting_price`
- `result`
- `current_performance_profit`

It also excludes identifier/context columns such as `runner_id`, `race_key`, `horse_name`, `race_date`, `race_track`, and `runner_number`.

## Output columns

| Column | Meaning | Source | Type | Blank behavior | Classification |
|---|---|---|---|---|---|
| `runner_id` | Stable row identifier for the current runner. | input `runner_id` -> `Runner["runner_id"]` | string | Never blank for valid input. | `identifier/context` |
| `horse_name` | Horse name for inspection and reporting. | input `horse_name` -> `Runner.horse["name"]` | string | Never blank for valid input. | `identifier/context` |
| `race_date` | Date of the target race. | `runner.race.meet["date"]` | string (`YYYY-MM-DD`) | Blank only if the race date is missing upstream. | `identifier/context` |
| `race_track` | Track of the target race. | `runner.race.meet["track"]` | string | Blank only if the race track is missing upstream. | `identifier/context` |
| `race_distance` | Declared race distance. | `runner.race["distance"]` | integer | Blank if race distance is missing. | `safe model input` |
| `race_key` | Stable race grouping key built from date, track, and distance. | generated from `race_date + "_" + race_track + "_" + race_distance` | string | Blank only if one of the source race fields is missing. | `identifier/context` |
| `runner_number` | Program number within the race. | `Runner["number"]` | integer | Blank if runner number is missing. | `identifier/context` |
| `carrying` | Current listed weight after jockey claim. | `runner.carrying` | float | Blank if runner weight is missing. | `safe model input` |
| `actual_weight` | Horse-weight baseline plus carried weight. | `runner.actual_weight` | float | Falls back to horse baseline weight if carrying is missing. | `safe model input` |
| `actual_distance` | Barrier-adjusted race distance estimate. | `runner.actual_distance` | float | Blank if race distance is missing. | `safe model input` |
| `career_starts` | Number of historical starts before the current race. | `runner.career.starts` | integer | `0` when there are no historical performances. | `derived historical feature` |
| `career_wins` | Historical win count before the current race. | `runner.career.wins` | integer | `0` when there are no historical wins. | `derived historical feature` |
| `career_places` | Historical place count before the current race. | `runner.career.places` | integer | `0` when there are no historical placings. | `derived historical feature` |
| `career_win_pct` | Historical win rate. | `runner.career.win_pct` | float | Blank when the career list is empty. | `derived historical feature` |
| `career_second_pct` | Historical second-place rate. | `runner.career.second_pct` | float | Blank when the career list is empty. | `derived historical feature` |
| `career_third_pct` | Historical third-place rate. | `runner.career.third_pct` | float | Blank when the career list is empty. | `derived historical feature` |
| `career_roi` | Historical $1 win-bet ROI. | `runner.career.roi` | float | Blank when the career list is empty. | `derived historical feature` |
| `career_earnings` | Historical prize money total. | `runner.career.earnings` | float | `0` when no prize money is available. | `derived historical feature` |
| `career_earnings_potential` | Historical prize money as a share of historical prize pools. | `runner.career.earnings_potential` | float | Blank when no prize-pool data is available. | `derived historical feature` |
| `career_result_potential` | Historical result-quality aggregate. | `runner.career.result_potential` | float | Blank when required result/starter inputs are missing. | `derived historical feature` |
| `last_10_wins` | Wins in the most recent up-to-10 prior runs. | `runner.last_10.wins` | integer | `0` when there are no prior wins in the last-10 window. | `derived historical feature` |
| `last_10_places` | Placings in the most recent up-to-10 prior runs. | `runner.last_10.places` | integer | `0` when there are no placings in the last-10 window. | `derived historical feature` |
| `last_10_win_pct` | Win rate in the most recent up-to-10 prior runs. | `runner.last_10.win_pct` | float | Blank when the last-10 list is empty. | `derived historical feature` |
| `last_10_place_pct` | Place rate in the most recent up-to-10 prior runs. | `runner.last_10.place_pct` | float | Blank when the last-10 list is empty. | `derived historical feature` |
| `last_10_starts` | Number of prior runs included in the last-10 window. | `runner.last_10.starts` | integer | `0` when there are no prior runs. | `derived historical feature` |
| `last_12_months_starts` | Number of prior runs inside the last 12 months. | `runner.last_12_months.starts` | integer | `0` when there are no matching historical runs. | `derived historical feature` |
| `at_distance_starts` | Number of prior runs within 100m of the target race distance. | `runner.at_distance.starts` | integer | `0` when there are no matching runs. | `derived historical feature` |
| `at_distance_win_pct` | Historical win rate within 100m of the target distance. | `runner.at_distance.win_pct` | float | Blank when the distance-matched list is empty. | `derived historical feature` |
| `on_track_starts` | Number of prior runs on the target track. | `runner.on_track.starts` | integer | `0` when there are no track-matched runs. | `derived historical feature` |
| `on_track_win_pct` | Historical win rate on the target track. | `runner.on_track.win_pct` | float | Blank when the track-matched list is empty. | `derived historical feature` |
| `on_good_starts` | Number of prior runs on good tracks. | `runner.on_good.starts` | integer | `0` when there are no good-track runs. | `derived historical feature` |
| `on_good_win_pct` | Historical win rate on good tracks. | `runner.on_good.win_pct` | float | Blank when the good-track list is empty. | `derived historical feature` |
| `on_soft_starts` | Number of prior runs on soft tracks. | `runner.on_soft.starts` | integer | `0` when there are no soft-track runs. | `derived historical feature` |
| `on_soft_win_pct` | Historical win rate on soft tracks. | `runner.on_soft.win_pct` | float | Blank when the soft-track list is empty. | `derived historical feature` |
| `with_jockey_starts` | Number of prior runs with the current jockey. | `runner.with_jockey.starts` | integer | `0` when there are no same-jockey runs. | `derived historical feature` |
| `with_jockey_win_pct` | Historical win rate with the current jockey. | `runner.with_jockey.win_pct` | float | Blank when the same-jockey list is empty. | `derived historical feature` |
| `starting_price` | Current-race starting price if a matching current performance is present. | `runner.starting_price` | float | Blank when the current race result row is absent. | `outcome/target/leakage` |
| `result` | Current-race finishing result if a matching current performance is present. | `runner.result` | integer | Blank when the current race result row is absent. | `outcome/target/leakage` |
| `current_performance_profit` | Current-race $1 win-bet profit/loss. | `runner.current_performance.profit` | float | Blank when the current race result row is absent. | `outcome/target/leakage` |
| `previous_performance_result` | Result of the most recent prior run. | `runner.previous_performance["result"]` | integer | Blank when no prior performance exists. | `derived historical feature` |
| `previous_performance_starting_price` | Starting price of the most recent prior run. | `runner.previous_performance["starting_price"]` | float | Blank when no prior performance exists or starting price is missing. | `derived historical feature` |
| `spell_days` | Days since the previous run. | `runner.spell` | integer | Blank when no previous performance exists. | `safe model input` |
| `up` | Current run number since the last long spell. | `runner.up` | integer | Blank only if underlying runner history cannot be resolved. | `safe model input` |

## Current safe modelling feature set

These are the current default safe numeric modelling inputs for the local MVP baseline:

- `race_distance`
- `carrying`
- `actual_weight`
- `actual_distance`
- `career_starts`
- `career_wins`
- `career_places`
- `career_win_pct`
- `career_second_pct`
- `career_third_pct`
- `career_roi`
- `career_earnings`
- `career_earnings_potential`
- `career_result_potential`
- `last_10_wins`
- `last_10_places`
- `last_10_win_pct`
- `last_10_place_pct`
- `last_10_starts`
- `last_12_months_starts`
- `at_distance_starts`
- `at_distance_win_pct`
- `on_track_starts`
- `on_track_win_pct`
- `on_good_starts`
- `on_good_win_pct`
- `on_soft_starts`
- `on_soft_win_pct`
- `with_jockey_starts`
- `with_jockey_win_pct`
- `previous_performance_result`
- `previous_performance_starting_price`
- `spell_days`
- `up`

## Outcome/target candidate columns

These columns are useful for evaluation or explicit target-oriented experiments, but not as default pre-race inputs:

- `result`
- `current_performance_profit`
- `starting_price`

## Future schema decisions

- Decide whether context columns such as `race_track`, `race_date`, and `runner_number` should stay excluded by default or move into an explicitly encoded feature set.
- Decide whether a strict pre-race feature export and an evaluation-enriched export should become separate output modes.
- Add an explicit schema version identifier to the feature table.
- Add stricter per-column validation for date parsing and required numeric fields when sample inputs move beyond the bundled demo data.
