import numpy as np
import math
import pandas as pd
import pickle
import ordpy
import os

def createCountyPred(TSDict, dim, timeWindow, numDays):
    predDict = {}
    for key, value in TSDict.items():
        predDict[key] = [1 - ordpy.permutation_entropy(value[x:x+timeWindow], dx=dim) 
                         if sum(math.isnan(el) for el in value[x:x+timeWindow]) <= 3 else np.NaN 
                         for x in range(numDays - timeWindow + 1)]
    return predDict

def load_data(directory, base_name):
    with open(f'{directory}{base_name}_smooth.pickle', 'rb') as handle:
        data = pickle.load(handle)
    return data

# Used in Figure 4
def save_pickle(data, filename):
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

#Used in Figure 5
def calculate_and_save_averages(pred, categories):
    for base_name, category in zip(base_names, categories):
        data_dict = pred[base_name]
        averages = {}
        for county, time_series in data_dict.items():
            averages[county] = pd.Series(time_series).mean()

        avg_data = pd.DataFrame.from_dict(averages, orient='index', columns=['AveragePercentChange'])
        avg_data.reset_index(inplace=True)
        avg_data.rename(columns={'index': 'FIPS'}, inplace=True)
        avg_data['FIPS'] = avg_data['FIPS'].astype(int).astype(str).str.zfill(5)
        avg_data = avg_data.dropna(subset=['AveragePercentChange'])

        csv_file_name = f"average_{category}.csv"
        csv_file_path = os.path.join("./data/intermediate_data/", csv_file_name)
        avg_data.to_csv(csv_file_path, index=False)


timeWindow = 30
dim = 4
numDays = 660

directory = './data/intermediate_data/'

base_names = [
    'countyRetail_And_Recreation',
    'countyGrocery_And_Pharmacy',
    'countyParks',
    'countyTransit_Stations',
    'countyWorkplaces',
    'countyResidential'
]

data = {base_name: load_data(directory, base_name) for base_name in base_names}
pred = {base_name: createCountyPred(data[base_name], dim, timeWindow, numDays) for base_name in base_names}

categories = [
    'RetailAndRecreation',
    'GroceriesAndPharmacies',
    'Parks', 
    'TransitStations',
    'Workplaces',
    'Residences']

calculate_and_save_averages(pred, categories)

for base_name in base_names:
    pickle_filename = f'./data/intermediate_data/{base_name}_smoothed_Predictability.pickle'
    save_pickle(pred[base_name], pickle_filename)

rows_list = []

for month in range(1, 23):
    for category, data in zip(['Retail and Recreation', 'Grocery and Pharmacy', 'Parks', 'Transit Stations', 'Workplaces', 'Residences'], pred.values()):
        for key, value in data.items():
            dict1 = {}
            county = str(int(key)).zfill(5)
            dict1['FIPS'] = county
            dict1['Month'] = month
            dict1['Category'] = category
            dict1['Pred'] = value[30 * (month - 1)]
            if not math.isnan(value[30 * (month - 1)]):
                rows_list.append(dict1)

df = pd.DataFrame(rows_list)

csv_file_path = "./data/intermediate_data/predictability_table.csv"
df.to_csv(csv_file_path, encoding='utf-8', index=False)