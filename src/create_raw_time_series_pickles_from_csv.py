import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta

class CountyTimeSeries:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.days = self.generate_days()
        self.county_dicts = self.initialize_dicts()

    def generate_days(self):
        start = datetime.strptime(self.start_date, '%Y-%m-%d')
        end = datetime.strptime(self.end_date, '%Y-%m-%d')
        num_days = (end - start).days + 1
        return [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days)]

    def read_data(self, filename):
        data = pd.read_csv(filename)
        data = data[data.census_fips_code.notnull()]
        return data

    def initialize_dicts(self):
        categories = ['RetailAndRecreation', 'GroceryAndPharmacy', 'Parks', 'TransitStations', 'Workplaces', 'Residences']
        return {category: {} for category in categories}

    def populate_time_series(self, data, year_start_index):
        grouped = data.groupby('census_fips_code')
        for county, group in grouped:
            if county not in self.county_dicts['RetailAndRecreation']:
                for category in self.county_dicts:
                    self.county_dicts[category][county] = [np.nan] * year_start_index
            
            which_day = year_start_index
            for _, row in group.iterrows():
                while self.days[which_day] != row['date']:
                    for category in self.county_dicts:
                        self.county_dicts[category][county].append(np.nan)
                    which_day += 1

                for category in self.county_dicts:
                    self.county_dicts[category][county].append(row[f'{category.lower()}_percent_change_from_baseline'])
                which_day += 1

            while which_day < len(self.days):
                for category in self.county_dicts:
                    self.county_dicts[category][county].append(np.nan)
                which_day += 1

    def clean_data(self):
        bad_counties = {county for county, values in self.county_dicts['RetailAndRecreation'].items() if all(np.isnan(values))}
        for category in self.county_dicts:
            for county in bad_counties:
                if county in self.county_dicts[category]:
                    del self.county_dicts[category][county]

    def save_pickle(self, directory):
        for category, data in self.county_dicts.items():
            with open(f'{directory}/county{category}.pickle', 'wb') as handle:
                pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def create_county_time_series(filenames, output_directory):
    start_dates = ['2020-02-15', '2021-01-01', '2022-01-01']
    end_date = '2022-07-26'
    year_start_indices = [0, 321, 686]  # Starting index for each year in the full date range

    cts = CountyTimeSeries('2020-02-15', end_date)
    
    for filename, year_start_index in zip(filenames, year_start_indices):
        data = cts.read_data(filename)
        cts.populate_time_series(data, year_start_index)

    cts.clean_data()
    cts.save_pickle(output_directory)

if __name__ == "__main__":
    filenames = [
        "F:/Pei/DATA/US_PERCENT_CHANGE_FINAL/2020_US_Region_Mobility_Report.csv",
        "F:/Pei/DATA/US_PERCENT_CHANGE_FINAL/2021_US_Region_Mobility_Report.csv",
        "F:/Pei/DATA/US_PERCENT_CHANGE_FINAL/2022_US_Region_Mobility_Report.csv"
    ]
    output_directory = "F:/Pei/DATA/US_PERCENT_CHANGE_FINAL"
    create_county_time_series(filenames, output_directory)
