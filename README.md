# AI Usage Data: Cleaning and Visualization

**Question:** How can a messy, synthetic AI-usage table be made analysis-ready with documented, reproducible steps, and what distributions does the cleaned data show?

> **Note:** The dataset is synthetic. According to its author, it was generated for educational purposes and intentionally includes missing values, duplicates and inconsistent formats. Nothing here describes real students or professionals.

## Summary
A 300 x 19 synthetic table of AI tool usage by students and professionals was validated and cleaned with logged, reusable functions. The cleaning dropped 12 exact duplicates, removed units from 81 numeric cells in 6 columns, merged category spellings (AI_Tool 16 → 8, Gender 11 → 3, Education_Level 16 → 6, Country 20 → 12) and set 4 impossible values to NaN, all without imputation. In the cleaned data, daily AI usage and Productivity_Score rank together strongly (Spearman 0.81), while Satisfaction_Score barely varies across purposes or between paid and free users.

## Key findings
1. In this dataset, only 138 of 288 cleaned rows are fully complete, but each single analysis still keeps n = 266-280 because rows are dropped per analysis, not globally (see `figures/01_missing_values.png`, `figures/02_ai_tool_standardization.png`).
2. In this dataset, daily AI usage and Productivity_Score have Spearman rho = 0.81 (n = 266), with similar values for students (0.82) and professionals (0.80) (see `figures/04_usage_vs_productivity.png`).
3. In this dataset, mean Satisfaction_Score ranges only from 5.82 (Coding) to 6.41 (Research) across purposes, every purpose median is 6, and paid vs free users average 5.98 vs 6.24 with both medians at 6 (see `figures/05_satisfaction_by_purpose.png`, `figures/06_satisfaction_paid_vs_free.png`).

Students and professionals also have nearly the same median daily usage, 2.00 vs 2.05 hours (`figures/03_usage_by_user_type.png`).

## Limitations
- Synthetic data: relationships reflect how the data was generated, not real behavior. This applies to every finding.
- Small sample (300 rows before cleaning, 288 after).
- Productivity, accuracy and satisfaction are simulated scores, so no causal claims. Each score is read on its own observed scale (Productivity 1.6-10, Accuracy 2-5, Satisfaction 3-10).
- Finding 1: some category mappings are assumptions (Gemini → Google Gemini, Copilot → Microsoft Copilot, Non-binary → Other); Undergraduate and Bachelor's are kept separate even though they likely overlap.
- Finding 2: Spearman only measures a monotonic association. 23 rows report more AI hours than work/study hours and were kept, so the usage column itself is partly inconsistent.
- Finding 3: Satisfaction is an integer score with 8 observed levels, some groups are small (Office Work n = 11), and no hypothesis test was run, so small mean gaps are not interpreted.
- Monthly_Income currency is unknown; it is never compared across countries.

## Product takeaway
Most of the cleaning work here (51 Gender relabels, 16 AI_Tool relabels, 81 numeric cells with units) comes from free-text input. A form with fixed choice lists for categories and numeric-only fields with the unit in the label would remove that work at collection time.

## Data
- Source: https://www.kaggle.com/datasets/eishatuzzuhra/ai-usage-and-impact-on-students-and-professionals, License: CC0 1.0 (Public Domain)
- Data is not included in the repo. Download with:
  `kaggle datasets download -d eishatuzzuhra/ai-usage-and-impact-on-students-and-professionals -p data/ --unzip`
- Generated outputs, also under `data/` (ignored): `ai_usage_clean.csv`, `cleaning_log.csv`, `category_mappings.csv`, `raw_report.csv`

## Method
- Validate the raw CSV (shape, types, missing values, duplicates, unique values): `src/validate_raw.py`
- Clean with reusable, logged functions in `src/clean.py`: drop exact duplicates, strip units, map category spellings with explicit tables, flag outliers
- Outliers are flagged in `flag_*` columns. Only 4 impossible values are set to NaN (Age 97 in 2 rows, 23 h/day of AI usage, a 250,000 income for a 17-year-old student); their rows stay
- Missing values are not imputed; each analysis reports its own n
- Verify cleaning with a before/after summary, mapping tables and 13 automated checks
- Descriptive statistics and Spearman correlation only (no ML, no hypothesis tests); figures in `src/figures.py`

## Reproduce
Tested with Python 3.15.
```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
kaggle datasets download -d eishatuzzuhra/ai-usage-and-impact-on-students-and-professionals -p data/ --unzip
jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb   # or: jupyter notebook notebooks/analysis.ipynb
```

## Structure
`data/` (ignored) | `notebooks/analysis.ipynb` | `figures/` | `src/clean.py`, `src/figures.py`, `src/validate_raw.py` | `DEVLOG.md` | `05-kalite-kontrol.md`
