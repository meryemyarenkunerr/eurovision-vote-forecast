# Eurovision Jury Vote Predictor 🎤🌍

This project aims to **predict which country will award jury points to which other country** in the next year's Eurovision Song Contest.
The focus is on **jury voting behavior**, rather than televoting, using past data scraped from Wikipedia and modeling patterns in cross-country jury preferences.

---

## 🎯 Project Objective

The goal is to build a machine learning model that can answer questions like:

> *"Which country is likely to give its 12 jury points to whom in next year’s contest?"*

Unlike models that predict the total score or rank, this project focuses on the **jury vote giver–receiver relationship**.

---

## 📦 Features

- ✅ Automated web scraping of jury voting tables from Wikipedia (2016–2025)
- ✅ Cleaned and structured CSV outputs for each year
- 🚧 (In Progress) Machine learning model to predict country-to-country jury votes

---

## 📁 Repository Structure

```
eurovision-jury-predictor/
│
│── data/ # Yearly CSV files (jury_votes_2016.csv, ...)
│── src/ # Python scripts for scraping & modeling
│	 ├── scrape.py # Wikipedia scraper using BeautifulSoup
│	 └── model.py # (Planned) ML model for prediction
│
│── notebooks/ # Jupyter notebooks for exploration
│
│── README.md # This file
└── requirements.txt # Python dependencies
```

## 🧪 Technologies Used

- Python 3.x
- `requests`, `BeautifulSoup4` – Web scraping
- `pandas` – Data cleaning
- `scikit-learn` (planned) – Modeling jury vote preferences
- `matplotlib`, `seaborn` – Data visualization

---

## 📊 Data Format

Each CSV (e.g., `jury_votes_2021.csv`) contains a structured view of how one country gave points to others in the final.

| Contestant | Country A | Country B | ... | Year |
|------------|-----------|-----------|-----|------|
| Germany    | 10        | 12        | ... | 2021 |
| France     | 8         | 6         | ... | 2021 |
| ...        | ...       | ...       | ... | ...  |

---

## 🧠 Prediction Task (planned)

- **Input**: Past jury voting behavior, geographical, cultural, or political similarities
- **Output**: Ranked list of countries each jury is likely to award 12–10–8...1 points to

---

## 🚀 Getting Started

1. Clone the repository
   ```
   git clone https://github.com/meryemyarenkunerr/eurovision-vote-forecast.git
   ```

2. Install dependencies
   ```
   pip install -r requirements.txt
   ```

3. Run scraper for a given year
   ```python
   from src.scrape import get_jury_votes, get_data
   ```