# Summary
Poo from one place to another.

# AI Prompt
## Background
I am a research student writing a paper on the effects if FMT (fecal microbiota transplant).

I am doing a study where i get around 20 patients with IBS to undergo FMT treatment over the course of 5 sessions (an initial session and 4 follow ups).

Some of the patients are given real FMT, others are given a placebo. Each session the patients complete 3 surveys (DASS, IBS-QoL and IBS-SSS) to record how they are feeling about their IBS and different attributes of it. The survey results are turned into scores. 

I am looking to see if the FMT performs better than the placebo in helping patients decrease their scores or do not perform differently to the placebo.

## Data
In the file ibs-all-patients-flat-scores.csv you will find the data in tablular form, with each row representing patients answer/score on a single question, from a single survey, on a single session.

Description of each header:
- survey_name: Which of the three surveys the question is from
- q_number: Number of question in that survey
- q_id: ID of question, unique across all surveys
- q_category: Category of question, for more granular scores
- patient_number: ID of patient HC01 to HC21
- patient_fmt_or_placebo: Whether patient was on FMT or placebo
- follow_up_number: Which session patient was on. 0 being first, 4 being last.
- answer: What they answered to the question
- score: The score given to that answer

Additionally there are two other files:
- all-survey-questions: Reference list of all questions from all surveys
- patient-fmt-or-placebo: List of patients and if they are on FMT or placebo

Both these are included in every row of the ibs-all-patients-flat-scores.csv file, however they are duplicated on every row and these two files are just normalised versions of that specific data (per patient and per survey data).

## My Task
I need to make some nice looking graphs for my research paper and also perform the Wilcoxon signed rank test to see if FMT is having an impact greater than the placebo.
