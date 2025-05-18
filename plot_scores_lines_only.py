import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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
df.dropna(subset=['follow_up_number'], inplace=True) # Drop if follow_up_number is not valid
df['patient_number'] = df['patient_number'].astype(str)
# Ensure patient_fmt_or_p is string and uppercase for consistent mapping
df['patient_fmt_or_p'] = df['patient_fmt_or_p'].astype(str).str.upper()

# Get unique survey names
survey_names = sorted(df['survey_name'].unique()) # Sort for consistent order
num_surveys = len(survey_names)

# Create a figure with subplots
# Adjust figsize: width 12, height 5 per subplot
fig, axes = plt.subplots(nrows=num_surveys, ncols=1, figsize=(12, 5 * num_surveys), sharex=True)
if num_surveys == 1: # Ensure axes is always a list for consistent indexing
    axes = [axes]

# Define colors for treatments
color_mapping = {'FMT': 'green', 'PLACEBO': 'orange'}

# Create a plot for each survey on its respective subplot
for i, survey_name in enumerate(survey_names):
    ax = axes[i]
    survey_df = df[df['survey_name'] == survey_name].copy()

    # Sum scores per patient, per follow-up, per survey
    patient_scores_over_time = survey_df.groupby(
        ['patient_number', 'follow_up_number', 'patient_fmt_or_p']
    )['score'].sum().reset_index()

    # Plot lines and error bars for each treatment
    for treatment in ['FMT', 'PLACEBO']:
        treatment_data = patient_scores_over_time[patient_scores_over_time['patient_fmt_or_p'] == treatment]
        
        # Calculate statistics for this treatment
        stats = treatment_data.groupby('follow_up_number')['score'].agg([
            'mean',
            'std'
        ]).reset_index()

        # Plot mean line with error bars
        ax.errorbar(stats['follow_up_number'], 
                   stats['mean'],
                   yerr=stats['std'],
                   color=color_mapping[treatment],
                   linewidth=2,
                   capsize=5,  # Length of error bar caps
                   capthick=2,  # Thickness of error bar caps
                   elinewidth=2,  # Thickness of error bar lines
                   label=f'{treatment} Mean ±1 SD')

    ax.set_title(f'Scores for {survey_name}')
    ax.set_ylabel('Total Score')
    # Ensure all follow-up numbers are shown as ticks
    ax.set_xticks(sorted(patient_scores_over_time['follow_up_number'].unique()))
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

# Set common X-axis label on the last subplot
axes[-1].set_xlabel('Follow Up Number')

# Add a main title to the figure
fig.suptitle('Mean Scores Over Time by Survey and Treatment', fontsize=16)

# Adjust layout to make space for legends and suptitle
plt.tight_layout(rect=[0, 0, 0.90, 0.96]) 

# Create results directory if it doesn't exist
import os
os.makedirs('results', exist_ok=True)

# Save the combined plot
combined_plot_filename = "results/all_surveys_scores_lines_only.png"
plt.savefig(combined_plot_filename)
print(f"Combined plot saved as {combined_plot_filename}")
plt.close(fig) # Close the figure to free memory

print("\nCombined plot generated.") 