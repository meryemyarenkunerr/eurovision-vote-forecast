import pandas as pd

ALLOWED_POINTS = {0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12}
REQUIRED_SET = {1, 2, 3, 4, 5, 6, 7, 8, 10, 12}

def validate_group(g: pd.DataFrame) -> list[str]:
	errs = []

	# 1) no self-votes
	if (g["jury_iso"] == g["performer_iso"]).any():
		errs.append("self-votes present")

	# 2) allowed points
	bad = ~g["jury_points"].isin(ALLOWED_POINTS)
	if bad.any():
		errs.append(f"invalid points: {sorted(
			g.loc[bad, "jury_points"].unique()
			)}")

	# 3-5) compute non-zero points once
	nz_values = g.loc[g["jury_points"] > 0, "jury_points"]
	nz_count = len(nz_values)
	nz_set = set(nz_values)
	nz_sum = nz_values.sum()

	if nz_count != 10:
		errs.append(f"non-zero points = {nz_count} (expected 10)")

	if nz_set != REQUIRED_SET:
		errs.append(f"set = {sorted(nz_set)} (expected {sorted(REQUIRED_SET)})")

	if nz_sum != 58:
		errs.append(f"sum = {nz_sum} (expected 58)")

	# 6) uniqueness
	dups = g.duplicated(["year", "jury_iso", "performer_iso"]).sum()
	if dups > 0:
		errs.append(f"duplicates = {dups}")

	return errs

def validate_all(df: pd.DataFrame) -> None:
	# required columns
	needed = {"year", "jury_iso", "performer_iso", "jury_points"}
	missing = needed - set(df.columns)
	if missing:
		raise ValueError(f"Missing columns: {sorted(missing)}")

	# coerce types
	df["year"] = (
		df["year"].astype(str)
		.str.replace(",", "", regex= False)
		.astype(int)
	)
	df["jury_points"] = (
		pd.to_numeric(df["jury_points"], errors= "coerce")
		.fillna(0)
		.astype(int)
	)

	problems = []
	for key, g in df.groupby(["year", "jury_iso"], sort= True):
		errs = validate_group(g)
		if errs:
			problems.append((key, errs))

	if problems:
		msgs = []
		for (y, jury), errs in problems:
			msgs.append(f"{y} | {jury}: " + "; ".join(errs))
		raise ValueError("Validation failed:\n" + "\n".join(msgs))
