# IBS Patient Study: FMT Treatment Analysis

This repository contains code for analyzing the effects of Fecal Microbiota Transplant (FMT) treatment on IBS patients, comparing outcomes between FMT and placebo groups.

## Project Overview

This study investigates the effectiveness of FMT treatment for IBS patients through a controlled trial with the following characteristics:
- Approximately 20 patients with IBS
- 5 sessions per patient (1 initial + 4 follow-ups)
- Two treatment groups: FMT and placebo
- Three surveys administered at each session:
  - DASS (Depression, Anxiety, and Stress Scale)
  - IBS-QoL (IBS Quality of Life)
  - IBS-SSS (IBS Symptom Severity Score)

## Data Structure

The main data file `data/ibs-all-patients-flat-scores.csv` contains the following columns:
- `survey_name`: Survey type (DASS, IBS-QoL, IBS-SSS)
- `q_number`: Question number within the survey
- `q_id`: Unique question ID across all surveys
- `q_category`: Question category for granular scoring
- `patient_number`: Patient identifier (HC01-HC21)
- `patient_fmt_or_placebo`: Treatment group (FMT or placebo)
- `follow_up_number`: Session number (0-4, where 0 is initial)
- `answer`: Patient's response
- `score`: Numerical score for the response

Additional reference files:
- `all-survey-questions`: Complete list of survey questions
- `patient-fmt-or-placebo`: Patient treatment group assignments

## Analysis Scripts

### 1. Wilcoxon Test Analysis (`perform_wilcoxon_tests.py`)
Performs Wilcoxon signed rank tests to compare baseline and follow-up scores for each:
- Survey type
- Treatment group
- Follow-up session

Outputs:
- HTML report with formatted results table
- CSV file with raw test results

### 2. Data Verification (`check_wilcoxon_data.py`)
Utility script to verify Wilcoxon test results by examining specific cases in detail.

## Results

The analysis reveals:
1. Significant improvement (p < 0.05) in:
   - IBS-QoL scores for placebo group at follow-up 1 (p = 0.031)

2. Notable trends:
   - Most changes were not statistically significant
   - Sample sizes range from 4-7 patients per group
   - Follow-up 4 groups have smaller sample sizes (4 patients)

## Requirements

Required Python packages:
- pandas
- numpy
- scipy
- jinja2

Install dependencies:
```bash
pip install pandas numpy scipy jinja2
```

## Usage

1. Ensure data files are in the `data/` directory
2. Run the analysis:
```bash
python perform_wilcoxon_tests.py
```
3. View results in:
   - `results/wilcoxon_test_results.html`
   - `results/wilcoxon_test_results.csv`

## Project Structure
```
.
├── data/
│   ├── ibs-all-patients-flat-scores.csv
│   ├── all-survey-questions
│   └── patient-fmt-or-placebo
├── results/
│   ├── wilcoxon_test_results.html
│   └── wilcoxon_test_results.csv
├── perform_wilcoxon_tests.py
├── check_wilcoxon_data.py
└── README.md
```
