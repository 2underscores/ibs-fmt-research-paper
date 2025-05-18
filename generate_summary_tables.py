import pandas as pd
import numpy as np
import os

# Load the dataset
try:
    df = pd.read_csv('data/ibs-all-patients-flat-scores.csv')
except FileNotFoundError:
    print("Error: 'data/ibs-all-patients-flat-scores.csv' not found. Make sure the file is in the 'data' directory.")
    exit()

# Data Cleaning and Preparation
# Convert 'score' to numeric, coercing errors to NaN
df['score'] = pd.to_numeric(df['score'], errors='coerce')

# Drop rows where 'score' is NaN after conversion
df.dropna(subset=['score'], inplace=True)

# Ensure 'follow_up_number' and 'patient_number' are of appropriate types
df['follow_up_number'] = pd.to_numeric(df['follow_up_number'], errors='coerce')
df.dropna(subset=['follow_up_number'], inplace=True)
df['patient_number'] = df['patient_number'].astype(str)
df['patient_fmt_or_p'] = df['patient_fmt_or_p'].astype(str).str.upper()

# Create results directory if it doesn't exist
os.makedirs('results', exist_ok=True)

# Function to format mean and std as "mean±std"
def format_mean_std(mean, std):
    return f"{mean:.1f}±{std:.1f}"

# Process each survey
for survey_name in sorted(df['survey_name'].unique()):
    survey_df = df[df['survey_name'] == survey_name].copy()
    
    # Get unique categories for this survey
    categories = sorted(survey_df['q_category'].unique())
    
    # Create empty list to store rows
    table_rows = []
    
    # Process each follow-up number
    for follow_up in sorted(survey_df['follow_up_number'].unique()):
        follow_up_df = survey_df[survey_df['follow_up_number'] == follow_up]
        
        # Process each treatment group
        for treatment in ['FMT', 'PLACEBO']:
            treatment_df = follow_up_df[follow_up_df['patient_fmt_or_p'] == treatment]
            
            # Calculate total scores per patient
            patient_totals = treatment_df.groupby('patient_number')['score'].sum()
            
            # Calculate mean and std for total scores
            total_mean = patient_totals.mean()
            total_std = patient_totals.std()
            
            # Get number of patients in this group
            n_patients = len(patient_totals)
            
            # Create row with follow-up, treatment, N, and total score
            row = {
                'Follow-up': follow_up,
                'Group': treatment,
                'N': n_patients,
                'Total Score': format_mean_std(total_mean, total_std)
            }
            
            # Calculate mean and std for each category
            for category in categories:
                category_scores = treatment_df[treatment_df['q_category'] == category].groupby('patient_number')['score'].sum()
                cat_mean = category_scores.mean()
                cat_std = category_scores.std()
                row[category] = format_mean_std(cat_mean, cat_std)
            
            table_rows.append(row)
    
    # Create DataFrame from rows
    table_df = pd.DataFrame(table_rows)
    
    # Reorder columns to put Total Score after N
    cols = ['Follow-up', 'Group', 'N', 'Total Score'] + categories
    table_df = table_df[cols]
    
    # Create styled table
    styled_table = table_df.style.set_properties(**{
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
    
    # Save as HTML
    output_file = f"results/{survey_name}_summary_table.html"
    with open(output_file, 'w') as f:
        f.write(f"<h2>{survey_name} Summary Table</h2>")
        f.write(styled_table.to_html())
    
    print(f"Generated summary table for {survey_name}")

print("\nAll summary tables have been generated in the 'results' directory.") 