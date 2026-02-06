from pathlib import Path
import pandas as pd
from .validate import validate_all
from .io import load_one_year_file

base_dir = Path(__file__).resolve().parents[2]
long_datasets_dir = base_dir / "data" / "long_datasets_with_iso"

def load(years: list[int] | None = None,
		 folder: str = long_datasets_dir) -> pd.DataFrame:
	"""
	Read per-year long Excel format files, normalize columns, concatenate,
	and run validations. Returns a modeling-ready DataFrame.
	"""

	folder_path = Path(folder)
	all_paths = sorted(folder_path.glob("jury_votes_*_long.xlsx"))
	if not all_paths:
		raise FileNotFoundError(f"No files found in {folder_path}")

	def year_from_name(p: Path) -> int:
		# expects filename: jury_votes_YYYY_long.xlsx
		return int(p.stem.split("_")[2])

	selected = [p for p in all_paths
			 if (years is None or year_from_name(p) in years)]

	if not selected:
		raise FileNotFoundError(f"No files matched requested years: {years}")

	frames = [load_one_year_file(p) for p in selected]
	df = pd.concat(frames, ignore_index= True)

	validate_all(df) # raises on error
	return df
