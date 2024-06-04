# USCOVID-Mobility-Predictability
"Predictability of human mobility during the COVID-19 pandemic in the United States" Code and Data

Michal Hajlasz and Sen Pei

The Google COVID-19 Community Mobility Reports data and a dataframe containing our analysis' features are in the data/raw_data directory.

Pickle files used to create some figures are in the data/intermediate_data directory.

Dataframes used for our GAM analysis are in the data/data_for_GAM directory.

All of the files in the data/intermediate_data and data/data_for_GAM directories can be created from the files in the data/raw_data directory by the running the scripts in src/data_processing in the following order:

    python ./src/data_processing/create_raw_time_series_pickles_from_csv.py
    python ./src/data_processing/preprocess_raw_time_series_pickles.py
    python ./src/data_processing/create_pred_table.py
    python ./src/data_processing/create_tables_for_GAM.py

In particular, outliers in the % change in mobility time series are removed in data_processing/preprocess_raw_time_series_pickles.py and predictability is calculated in src/data_processing/create_pred_table.py

Select figures from our paper are in the results/figures directory and can be created by running their respective scripts in the src/make_Figures directory.

TODO. GAM_analysis.R

and the results are outputed in results/GAM_summary.txt