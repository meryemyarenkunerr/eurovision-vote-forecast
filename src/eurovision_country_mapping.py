import pandas as pd
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
mappings_dir = base_dir / "data" / "mappings"

iso_file = mappings_dir / "iso_country_codes.xlsx"
output_file = mappings_dir / "eurovision_country_check.xlsx"

# Eurovision 2018 country list
eurovision_countries = [
	"Ukraine", "Azerbaijan", "Belarus", "San Marino", "Netherlands",
	"Macedonia", "Malta", "Georgia", "Spain", "Austria", "Denmark",
	"United Kingdom", "Sweden", "Latvia", "Albania", "Croatia", "Ireland",
	"Romania", "Czech Republic", "Iceland", "Moldova", "Belgium",
	"Norway", "France", "Italy", "Australia", "Estonia", "Serbia",
	"Cyprus", "Armenia", "Bulgaria", "Greece", "Hungary", "Montenegro",
	"Germany", "Finland", "Russia", "Switzerland", "Israel", "Poland",
	"Lithuania", "Slovenia", "Portugal"
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
print(f"Eurovision 2018 country mapping check saved to {output_file}")