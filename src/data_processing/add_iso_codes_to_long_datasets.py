import pandas as pd
from pathlib import Path

# paths
base_dir = Path(__file__).resolve().parent.parent
mappings_dir = base_dir / "data" / "mappings"
long_datasets_dir = base_dir / "data" / "long_datasets"
output_dir = base_dir / "data" / "long_datasets_with_iso"
output_dir.mkdir(parents= True, exist_ok= True)

mapping_file = mappings_dir / "eurovision_country_check.xlsx"

# load mapping
mapping_df = pd.read_excel(mapping_file)
iso_map = dict(
	zip(mapping_df["eurovision_name"], mapping_df["iso_alpha_3"])
)

# helper
def get_iso(country_name: str):
	if (pd.isna(country_name)):
		return None

	return iso_map.get(country_name)

# process datasets
for file in long_datasets_dir.glob("*.xlsx"):
	df = pd.read_excel(file)

	df["performer_iso"] = df["performer_country"].apply(get_iso)
	df["jury_iso"] = df["jury_country"].apply(get_iso)

	output_file = output_dir / file.name
	df.to_excel(output_file, index= False)
	print(f"ISO codes added to {output_file}")