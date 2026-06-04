# Modern Olympic Games Analysis

An exploratory data analysis of the Modern Olympic Games (1992–present), focusing on the post-USSR era to ensure consistent country-level comparisons.

## Overview

This project analyses Olympic data to extract insights on medals, athletes, countries, and disciplines across both Summer and Winter Games. The analysis intentionally starts from the 1992 edition to avoid splitting results between the USSR and its successor states.

Notable limitations in the source data:
- No qualification/semi-final results — only finals are recorded
- Team events with more than 2 athletes are stored as team records, not individual entries

## Data Sources

Data is sourced from two Kaggle datasets:
- [Olympic Games Medals 1986–2018](https://www.kaggle.com/datasets/piterfm/olympic-games-medals-19862018) by piterfm
- [126 Years of Historical Olympic Dataset](https://www.kaggle.com/datasets/muhammadehsan02/126-years-of-historical-olympic-dataset) by muhammadehsan02

## Repository Structure

```
.
├── Data/
│   ├── olympic_athletes.csv     # Athlete profiles and participation info
│   ├── olympic_hosts.csv        # Host cities, dates, and seasons
│   ├── olympic_medals.csv       # Medal records per athlete/team/event
│   └── olympic_results.csv      # Full event results with rankings
├── DataExtraction/
│   ├── scraping.py              # Parallel scraper for athlete bio data (sex, height, weight, NOC)
│   └── olympia_athletes_bio_parallel.csv  # Scraped biographical data
└── ModernOlympicAnalysis.Rmd    # Main R Markdown analysis document
```

## Requirements

**R analysis (`ModernOlympicAnalysis.Rmd`):**
- R ≥ 4.0
- Packages: `readr`, `dplyr`, `purrr`, and other tidyverse libraries

**Data scraper (`DataExtraction/scraping.py`):**
- Python ≥ 3.8
- `pandas`, `requests`, `beautifulsoup4`, `tqdm`

Install Python dependencies with:
```bash
pip install pandas requests beautifulsoup4 tqdm
```

## Usage

Open `ModernOlympicAnalysis.Rmd` in RStudio and knit to HTML or PDF. The scraper in `DataExtraction/scraping.py` can be re-run to refresh athlete biographical data.
