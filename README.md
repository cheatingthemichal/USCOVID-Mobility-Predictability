# USCOVID-Mobility-Predictability
"Predictability of human mobility during the COVID-19 pandemic in the United States" Code and Data

Michal Hajlasz and Sen Pei

This repository uses Git Large File Storage (LFS) to manage large files. To properly clone the repository and fetch all the LFS files, ensure that you have Git LFS installed on your machine (https://git-lfs.com/).

Then initialize Git LFS with:

    git lfs install

Clone the repository using the standard git clone command:

    git clone https://github.com/cheatingthemichal/USCOVID-Mobility-Predictability.git

After cloning the repository, navigate to the repository directory and pull the LFS files:

    cd repo
    git lfs pull

The Google COVID-19 Community Mobility Reports data, a dataframe containing our analysis' features, and an rds file containing data related to the geographical centroids of counties used in our GAM, are in the data/raw_data directory.

Files used to create figures are in the data/intermediate_data directory.

Dataframes used for our GAM analysis are in the data/data_for_GAM directory.

All of the files in the data/intermediate_data and data/data_for_GAM directories can be created from the files in the data/raw_data directory by the running the scripts in src/data_processing in the following order:

    python ./src/data_processing/create_raw_time_series_pickles_from_csv.py
    python ./src/data_processing/preprocess_raw_time_series_pickles.py
    python ./src/data_processing/calculate_predictability.py
    python ./src/data_processing/create_tables_for_GAM.py

In particular, outliers in the % change in mobility time series are removed in src/data_processing/preprocess_raw_time_series_pickles.py and predictability is calculated in src/data_processing/calculate_predictability.py

All main figures from our paper are in the results/figures directory and can be created by running their respective scripts in the src/make_Figures directory.

Run src/GAM_analysis.R to print a summary of our model for each category to results/gam_summaries.txt. The p-values indicates the probability that the observed association occurred by chance. A low p-value (<0.05) suggests a statistically significant relationship. The F-value measures the ratio of the variance explained by the model to the variance due to error. Higher F-values indicate a stronger influence of the predictor on the response variable. The adjusted R-squared value reflects the proportion of the variance in the response variable explained by the model, adjusted for the number of predictors.