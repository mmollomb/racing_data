# Feature Schema

This document defines the current output schema for the local feature-table generator:

- script: `examples/build_feature_table.py`
- example input: `data/examples/sample_runner_history.csv`
- example output: `data/examples/runner_features.csv`

This is a practical contract for local modelling work on the `modernize-analysis-layer` branch.

## Leakage policy

Columns classified as `outcome_or_target` must not be used as model inputs for pre-race prediction.

They may be kept only for:

- labels/targets
- evaluation
- reporting
- sanity checks

If a modelling task is intended to make predictions before the race is run, the default assumption is:

- `outcome_or_target` columns are excluded from the input matrix
- `review_before_modelling` columns are excluded unless the modelling task explicitly justifies and documents their use

## Current columns

| Column | Classification | Practical note |
|---|---|---|
| `runner_id` | `identifier/context` | Row identifier for joins and traceability; exclude from model inputs. |
| `horse_name` | `review_before_modelling` | Useful for inspection, but high-cardinality identity data should be excluded unless explicitly encoded. |
| `race_date` | `review_before_modelling` | Useful context, but requires an explicit time encoding and train/test split policy. |
| `race_track` | `review_before_modelling` | Useful context, but should only be used after an explicit categorical encoding decision. |
| `race_distance` | `pre_race_feature` | Declared race distance; available before the race. |
| `race_key` | `identifier/context` | Stable per-race identifier derived from date, track, and distance for grouping/reporting. |
| `runner_number` | `review_before_modelling` | Program number, not barrier; keep only if a modelling use case is explicitly justified. |
| `carrying` | `pre_race_feature` | Current listed weight less allowances. |
| `actual_weight` | `pre_race_feature` | Horse weight baseline plus carried weight. |
| `actual_distance` | `pre_race_feature` | Barrier-adjusted race distance estimate derived from current race context. |
| `career_starts` | `historical_derived_feature` | Historical career count before the current race. |
| `career_wins` | `historical_derived_feature` | Historical career wins before the current race. |
| `career_places` | `historical_derived_feature` | Historical career places before the current race. |
| `career_win_pct` | `historical_derived_feature` | Historical career win rate. |
| `career_second_pct` | `historical_derived_feature` | Historical career second-place rate. |
| `career_third_pct` | `historical_derived_feature` | Historical career third-place rate. |
| `career_roi` | `historical_derived_feature` | Historical return-on-investment summary. |
| `career_earnings` | `historical_derived_feature` | Historical prize-money total. |
| `career_earnings_potential` | `historical_derived_feature` | Historical earnings as a share of prize pools. |
| `career_result_potential` | `historical_derived_feature` | Historical result-quality aggregate from prior runs. |
| `last_10_wins` | `historical_derived_feature` | Wins in the most recent up-to-10 prior runs. |
| `last_10_places` | `historical_derived_feature` | Places in the most recent up-to-10 prior runs. |
| `last_10_win_pct` | `historical_derived_feature` | Win rate in the most recent up-to-10 prior runs. |
| `last_10_place_pct` | `historical_derived_feature` | Place rate in the most recent up-to-10 prior runs. |
| `last_10_starts` | `historical_derived_feature` | Number of prior runs considered in the last-10 window. |
| `last_12_months_starts` | `historical_derived_feature` | Number of prior runs in the previous 12 months. |
| `at_distance_starts` | `historical_derived_feature` | Prior starts near the current race distance. |
| `at_distance_win_pct` | `historical_derived_feature` | Historical win rate near the current race distance. |
| `on_track_starts` | `historical_derived_feature` | Prior starts on the current track. |
| `on_track_win_pct` | `historical_derived_feature` | Historical win rate on the current track. |
| `on_good_starts` | `historical_derived_feature` | Prior starts on good tracks. |
| `on_good_win_pct` | `historical_derived_feature` | Historical win rate on good tracks. |
| `on_soft_starts` | `historical_derived_feature` | Prior starts on soft tracks. |
| `on_soft_win_pct` | `historical_derived_feature` | Historical win rate on soft tracks. |
| `with_jockey_starts` | `historical_derived_feature` | Prior starts with the same jockey. |
| `with_jockey_win_pct` | `historical_derived_feature` | Historical win rate with the same jockey. |
| `starting_price` | `outcome_or_target` | Current-race starting price from `current_performance`; not safe as a default pre-race input. |
| `result` | `outcome_or_target` | Current-race finishing result; primary label-style field. |
| `current_performance_profit` | `outcome_or_target` | Current-race derived profit field based on current outcome. |
| `previous_performance_result` | `historical_derived_feature` | Most recent prior-run finishing result. |
| `previous_performance_starting_price` | `historical_derived_feature` | Most recent prior-run starting price. |
| `spell_days` | `pre_race_feature` | Days since the runner’s previous performance. |
| `up` | `pre_race_feature` | Current run number since last spell of 90 days or more. |

## Safe modelling input columns

These are the default safe input columns for pre-race modelling work, assuming the task is to predict the current race without using current-race outcomes:

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

## Excluded columns

These should be excluded by default from pre-race model inputs:

- `runner_id`
- `race_key`
- `horse_name`
- `race_date`
- `race_track`
- `runner_number`
- `starting_price`
- `result`
- `current_performance_profit`

## Possible target columns

These are the current columns most likely to be used as targets, depending on the modelling task:

- `result`
  Default race-outcome target.
- `current_performance_profit`
  Suitable for profit-oriented or betting-style experiments.
- `starting_price`
  Only for explicitly defined market/price modelling tasks; not a default pre-race prediction input.

## Future schema decisions

- Decide whether `race_date`, `race_track`, `horse_name`, and `runner_number` stay excluded by default or move into an explicitly encoded feature set.
- Split the generated schema into:
  - a strict pre-race feature view
  - an evaluation/target-enriched post-race view
- Add explicit type/nullability documentation for every column.
- Version the schema so downstream modelling code can detect breaking changes.
- Define one canonical target policy per modelling workflow to avoid mixing labels across experiments.
