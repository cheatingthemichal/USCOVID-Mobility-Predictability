import numpy as np
import math
import pandas as pd
import pickle
import ordpy

def createCountyPred(TSDict, dim, timeWindow, numDays, base_name):
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

timeWindow = 30
dim = 4
numDays = 660

directory = '.data/intermediate_data/'

base_names = [
    'countyRetail_And_Recreation',
    'countyGrocery_And_Pharmacy',
    'countyParks',
    'countyTransit_Stations',
    'countyWorkplaces',
    'countyResidential'
]

data = {base_name: load_data(directory, base_name) for base_name in base_names}
pred = {base_name: createCountyPred(data[base_name], dim, timeWindow, numDays, base_name) for base_name in base_names}

rows_list = []

for month in range(1, 23):
    for category, data in zip(['Retail and Recreation', 'Grocery and Pharmacy', 'Parks', 'Transit Stations', 'Workplaces', 'Residences'], pred.values()):
        for key, value in data.items():
            dict1 = {}
            county = str(int(key)).zfill(5)
            dict1['FIPS'] = county
            dict1['Month'] = month
            dict1['Category'] = category
            dict1['PE'] = value[30 * (month - 1)]
            if not math.isnan(value[30 * (month - 1)]):
                rows_list.append(dict1)

df = pd.DataFrame(rows_list)

csv_file_path = "./data/intermediate_data/predictability_table.csv"
df.to_csv(csv_file_path, encoding='utf-8', index=False)