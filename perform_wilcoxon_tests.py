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

# Function to perform Wilcoxon test and return results
def perform_wilcoxon_test(baseline_scores, follow_up_scores):
    # Calculate differences
    differences = follow_up_scores - baseline_scores
    
    # Remove zero differences as they don't contribute to the test
    differences = differences[differences != 0]
    
    if len(differences) < 2:  # Need at least 2 non-zero differences
        return {
            'statistic': np.nan,
            'p_value': np.nan,
            'significant': False
        }
    
    # Use the 'zero_method' parameter to handle ties correctly
    statistic, p_value = stats.wilcoxon(differences, zero_method='wilcox')
    return {
        'statistic': statistic,
        'p_value': p_value,
        'significant': p_value < 0.05
    }

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
            
            # Perform Wilcoxon test
            result = perform_wilcoxon_test(baseline_subset, follow_up_subset)
            
            # Store results
            all_results.append({
                'Survey': survey_name,
                'Treatment': treatment,
                'Follow-up': follow_up,
                'N': len(common_patients),
                'Statistic': result['statistic'],
                'p-value': result['p_value'],
                'Significant': result['significant']
            })

# Convert results to DataFrame
results_df = pd.DataFrame(all_results)

# Format p-values to 3 decimal places
results_df['p-value'] = results_df['p-value'].round(3)

# Create styled table
styled_table = results_df.style.set_properties(**{
    'text-align': 'center',
    'padding': '5px',
    'border': '1px solid black'
}).set_table_styles([
    {'selector': 'th',
     'props': [('background-color', '#f0f0f0'),
              ('text-align', 'center'),
              ('padding', '5px'),
              ('border', '1px solid black'),
              ('font-weight', 'bold')]},
    {'selector': 'td',
     'props': [('border', '1px solid black')]},
    {'selector': 'tr:nth-of-type(odd)',
     'props': [('background-color', '#f9f9f9')]}
])

# Save results as HTML
output_file = "results/wilcoxon_test_results.html"
with open(output_file, 'w') as f:
    f.write("<h2>Wilcoxon Signed Rank Test Results</h2>")
    f.write("<p>Comparing each follow-up to baseline (follow-up 0) for each treatment group.</p>")
    f.write("<p>Significance level: α = 0.05</p>")
    f.write(styled_table.to_html())

print("\nWilcoxon test results have been generated in 'results/wilcoxon_test_results.html'")

# Also save as CSV for easy access to the raw data
results_df.to_csv("results/wilcoxon_test_results.csv", index=False)
print("Raw results have also been saved to 'results/wilcoxon_test_results.csv'") 