# Eurovision Jury Vote Predictor 🎤🌍

This project aims to **predict which country will award jury points to which other country** in the next year's Eurovision Song Contest.
The focus is on **jury voting behavior**, rather than televoting, using past data scraped from Wikipedia and modeling patterns in cross-country jury preferences.

---

## 🎯 Project Objective

The goal is to build a machine learning model that can answer questions like:

> *"Which country is likely to give its 12 jury points to whom in next year’s contest?"*

Unlike models that predict the total score or final ranking, this project focuses specifically on the **jury vote giver–receiver relationship**, framing the task as a **learning-to-rank problem**.

---

## 📦 Features

### Implemented

* ✅ Automated web scraping of jury voting tables from Wikipedia (2016–2025)
* ✅ Robust data cleaning and normalization using ISO country codes
* ✅ Transformation of raw tables into a long-format dataset suitable for ML
* ✅ Ranking-based machine learning approach for jury vote prediction

### Planned / In Progress

* 🚧 Feature enrichment with geographical and regional proximity
* 🚧 Historical bias and voting affinity features (e.g. repeated jury preferences)
* 🚧 Temporal weighting to emphasize recent contests
* 🚧 Model comparison with alternative ranking algorithms
* 🚧 Extended evaluation metrics tailored to Eurovision voting rules

---

## 📁 Repository Structure

```
eurovision-vote-forecast/
│
│── data/                  # Raw and processed jury vote files
│
│── src/
│   ├── data_processing/   # Modular preprocessing steps
│   ├── models/            # Model training and inference scripts
│   └── utils/             # Shared helper functions
│
│── notebooks/             # Exploratory analysis and experiments
│── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

---

## 🧪 Technologies Used

* Python 3.x
* `requests`, `BeautifulSoup4` – Web scraping
* `pandas`, `numpy` – Data processing
* `lightgbm` – Learning-to-rank model (`import lightgbm as lgb`)
* `scikit-learn` – Evaluation utilities
* `matplotlib`, `seaborn` – Visualization

---

## 📊 Data Representation

The final modeling dataset is in **long format**, where each row represents a jury–performer interaction for a given year.

| jury_iso | performer_iso | jury_points | year |
| -------- | ------------- | ----------- | ---- |
| ALB      | SWE           | 12          | 2022 |
| ALB      | ITA           | 10          | 2022 |
| ...      | ...           | ...         | ...  |

This structure enables treating each jury as a *query group* and the performers as *ranked candidates*.

---

## 🧠 Modeling Approach

* Each **jury country** is modeled as a separate ranking query
* The task is to **rank performer countries** by likelihood of receiving high jury points
* The model learns from historical voting patterns only, without using song-level features

### Why LightGBM Ranker?

Eurovision jury voting is inherently a **ranking problem**: each jury produces an ordered list of countries and assigns points based on relative preference, not absolute scores.

`LightGBM LGBMRanker` is well-suited for this task because:

* It directly optimizes ranking-based objectives (e.g. LambdaRank)
* It naturally supports **grouped data** (one group per jury)
* It handles sparse and categorical-heavy feature spaces efficiently
* It scales well as additional features (geography, history, recency) are introduced

This makes LightGBM a strong baseline for modeling structured preference behavior such as Eurovision jury voting.

---

## 🚀 Getting Started

1. Clone the repository

   ```bash
   git clone https://github.com/meryemyarenkunerr/eurovision-vote-forecast.git
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the data processing pipeline

   ```bash
   python src/data_processing/build_dataset.py
   ```

4. Train the ranking model

   ```bash
   python src/models/ranker.py
   ```

---

## 📌 Notes

* Only the **modern Eurovision voting system (post-2016)** is used
* Country names are normalized using **ISO-3 codes** to avoid inconsistencies
* Model interpretation and qualitative analysis are handled separately from this repository
