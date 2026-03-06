"""
metrics.py — Ranking evaluation metrics for Eurovision jury vote prediction.

Metrics:
	- nDCG@k			: Normalized Discounted Cumulative Gain
	- Spearman			: Rank correlation between predicted and actual scores
	- Top-k hit rate	: Fraction of juries whose actual top-k appears in
	predicted top-k
"""

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


# ---------------------------------------------------------------------------
# nDCG@k
# ---------------------------------------------------------------------------

def dcg_at_k(relevances: np.ndarray, k: int) -> float:
	"""
	Compute DCG@k for a single ranked list.

	Parameters
		- relevances: Relevance scores in predicted rank order (highest
		predicted -> first).
		- k: Cutoff rank.
	"""
	relevances = np.asarray(relevances, dtype=float)[:k]
	if relevances.size == 0:
		return 0.0
	positions = np.arange(1, relevances.size + 1)
	return float(np.sum(relevances / np.log2(positions + 1)))


def ndcg_at_k(y_true: np.ndarray, y_pred: np.ndarray, k: int) -> float:
	"""
	Compute nDCG@k for a single jury (query).

	Parameters
		- y_true: Actual jury_points for each performer (same order as y_pred).
		- y_pred: Predicted scores for each performer.
		- k: Cutoff rank.
	"""
	y_true = np.asarray(y_true, dtype=float)
	y_pred = np.asarray(y_pred, dtype=float)

	# Sort true relevances by predicted score (descending)
	pred_order = np.argsort(-y_pred)
	relevances_in_pred_order = y_true[pred_order]

	# Ideal: sort true relevances descending
	ideal_relevances = np.sort(y_true)[::-1]

	dcg  = dcg_at_k(relevances_in_pred_order, k)
	idcg = dcg_at_k(ideal_relevances, k)

	return dcg / idcg if idcg > 0 else 0.0


def mean_ndcg_at_k(df: pd.DataFrame, k: int,
				   score_col: str = "predicted_score",
				   label_col: str = "jury_points",
				   group_cols: tuple = ("year", "jury_iso")) -> float:
	"""
	Compute mean nDCG@k across all (year, jury) groups in df.

	Parameters
		- df: DataFrame with columns group_cols + [score_col, label_col]
		- k: Cutoff rank
		- score_col: Column containing predicted scores
		- label_col: Column containing ground-truth points
		- group_cols: Columns that define a single jury query

	Return
		— macro-averaged nDCG@k
	"""
	scores = []
	for _, group in df.groupby(list(group_cols)):
		scores.append(
				  ndcg_at_k(
						group[label_col].values,
						group[score_col].values,
						k=k
				  )
		)
	return float(np.mean(scores)) if scores else 0.0


# ---------------------------------------------------------------------------
# Spearman ρ
# ---------------------------------------------------------------------------

def mean_spearman(df: pd.DataFrame,
				  score_col: str = "predicted_score",
				  label_col: str = "jury_points",
				  group_cols: tuple = ("year", "jury_iso")) -> float:
	"""
	Compute mean Spearman rank correlation across all jury groups.
	Groups with fewer than 2 performers are skipped.

	Return
		— macro-averaged Spearman rho
	"""
	rhos = []
	for _, group in df.groupby(list(group_cols)):
		if len(group) < 2:
			continue
		rho, _ = spearmanr(group[label_col].values,
					 group[score_col].values)
		if not np.isnan(rho):
			rhos.append(rho)
	return float(np.mean(rhos)) if rhos else 0.0


# ---------------------------------------------------------------------------
# Top-k hit rate
# ---------------------------------------------------------------------------

def top_k_hit_rate(df: pd.DataFrame, k: int,
				   score_col: str = "predicted_score",
				   label_col: str = "jury_points",
				   group_cols: tuple = ("year", "jury_iso"),
				   performer_col: str = "performer_iso") -> float:
	"""
	Fraction of juries where at least one of the actual top-k point receivers
	appears in the predicted top-k.

	"Actual top-k" = k performers with the highest jury_points.
	"Predicted top-k" = k performers with the highest predicted_score.

	Parameters
		- df: DataFrame with required columns
		- k: Top-k cutoff
		- score_col: Predicted score column
		- label_col: Ground-truth points column
		- group_cols: Columns defining a jury group
		- performer_col: Column identifying performers

	Return
		- float in [0, 1]
	"""
	hits = []
	for _, group in df.groupby(list(group_cols)):
		actual_top_k = set(
			group.nlargest(k, label_col)[performer_col]
		)
		predicted_top_k = set(
			group.nlargest(k, score_col)[performer_col]
		)
		hits.append(int(bool(actual_top_k & predicted_top_k)))
	return float(np.mean(hits)) if hits else 0.0


# ---------------------------------------------------------------------------
# Convenience: evaluate all metrics at once
# ---------------------------------------------------------------------------

def evaluate(df: pd.DataFrame,
			 score_col: str = "predicted_score",
			 label_col: str = "jury_points",
			 group_cols: tuple = ("year", "jury_iso"),
			 performer_col: str = "performer_iso",
			 k: int = 10) -> dict:
	"""
	Run all three metrics and return a summary dict.

	Return
		- dict with keys: ndcg@k, spearman, top3_hit_rate
	"""
	return {
		f"ndcg@{k}": mean_ndcg_at_k(df, k=k,
							  score_col=score_col,
							  label_col=label_col,
							  group_cols=group_cols),
		"spearman": mean_spearman(df,
								  score_col=score_col,
								  label_col=label_col,
								  group_cols=group_cols),
		"top3_hit_rate": top_k_hit_rate(df, k=3,
										score_col=score_col,
										label_col=label_col,
										group_cols=group_cols,
										performer_col=performer_col),
	}
