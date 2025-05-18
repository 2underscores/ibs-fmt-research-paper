import pandas as pd
import numpy as np
from scipy import stats

# Load the dataset
df = pd.read_csv('data/ibs-all-patients-flat-scores.csv')

# Data Cleaning and Preparation
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df.dropna(subset=['score'], inplace=True)
df['follow_up_number'] = pd.to_numeric(df['follow_up_number'], errors='coerce')
df.dropna(subset=['follow_up_number'], inplace=True)
df['patient_number'] = df['patient_number'].astype(str)
df['patient_fmt_or_p'] = df['patient_fmt_or_p'].astype(str).str.upper()

# Function to print detailed comparison
def print_comparison(survey_name, treatment, follow_up):
    survey_df = df[df['survey_name'] == survey_name].copy()
    treatment_df = survey_df[survey_df['patient_fmt_or_p'] == treatment]
    
    # Get baseline scores
    baseline_scores = treatment_df[treatment_df['follow_up_number'] == 0].groupby('patient_number')['score'].sum()
    
    # Get follow-up scores
    follow_up_scores = treatment_df[treatment_df['follow_up_number'] == follow_up].groupby('patient_number')['score'].sum()
    
    # Get common patients
    common_patients = baseline_scores.index.intersection(follow_up_scores.index)
    
    print(f"\nDetailed comparison for {survey_name}, {treatment}, Follow-up {follow_up}:")
    print(f"Number of patients: {len(common_patients)}")
    print("\nPatient scores:")
    print("Patient\tBaseline\tFollow-up\tDifference")
    print("-" * 50)
    
    for patient in common_patients:
        baseline = baseline_scores[patient]
        follow_up = follow_up_scores[patient]
        diff = follow_up - baseline
        print(f"{patient}\t{baseline:.1f}\t\t{follow_up:.1f}\t\t{diff:+.1f}")
    
    # Perform Wilcoxon test
    statistic, p_value = stats.wilcoxon(baseline_scores[common_patients], follow_up_scores[common_patients])
    print(f"\nWilcoxon test statistic: {statistic:.3f}")
    print(f"p-value: {p_value:.3f}")

# Check cases where p=1.0
print_comparison('IBS-QOL', 'FMT', 2)  # IBS-QOL FMT follow-up 2
print_comparison('IBS-SSS', 'PLACEBO', 1)  # IBS-SSS Placebo follow-up 1
print_comparison('IBS-SSS', 'PLACEBO', 2)  # IBS-SSS Placebo follow-up 2 