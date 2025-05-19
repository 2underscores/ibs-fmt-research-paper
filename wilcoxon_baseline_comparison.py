import pandas as pd
import numpy as np
from scipy import stats
import os

# Load the dataset
try:
    df = pd.read_csv('data/ibs-all-patients-flat-scores.csv')
except FileNotFoundError:
    print("Error: 'data/ibs-all-patients-flat-scores.csv' not found. Make sure the file is in the 'data' directory.")
    exit()

# Data Cleaning and Preparation
df['score'] = pd.to_numeric(df['score'], errors='coerce')
df.dropna(subset=['score'], inplace=True)
df['follow_up_number'] = pd.to_numeric(df['follow_up_number'], errors='coerce')
df.dropna(subset=['follow_up_number'], inplace=True)
df['patient_number'] = df['patient_number'].astype(str)
df['patient_fmt_or_p'] = df['patient_fmt_or_p'].astype(str).str.upper()

# Create results directory if it doesn't exist
os.makedirs('results', exist_ok=True)

def perform_wilcoxon_test(baseline_scores, follow_up_scores):
    """Perform Wilcoxon test and return results."""
    # Calculate differences
    differences = follow_up_scores - baseline_scores
    
    # Remove zero differences as they don't contribute to the test
    differences = differences[differences != 0]
    
    if len(differences) < 2:  # Need at least 2 non-zero differences
        return {
            'statistic': np.nan,
            'p_value': np.nan,
            'significant': False,
            'n': len(differences)
        }
    
    # Use the 'zero_method' parameter to handle ties correctly
    statistic, p_value = stats.wilcoxon(differences, zero_method='wilcox')
    return {
        'statistic': statistic,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'n': len(differences)
    }

def format_p_value(p_value):
    """Format p-value for LaTeX table."""
    if pd.isna(p_value):
        return "---"
    if p_value < 0.001:
        return "< 0.001"
    return f"{p_value:.3f}"

def generate_results_table():
    """Generate results table for all surveys and follow-ups."""
    # Store all results
    all_results = []
    
    # Process each survey
    for survey_name in sorted(df['survey_name'].unique()):
        survey_df = df[df['survey_name'] == survey_name].copy()
        
        # Process each treatment group
        for treatment in ['FMT', 'PLACEBO']:
            treatment_df = survey_df[survey_df['patient_fmt_or_p'] == treatment]
            
            # Get baseline scores (follow-up 0)
            baseline_scores = treatment_df[treatment_df['follow_up_number'] == 0].groupby('patient_number')['score'].sum()
            
            # Compare each follow-up to baseline
            for follow_up in sorted(treatment_df['follow_up_number'].unique()):
                if follow_up == 0:  # Skip comparing baseline to itself
                    continue
                    
                follow_up_scores = treatment_df[treatment_df['follow_up_number'] == follow_up].groupby('patient_number')['score'].sum()
                
                # Ensure we only compare patients who have both baseline and follow-up scores
                common_patients = baseline_scores.index.intersection(follow_up_scores.index)
                if len(common_patients) < 2:  # Need at least 2 patients for the test
                    continue
                    
                baseline_subset = baseline_scores[common_patients]
                follow_up_subset = follow_up_scores[common_patients]
                
                # Calculate mean changes
                mean_baseline = baseline_subset.mean()
                mean_followup = follow_up_subset.mean()
                mean_change = mean_followup - mean_baseline
                
                # Perform Wilcoxon test
                result = perform_wilcoxon_test(baseline_subset, follow_up_subset)
                
                # Store results
                all_results.append({
                    'Survey': survey_name,
                    'Treatment': treatment,
                    'Follow-up': follow_up,
                    'N': result['n'],
                    'Baseline Mean': mean_baseline,
                    'Follow-up Mean': mean_followup,
                    'Mean Change': mean_change,
                    'Statistic': result['statistic'],
                    'p-value': result['p_value'],
                    'Significant': result['significant']
                })
    
    return pd.DataFrame(all_results)

def generate_latex_table(results_df):
    """Generate LaTeX table from results DataFrame."""
    latex_table = []
    latex_table.append("\\begin{table}[htbp]")
    latex_table.append("\\centering")
    latex_table.append("\\caption{Wilcoxon Signed Rank Test Results: Comparison to Baseline}")
    latex_table.append("\\label{tab:wilcoxon_baseline}")
    
    # Add table header
    latex_table.append("\\begin{tabular}{llrrrrrrr}")
    latex_table.append("\\hline")
    latex_table.append("Survey & Treatment & Follow-up & N & Baseline & Follow-up & Change & W & p-value \\\\")
    latex_table.append("\\hline")
    
    # Add data rows
    for _, row in results_df.iterrows():
        p_value = format_p_value(row['p-value'])
        if row['Significant']:
            p_value = f"\\textbf{{{p_value}}}"
        
        # Format the statistic, using --- for NaN values
        statistic = "---" if pd.isna(row['Statistic']) else f"{row['Statistic']:.1f}"
        
        row_str = (f"{row['Survey']} & {row['Treatment']} & {row['Follow-up']} & {row['N']} & "
                  f"{row['Baseline Mean']:.1f} & {row['Follow-up Mean']:.1f} & "
                  f"{row['Mean Change']:+.1f} & {statistic} & {p_value} \\\\")
        latex_table.append(row_str)
    
    latex_table.append("\\hline")
    latex_table.append("\\end{tabular}")
    latex_table.append("\\end{table}")
    
    return "\n".join(latex_table)

# Generate results
results_df = generate_results_table()

# Generate and save LaTeX table
latex_table = generate_latex_table(results_df)
output_file = "results/wilcoxon_baseline_table.tex"
with open(output_file, 'w') as f:
    f.write(latex_table)

# Also save as CSV for easy access
results_df.to_csv("results/wilcoxon_baseline_results.csv", index=False)

print(f"\nResults have been saved to:")
print(f"1. LaTeX table: {output_file}")
print(f"2. CSV file: results/wilcoxon_baseline_results.csv") 