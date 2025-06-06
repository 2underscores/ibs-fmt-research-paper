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

# Create mapping from follow-up number to months
follow_up_to_months = {
    0: 0,   # baseline
    1: 1,   # 1 month
    2: 3,   # 3 months
    3: 6,   # 6 months
    4: 12   # 12 months
}

# Add months column to dataframe
df['months'] = df['follow_up_number'].map(follow_up_to_months)

# Filter for only first (0) and last (4) follow-up numbers
df = df[df['follow_up_number'].isin([0, 4])]

if df.empty:
    print("Error: No data available for follow-up 0 or 4. Cannot generate plot.")
    exit()

# Get unique survey names
survey_names = sorted(df['survey_name'].unique())
num_surveys = len(survey_names)

if num_surveys == 0:
    print("Error: No survey data found after filtering for follow-ups 0 and 4.")
    exit()

# Create a figure with subplots (side-by-side)
# Adjusted figsize for narrower and taller individual plots (e.g., each ~4 wide, 6 tall)
fig, axes = plt.subplots(nrows=1, ncols=num_surveys, figsize=(3 * num_surveys, 7), sharey=False)
if num_surveys == 1: # Ensure axes is always an array-like for consistent indexing
    axes = [axes]

# Define the style mapping for treatments
style_mapping = {'FMT': '', 'PLACEBO': (4, 4)} # Solid for FMT, dashed for Placebo

# Create a plot for each survey on its respective subplot
for i, survey_name in enumerate(survey_names):
    ax = axes[i]
    survey_df = df[df['survey_name'] == survey_name].copy()

    patient_scores_over_time = survey_df.groupby(
        ['patient_number', 'months', 'patient_fmt_or_p']
    )['score'].sum().reset_index()

    if patient_scores_over_time.empty:
        ax.set_title(f'{survey_name}\n(No Data for FU 0/4)')
        if i == 0:
            ax.set_ylabel('Total Score')
        ax.set_xticks([0, 12])  # Changed to show 0 and 12 months
        print(f"No data to plot for survey: {survey_name} for follow-ups 0 and 4. Skipping subplot content.")
        continue

    sns.lineplot(
        data=patient_scores_over_time,
        x='months',  # Changed from follow_up_number to months
        y='score',
        hue='patient_number',
        style='patient_fmt_or_p',
        dashes=style_mapping,
        markers=True,
        ax=ax,
        legend=False
    )

    ax.margins(0.4)

    ax.set_title(f'{survey_name}')
    ax.set_xticks([0, 12])  # Changed to show 0 and 12 months
    
    if i == 0:
        ax.set_ylabel('Total Score')
    else:
        ax.set_ylabel('')

    if num_surveys > 1 and i == num_surveys // 2:
        ax.set_xlabel('Months')  # Updated label
    elif num_surveys == 1:
        ax.set_xlabel('Months')  # Updated label
    else:
        ax.set_xlabel('')

# Add a main title to the figure
fig.suptitle('Patient Scores: Baseline (0 months) vs. End (12 months) by Survey', fontsize=16)  # Updated title

# Create a custom legend for just FMT vs Placebo
# Create dummy lines for the legend
fmt_line = plt.Line2D([0], [0], color='gray', linestyle='-', label='FMT')
placebo_line = plt.Line2D([0], [0], color='gray', linestyle='--', label='Placebo')

# Add the figure-level legend
fig.legend([fmt_line, placebo_line], ['FMT', 'Placebo'],
          loc='center', 
          bbox_to_anchor=(0.5, 0.02),
          ncol=2,
          title='Treatment Type')

# Adjust subplot parameters for better spacing and to accommodate suptitle and legend
fig.subplots_adjust(left=0.07, right=0.97, bottom=0.25, top=0.90, wspace=0.35)

# Save the combined plot
combined_plot_filename = "results/all_surveys_start_end_plot.png"
plt.savefig(combined_plot_filename, bbox_inches='tight')
print(f"Combined plot saved as {combined_plot_filename}")
plt.close(fig)

print("\nStart-to-end plot generated with adjusted aesthetics and margins.") 