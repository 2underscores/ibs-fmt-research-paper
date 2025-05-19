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

# Get unique survey names
survey_names = sorted(df['survey_name'].unique()) # Sort for consistent order
num_surveys = len(survey_names)

# Create a figure with subplots
# Adjust figsize: width 12, height 5 per subplot
fig, axes = plt.subplots(nrows=num_surveys, ncols=1, figsize=(12, 5 * num_surveys))
if num_surveys == 1: # Ensure axes is always a list for consistent indexing
    axes = [axes]

# Define the style mapping for treatments
# '' is solid, (4, 4) is a dash pattern (4 points on, 4 points off)
style_mapping = {'FMT': '', 'PLACEBO': (4, 4)}

# Create a plot for each survey on its respective subplot
for i, survey_name in enumerate(survey_names):
    ax = axes[i]
    # Use .copy() to avoid SettingWithCopyWarning when potentially modifying survey_df later (though not in this version)
    survey_df = df[df['survey_name'] == survey_name].copy()

    # Sum scores per patient, per follow-up, per survey, including treatment type for styling
    patient_scores_over_time = survey_df.groupby(
        ['patient_number', 'months', 'patient_fmt_or_p']
    )['score'].sum().reset_index()

    if patient_scores_over_time.empty:
        ax.set_title(f'Scores for {survey_name} (No Data)')
        ax.set_ylabel('Total Score')
        print(f"No data to plot for survey: {survey_name} after processing. Skipping subplot.")
        continue

    sns.lineplot(
        data=patient_scores_over_time,
        x='months',
        y='score',
        hue='patient_number',
        style='patient_fmt_or_p',
        dashes=style_mapping, # Apply custom dash styles based on 'patient_fmt_or_p'
        markers=True, # Add markers to data points
        ax=ax,
        legend='full' # Seaborn will generate a combined legend
    )

    ax.set_title(f'Scores for {survey_name}')
    ax.set_ylabel('Total Score')
    # Set x-axis ticks every 2 months from 0 to 12
    ax.set_xticks(np.arange(0, 13, 2))
    ax.set_xlim(-0.5, 12.5)  # Add small padding on both sides
    ax.set_xlabel('Months')  # Add x-axis label to all subplots
    
    # Adjust legend position to avoid overlap with the plot
    # Title for the legend combines patient and treatment info
    ax.legend(title='Patient / Treatment', bbox_to_anchor=(1.02, 1), loc='upper left')

# Add a main title to the figure
fig.suptitle('Patient Scores Over Time by Survey and Treatment', fontsize=16)

# Adjust layout to make space for legends and suptitle
# rect=[left, bottom, right, top] - may need fine-tuning
plt.tight_layout(rect=[0, 0, 0.90, 0.96]) 

# Save the combined plot
combined_plot_filename = "results/all_surveys_scores_plot_combined.png"
plt.savefig(combined_plot_filename)
print(f"Combined plot saved as {combined_plot_filename}")
plt.close(fig) # Close the figure to free memory

print("\nCombined plot generated.") 