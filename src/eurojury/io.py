from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parents[2]
processed_dataset_dir = base_dir / "data" / "processed"

def load_one_year_file(path: Path) -> pd.DataFrame:
	"""
	Load a single year's long-format Excel file.
	"""
	df = pd.read_excel(path, engine= "openpyxl")
	df.columns = [c.strip().lower() for c in df.columns]

	# basic coercions
	if "year" in df.columns:
		df["year"] = (
			df["year"].astype(str)
			.str.replace(",", "", regex= False)
			.astype(int)
		)
	if "jury_points" in df.columns:
		df["jury_points"] = (
			pd.to_numeric(df["jury_points"], errors= "coerce")
			.fillna(0)
			.astype(int)
		)

	# normalize text fields if present
	for col in ["jury_country", "performer_country", "jury_iso",
			 "performer_iso"]:
		if col in df.columns:
			df[col] = df[col].astype(str).str.strip()

	return df

def export(df: pd.DataFrame, fmt: str = "csv",
		   out: str = processed_dataset_dir) -> None:
	p = Path(out)
	p.parent.mkdir(parents= True, exist_ok= True)
	if fmt == "csv":
		df.to_csv(p, index= False)
	elif fmt == "parquet":
		df.to_parquet(p, index= False)
	elif fmt in ("xlsx", "excel"):
		with pd.ExcelWriter(p, engine= "openpyxl") as xw:
			df.to_excel(xw, sheet_name= "votes", index= False)
	else:
		raise ValueError(f"Unsupported export fmt: {fmt}")
