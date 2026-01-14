import pandas as pd
import requests
from bs4 import BeautifulSoup
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent
mappings_dir = base_dir / "data" / "mappings"
mappings_dir.mkdir(parents= True, exist_ok= True)
output_file = mappings_dir / "iso_country_codes.xlsx"

url = "https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3"

headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
}

response = requests.get(url, headers= headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

plainlist = soup.find("div", class_= "plainlist")
items = plainlist.find_all("li")

data = []

for item in items:
	code_tag = item.find("span", class_= "monospaced")
	country_tag = item.find("a")

	if code_tag and country_tag:
		data.append({
			"iso_alpha_3": code_tag.text.strip(),
			"country_name": country_tag.text.strip()
		})

df = pd.DataFrame(data).sort_values("country_name")
df.to_excel(output_file, index= False)

print(f"Saved {len(df)} ISO country codes to {output_file}")