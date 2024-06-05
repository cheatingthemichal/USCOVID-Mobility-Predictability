import pandas as pd

features_csv_path = "./data/raw_data/features_table.csv"
pe_csv_path = "./data/intermediate_data/predictability_table.csv"

features_df = pd.read_csv(features_csv_path, dtype={'FIPS': str})
pe_df = pd.read_csv(pe_csv_path, dtype={'FIPS': str})

categories = ['Retail and Recreation',
    'Grocery and Pharmacy',
    'Parks',
    'Transit Stations',
    'Workplaces',
    'Residences']

for category in categories:
    category_pe_df = pe_df[pe_df['Category'] == category]

    merged_df = pd.merge(category_pe_df, features_df, on=['FIPS', 'Month'])

    output_csv_path = f"./data/data_for_GAM/{category.replace(' ', '_')}_table_for_GAM.csv"
    merged_df.to_csv(output_csv_path, encoding='utf-8', index=False)
