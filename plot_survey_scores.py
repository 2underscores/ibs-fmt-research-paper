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


# Get unique survey names
survey_names = df['survey_name'].unique()

# Create a plot for each survey
for survey_name in survey_names:
    plt.figure(figsize=(15, 8))
    survey_df = df[df['survey_name'] == survey_name]

    # Sum scores per patient, per follow-up, per survey
    # This is because each row is a single question's score, not the total survey score.
    # The request "scores on the Y axis" implies a total score for the survey at that follow-up.
    patient_scores_over_time = survey_df.groupby(['patient_number', 'follow_up_number'])['score'].sum().reset_index()

    if patient_scores_over_time.empty:
        print(f"No data to plot for survey: {survey_name} after processing. Skipping.")
        continue

    sns.lineplot(data=patient_scores_over_time, x='follow_up_number', y='score', hue='patient_number', marker='o', legend='full')

    plt.title(f'Scores for {survey_name} vs. Follow Up Number (One Line Per Patient)')
    plt.xlabel('Follow Up Number')
    plt.ylabel('Total Score')
    plt.xticks(sorted(patient_scores_over_time['follow_up_number'].unique())) # Ensure all follow-up numbers are shown as ticks
    
    # Adjust legend position to avoid overlap
    plt.legend(title='Patient Number', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for legend

    # Save the plot
    plot_filename = f"{survey_name.lower().replace(' ', '_').replace('-', '_')}_scores_plot.png"
    plt.savefig(plot_filename)
    print(f"Plot saved as {plot_filename}")
    plt.close() # Close the figure to free memory

print("\nAll plots generated.") 