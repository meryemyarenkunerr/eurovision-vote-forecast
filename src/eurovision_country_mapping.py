import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
mappings_dir = base_dir / "data" / "mappings"

iso_file = mappings_dir / "iso_country_codes.xlsx"
output_file = mappings_dir / "eurovision_country_check.xlsx"

# Eurovision 2016-2025 country list
eurovision_countries = [
	"Albania", "Armenia", "Australia", "Austria", "Azerbaijan",
	"Belarus", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czechia",
	"Czech Republic", "Denmark", "Estonia", "Finland", "France",
	"Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland",
	"Israel", "Italy", "Latvia", "Lithuania", "Luxembourg", "Macedonia",
	"Malta", "Moldova", "Montenegro", "Netherlands", "North Macedonia",
	"Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino",
	"Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
	"Ukraine", "United Kingdom"
]

# malual alias
manual_aliases = {
	"Netherlands": "Netherlands, Kingdom of the",
	"Macedonia": "North Macedonia",
	"United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
	"Czech Republic": "Czechia",
	"Moldova": "Moldova, Republic of",
	"Russia": "Russian Federation"
}

iso_df = pd.read_excel(iso_file)

# normalize for safer matching
iso_df["country_name_norm"] = iso_df["country_name"].str.lower().str.strip()

euro_df = pd.DataFrame({
	"eurovision_name": eurovision_countries
})
euro_df["mapped_name"] = euro_df["eurovision_name"].map(
	lambda x: manual_aliases.get(x, x)
)
euro_df["mapped_name_norm"] = euro_df["mapped_name"].str.lower().str.strip()

merged = euro_df.merge(
	iso_df,
	left_on= "mapped_name_norm",
	right_on= "country_name_norm",
	how= "left"
)

# keep it clean
result = merged[[
	"eurovision_name",
	"country_name",
	"iso_alpha_3"
]]

result.to_excel(output_file, index= False)
print(f"Eurovision country mapping check saved to {output_file}")