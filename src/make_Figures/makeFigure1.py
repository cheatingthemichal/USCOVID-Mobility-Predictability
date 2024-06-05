import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import math
import matplotlib.dates as mdates
from datetime import datetime as D
from matplotlib.ticker import FixedLocator

# Initialize time variables
timeWindow = 30
startDate = '2020-02-15'
endDate = '2021-12-05'
date_format = "%Y-%m-%d"
start = D.strptime(startDate, date_format)
end = D.strptime(endDate, date_format)
numDays = (end - start).days + 1
lengthFinal = numDays - timeWindow + 1

# Create times array with correct length
times = pd.date_range(start=startDate, end=endDate, periods=numDays)

# Function to calculate empirical confidence intervals
def mean_confidence_interval_empirical(data, CI_amount):
    lower_bound = np.percentile(data, (100 - CI_amount)/2)
    upper_bound = np.percentile(data, 100 - (100 - CI_amount)/2)
    return np.mean(data), lower_bound, upper_bound

def calculate_avg_and_ci(county_data, CI_amounts=[90, 50]):
    net = [0] * numDays
    ci_low_90 = [0] * numDays
    ci_high_90 = [0] * numDays
    ci_low_50 = [0] * numDays
    ci_high_50 = [0] * numDays
    min_counties = float('inf')
    max_counties = 0
    
    for i in range(numDays):
        daily_values = [value[i] for value in county_data.values() if not math.isnan(value[i])]
        num_counties = len(daily_values)
        if num_counties:
            mean, lower_bound_90, upper_bound_90 = mean_confidence_interval_empirical(daily_values, CI_amounts[0])
            _, lower_bound_50, upper_bound_50 = mean_confidence_interval_empirical(daily_values, CI_amounts[1])
            net[i] = mean
            ci_low_90[i] = lower_bound_90
            ci_high_90[i] = upper_bound_90
            ci_low_50[i] = lower_bound_50
            ci_high_50[i] = upper_bound_50
            min_counties = min(min_counties, num_counties)
            max_counties = max(max_counties, num_counties)
        else:
            net[i] = float('nan')
            ci_low_90[i] = float('nan')
            ci_high_90[i] = float('nan')
            ci_low_50[i] = float('nan')
            ci_high_50[i] = float('nan')

    return net, ci_low_90, ci_high_90, ci_low_50, ci_high_50, min_counties, max_counties

file_paths = [
    "./data/intermediate_data/countyRetail_And_Recreation_smooth.pickle",
    "./data/intermediate_data/countyGrocery_And_Pharmacy_smooth.pickle",
    "./data/intermediate_data/countyParks_smooth.pickle",
    "./data/intermediate_data/countyTransit_Stations_smooth.pickle",
    "./data/intermediate_data/countyWorkplaces_smooth.pickle",
    "./data/intermediate_data/countyResidential_smooth.pickle",
]

county_data = []

for file_path in file_paths:
    with open(file_path, 'rb') as handle:
        county_data.append(pickle.load(handle))

processed_data = []

titles = ['Retail and Recreation',
          'Groceries and Pharmacies',
          'Parks',
          'Transit Stations',
          'Workplaces',
          'Residences']

for index, data in enumerate(county_data):
    avg_data, ci_low_90, ci_high_90, ci_low_50, ci_high_50, min_counties, max_counties = calculate_avg_and_ci(data)
    processed_data.append((avg_data, ci_low_90, ci_high_90, ci_low_50, ci_high_50))
    print(f"{titles[index]}: Min Counties = {min_counties}, Max Counties = {max_counties}")

plt.rcParams.update({'font.size': 28})
fig, axs = plt.subplots(2, 3, figsize=(30, 20))
important_dates = ["2020-03-01", "2021-01-01", "2021-11-01"]
tick_dates = pd.to_datetime(important_dates)

for i, ax in enumerate(axs.flat):
    avg_data, ci_low_90, ci_high_90, ci_low_50, ci_high_50 = processed_data[i]
    ax.tick_params(axis='x', which='major', pad=10)
    ax.tick_params(axis='y', which='major', pad=10)
    ax.fill_between(times, ci_low_90, ci_high_90, color='cornflowerblue', label='90% Confidence Interval')
    ax.fill_between(times, ci_low_50, ci_high_50, color='blue', label='50% Confidence Interval')
    ax.plot(times, avg_data, color='black', label='Mean', linewidth=3)
    ax.set_title(titles[i], fontsize = 42)
    ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(tick_dates)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.set_xlabel("Date (day)", fontsize=28) 
    if i % 3 == 0:
        ax.set_ylabel("Percent change in mobility from baseline (%)", fontsize=28)

plt.subplots_adjust(left=0.07,
                    bottom=0.08,
                    right=0.98,
                    top=0.91,
                    wspace=0.2,
                    hspace=0.4)
plt.legend()

save_path_png = "./results/figures/Figure1.png"
plt.savefig(save_path_png, format='png')