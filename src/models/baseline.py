"""
baseline.py — Time-decayed historical affinity baseline for Eurovision jury vote prediction.

Pipeline:
  1. Load historical votes via eurojury.aggregate.load()
  2. Compute time-decayed affinity score for every (jury_iso, performer_iso) pair
  3. For a given test year: rank performers per jury by affinity score
  4. Map top-10 rankings → Eurovision point values {12,10,8,7,6,5,4,3,2,1}
  5. Return a DataFrame ready for metrics.evaluate()
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Eurovision point values assigned to ranks 1–10
RANK_TO_POINTS = {
	1: 12, 2: 10, 3: 8, 4: 7, 5: 6,
	6:  5, 7:  4, 8: 3, 9: 2, 10: 1,
}


# ---------------------------------------------------------------------------
# Step 1 — Decay weights
# ---------------------------------------------------------------------------

def _decay_weights(years: np.ndarray, test_year: int,
				   half_life: float) -> np.ndarray:
	"""
	Compute exponential decay weights for historical years relative to test_year.

	Weight formula: w(t) = 2 ** (-(test_year - t) / half_life)

	So a year exactly 'half_life' years before test_year gets weight 0.5, and
	test_year - 1 (most recent) approaches 1.0.

	Parameters
	 - years		: array of historical years
	 - test_year	: the year we are predicting (excluded from training)
	 - half_life	: number of years after which weight halves (default 3)

	Return
	 - np.ndarray of weights, same shape as years
	"""
	gaps = test_year - np.asarray(years, dtype=float)
	return np.power(2.0, -gaps / half_life)


# ---------------------------------------------------------------------------
# Step 2 — Affinity matrix
# ---------------------------------------------------------------------------

def compute_affinity(train_df: pd.DataFrame, test_year: int,
					 half_life: float = 3.0) -> pd.DataFrame:
	"""
	Compute time-decayed affinity score for every (jury_iso, performer_iso)
	pair seen in train_df.

	score(jury → performer) = Σ(w_t * points_t) / Σ(w_t)

	Only years strictly before test_year are used.

	Parameters
	 - train_df: historical votes DataFrame (columns: year, jury_iso,
		performer_iso, jury_points)
	 - test_year : prediction target year — rows with year >= test_year are
		excluded
	 - half_life : decay half-life in years

	Return
	 - DataFrame with columns: jury_iso | performer_iso | affinity_score
	"""
	df = train_df[train_df["year"] < test_year].copy()

	if df.empty:
		raise ValueError(f"No training data available before year {test_year}.")

	df["weight"] = _decay_weights(df["year"].values, test_year, half_life)
	df["weighted_points"] = df["weight"] * df["jury_points"]

	agg = (
			df.groupby(["jury_iso", "performer_iso"], sort=False)
				  .agg(
					  sum_weighted_points=("weighted_points", "sum"),
					  sum_weights=("weight", "sum"),
				  )
			  .reset_index()
	)

	agg["affinity_score"] = agg["sum_weighted_points"] / agg["sum_weights"]
	return agg[["jury_iso", "performer_iso", "affinity_score"]]


# ---------------------------------------------------------------------------
# Step 3+4 — Predict for a single test year
# ---------------------------------------------------------------------------

def predict_year(train_df: pd.DataFrame, test_df: pd.DataFrame,
				 test_year: int, half_life: float = 3.0) -> pd.DataFrame:
	"""
	Generate jury vote predictions for a single test year.

	Steps:
	 1. Compute affinity scores from train_df
	 2. For each (jury, performer) pair present in test_df, look up affinity
		 score → pairs with no history get score 0.0 (ranked last)
	 3. Rank performers per jury by affinity score (descending)
	 4. Map rank → predicted_points via RANK_TO_POINTS

	Parameters
	 - train_df: all historical data (will be filtered to < test_year
		internally)
	 - test_df: actual votes for test_year (used for jury/performer universe +
		ground truth)
	 - test_year: year to predict
	 - half_life: decay half-life in years

	Return
	 - DataFrame with columns:
		year | jury_iso | performer_iso | jury_points | predicted_score | predicted_points
	"""
	affinity = compute_affinity(train_df, test_year, half_life)

	# Work on test year only
	df = test_df[test_df["year"] == test_year].copy()

	# Merge affinity scores — unseen pairs get 0.0
	df = df.merge(affinity, on=["jury_iso", "performer_iso"], how="left")
	df["affinity_score"] = df["affinity_score"].fillna(0.0)

	# Rename for metrics.evaluate() compatibility
	df = df.rename(columns={"affinity_score": "predicted_score"})

	# Rank performers per jury (rank 1 = highest predicted_score)
	df["rank"] = (
			df.groupby("jury_iso")["predicted_score"]
			  .rank(method="first", ascending=False)
			  .astype(int)
	)

	# Map rank → predicted Eurovision points
	df["predicted_points"] = (
		df["rank"].map(RANK_TO_POINTS)
		.fillna(0)
		.astype(int)
	)

	return df[["year", "jury_iso", "performer_iso",
			   "jury_points", "predicted_score", "predicted_points"]]


# ---------------------------------------------------------------------------
# Step 5 — Rolling backtest
# ---------------------------------------------------------------------------

def rolling_backtest(full_df: pd.DataFrame,
					 half_life: float = 3.0,
					 min_train_years: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
	"""
	Perform a rolling backtest across all available years.

	For each test year t:
	 - Train on all years < t
	 - Predict year t
	 - Evaluate with metrics.evaluate()

	Parameters
	 - full_df			: complete dataset (all years)
	 - half_life		: decay half-life passed to predict_year
	 - min_train_years	: skip test years where fewer than this many training years
		exist (first years have too little history to be meaningful)

	Returns
	 - predictions_df	: all predictions concatenated (all test years)
	 - results_df		: one row per test year with nDCG@10, spearman, top3_hit_rate
	"""
	from .metrics import evaluate  # local import to avoid circular deps

	all_years = sorted(full_df["year"].unique())
	all_predictions = []
	all_results = []

	for test_year in all_years:
		train_years = [y for y in all_years if y < test_year]

		if len(train_years) < min_train_years:
			print(f"  Skipping {test_year} — only {len(train_years)} training year(s).")
			continue

		test_df = full_df[full_df["year"] == test_year]

		preds = predict_year(
			train_df=full_df,
			test_df=test_df,
			test_year=test_year,
			half_life=half_life,
		)

		metrics = evaluate(preds)
		metrics["year"] = test_year
		metrics["n_juries"] = preds["jury_iso"].nunique()
		metrics["n_train_years"] = len(train_years)

		all_predictions.append(preds)
		all_results.append(metrics)

		print(
			f"  {test_year} | "
			f"nDCG@10={metrics['ndcg@10']:.3f} | "
			f"Spearman={metrics['spearman']:.3f} | "
			f"Top3-HR={metrics['top3_hit_rate']:.3f} | "
			f"juries={metrics['n_juries']}"
		)

	predictions_df = pd.concat(all_predictions, ignore_index=True)
	results_df = pd.DataFrame(all_results).set_index("year")

	return predictions_df, results_df
