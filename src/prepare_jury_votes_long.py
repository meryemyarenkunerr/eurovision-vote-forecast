import pandas as pd
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

raw_dir = project_root / "data" / "raw"
long_dir = project_root / "data" / "long_datasets"
long_dir.mkdir(exist_ok= True)

files = raw_dir.glob("jury_votes_*.xlsx")

for file in files:
	year = int(file.stem.split("_")[-1])
	print(f"Processing {year}...")

	df = pd.read_excel(file)
	df.drop(columns= "Year", inplace= True)

	df_long = df.melt(
		id_vars= "Contestant",
		var_name= "jury_country",
		value_name= "jury_points"
	)

	df_long = df_long.rename(
		columns= {"Contestant": "performer_country"}
	)

	df_long["jury_points"] = (
		df_long["jury_points"]
		.fillna(0)
		.astype(int)
	)

	df_long["year"] = year

	df_long = df_long[
		df_long["jury_country"] != df_long["performer_country"]
	]

	output_path = long_dir / f"jury_votes_{year}_long.xlsx"
	df_long.to_excel(output_path, index= False)
	print(f"Saved to {output_path}")