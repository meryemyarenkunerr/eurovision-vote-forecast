import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def fetch_jury_voting_table(year):
	"""
	Fetch the jury voting table for a given Eurovision year from Wikipedia.

	Args:
		year (int): Contest year (e.g., 2016)

	Returns:
		tuple:
			- final_results: HTML table element or None if not found.
			- column_names: List of column headers including 'Contestant' and 'Year'.
	"""

	url = "https://en.wikipedia.org/wiki/Eurovision_Song_Contest_" + str(year)
	data = requests.get(url).text
	soup = BeautifulSoup(data, 'html.parser')

	tables = soup.find_all('table', class_='wikitable plainrowheaders')
	final_results = None

	# Look for the table specifically labeled as "jury voting results of the final"
	for table in tables:
		caption = table.find('caption')
		if caption and 'jury voting results of the final' in caption.text.lower():
			final_results = table
			break

	column_names = ["Contestant"]
	if final_results:
		tbody = final_results.find('tbody')
		rows = tbody.find_all('tr')
		attribute_row = rows[1].find_all('th')
		names = [cell.get_text(strip= True) for cell in attribute_row]
		column_names.extend(names)

	column_names.extend(["Year"])
	return final_results, column_names


def get_data(final_result, year):
	"""
	Parse jury vote data from given HTML table and year.

	Args:
		final_result: HTML table element withjury notes.
		year (int): Contest year.

	Returns:
		list: Rows of woting data with country names and contest year.
	"""

	data = []
	rows = final_result.find('tbody').find_all('tr')[3:]

	flag = 0  # Used to treat the first data row differently due to HTML structure
	for row in rows:
		cells = row.find_all(['th', 'td'])

		if flag == 0:
			# First row have extra <th> cell, so indexes shift by 1
			country = [cells[1].get_text(strip= True)]
			votes = [cell.get_text(strip= True) for cell in cells[5:]]
			votes.append(year)

			country.extend(votes)
			data.append(country)
			flag = 1
		else:
			country = [cells[0].get_text(strip= True)]
			votes = [cell.get_text(strip= True) for cell in cells[4:]]
			votes.append(year)

			country.extend(votes)
			data.append(country)

	return data

# Ensure "data/" folder exists
project_root = os.path.dirname(os.path.dirname(__file__))
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok= True)

# Loop over multiple years and save as CSV
for year in range(2016, 2026):
	print(f"Processing year: {year}")

	if year == 2020:
		print(f"The Eurovision Song Contest could not be held in {year} due to Covid.")
		continue

	final_res, column_names = fetch_jury_voting_table(year)

	if final_res:
		data = get_data(final_res, year)
		df = pd.DataFrame(data, columns= column_names)
		df.to_csv(os.path.join(data_dir, f"jury_votes_{year}.csv"), index= False)
		print(f"Saved data/jury_votes_{year}.csv")
	else:
		print("No jury data found for {year}.")