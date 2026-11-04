# Data location

Download the official **Online Retail II** Excel workbook from:
https://archive.ics.uci.edu/dataset/502/online+retail+ii

Place `online_retail_II.xlsx` in `data/raw/` (NOT in `.venv`).
The dataset is intentionally not in this GitHub repository or ZIP archive.

Explore it:
`python src/explore_data.py`

Generate derived outputs:
`python -m src.pipeline`

Generated outputs are saved in `data/processed/` and excluded from Git.
