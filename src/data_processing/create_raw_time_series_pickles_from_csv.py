import numpy as np
import pandas as pd
import pickle
from datetime import timedelta, datetime

START_OF_2020 = '2020-02-15'
END_OF_2020 = '2020-12-31'
START_OF_2021 = '2021-01-01'
END_OF_2021 = '2021-12-31'
START_OF_2022 = '2022-01-01'
END_OF_2022 = '2022-07-26'

date_format = '%Y-%m-%d'
start = datetime.strptime(START_OF_2020, date_format)
end = datetime.strptime(END_OF_2022, date_format)
numDays = (end - start).days + 2

days = [(start + timedelta(days=i)).strftime(date_format) for i in range(numDays)]

def add_missing_days(county_data, numDays):
    county_data.extend([np.NAN] * numDays)

def populate_time_series(county_dicts, group, start_index, end_date):
    whichDayIsIt = start_index
    for index, row in group.iterrows():
        while days[whichDayIsIt] != row['date']:
            intendedDay = datetime.strptime(days[whichDayIsIt], date_format)
            actualDay = datetime.strptime(row['date'], date_format)
            numDays = (actualDay - intendedDay).days
            for county_data in county_dicts.values():
                add_missing_days(county_data, numDays)
            whichDayIsIt += numDays
        for category, county_data in county_dicts.items():
            county_data.append(row[category])
        whichDayIsIt += 1
    intendedLastDay = datetime.strptime(end_date, date_format)
    actualLastDay = datetime.strptime(days[whichDayIsIt], date_format)
    numMissingDays = (intendedLastDay - actualLastDay).days + 1
    for county_data in county_dicts.values():
        add_missing_days(county_data, numMissingDays)

def createCountyTS(filename2020, filename2021, filename2022):
    table2020 = pd.read_csv(filename2020)
    table2021 = pd.read_csv(filename2021)
    table2022 = pd.read_csv(filename2022)

    #REMOVE ROWS WHERE FIPS = NAN
    table2020 = table2020[table2020.census_fips_code.notnull()]
    table2021 = table2021[table2021.census_fips_code.notnull()]
    table2022 = table2022[table2022.census_fips_code.notnull()]

    categories = [
        'retail_and_recreation_percent_change_from_baseline',
        'grocery_and_pharmacy_percent_change_from_baseline',
        'parks_percent_change_from_baseline',
        'transit_stations_percent_change_from_baseline',
        'workplaces_percent_change_from_baseline',
        'residential_percent_change_from_baseline'
    ]

    county_dicts = {category: {} for category in categories}

    #INIT EACH TIME SERIES AS AN EMPTY LIST
    grouped2020 = table2020.groupby('census_fips_code')
    for county, group in grouped2020:
        for category in categories:
            county_dicts[category][county] = []

    #POPULATE TIME SERIES WITH VALUES FOR 2020
    for county, group in grouped2020:
        populate_time_series({cat: county_dicts[cat][county] for cat in categories}, group, 0, END_OF_2020)

    #POPULATE TIME SERIES WITH VALUES FOR 2021
    grouped2021 = table2021.groupby('census_fips_code')
    for county, group in grouped2021:
        if county in county_dicts[categories[0]]:
            populate_time_series({cat: county_dicts[cat][county] for cat in categories}, group, 321, END_OF_2021)

    #POPULATE TIME SERIES WITH VALUES FOR 2022
    grouped2022 = table2022.groupby('census_fips_code')
    for county, group in grouped2022:
        if county in county_dicts[categories[0]]:
            populate_time_series({cat: county_dicts[cat][county] for cat in categories}, group, 686, END_OF_2022)

    #REMOVE COUNTIES THAT APPEAR IN 2021/2022 BUT NOT EARLIER 
    setOfBadCounties = set()
    for key, value in county_dicts[categories[0]].items():
        if value == [np.NAN] * 893 or len(value) != 893:
            setOfBadCounties.add(key)
    for county_data in county_dicts.values():
        for key in setOfBadCounties:
            if key in county_data:
                del county_data[key]
    
    #LOAD DICTS TO PICKLES
    for category, county_data in county_dicts.items():
        with open(f'./data/intermediate_data/county{category.replace("_percent_change_from_baseline", "").title()}.pickle', 'wb') as handle:
            pickle.dump(county_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

createCountyTS("./data/raw_data/2020_US_Region_Mobility_Report.csv",
    "./data/raw_data/2021_US_Region_Mobility_Report.csv",
    "./data/raw_data/2022_US_Region_Mobility_Report.csv")
