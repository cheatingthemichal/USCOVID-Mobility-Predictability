import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
import matplotlib.dates as mdates
from matplotlib.ticker import FixedLocator


def mean_confidence_interval_empirical(data, CI_amount):
    lower_bound = np.percentile(data, (100 - CI_amount)/2)
    upper_bound = np.percentile(data, 100 - (100 - CI_amount)/2)
    return np.mean(data), lower_bound, upper_bound

def process_time_series_data(county_data, category_name):
    net_data = {}
    low_data_90 = np.empty(lengthFinal)
    high_data_90 = np.empty(lengthFinal)
    low_data_50 = np.empty(lengthFinal)
    high_data_50 = np.empty(lengthFinal)
    med_data = np.empty(lengthFinal)
    min_counties = None
    max_counties = None

    for i in range(lengthFinal):
        net_data[i] = []

    for i in range(lengthFinal):
        for value in county_data.values():
            if not math.isnan(value[i]):
                net_data[i].append(value[i])

        # Update the minimum number of counties
        if min_counties is None or len(net_data[i]) < min_counties:
            min_counties = len(net_data[i])
        if max_counties is None or len(net_data[i]) > max_counties:
            max_counties = len(net_data[i])

    for i in range(lengthFinal):
        med_data[i], low_data_90[i], high_data_90[i] = mean_confidence_interval_empirical(net_data[i], 90)
        _, low_data_50[i], high_data_50[i] = mean_confidence_interval_empirical(net_data[i], 50)

    print(f"{category_name}: Min Counties = {min_counties}, Max Counties = {max_counties}")

    return low_data_90, med_data, high_data_90, low_data_50, high_data_50

file_paths = [
    "./data/intermediate_data/countyRetail_And_Recreation_smoothed_Predictability.pickle",
    "./data/intermediate_data/countyGrocery_And_Pharmacy_smoothed_Predictability.pickle",
    "./data/intermediate_data/countyParks_smoothed_Predictability.pickle",
    "./data/intermediate_data/countyTransit_Stations_smoothed_Predictability.pickle",
    "./data/intermediate_data/countyWorkplaces_smoothed_Predictability.pickle",
    "./data/intermediate_data/countyResidential_smoothed_Predictability.pickle",
]

county_data = []

for file_path in file_paths:
    with open(file_path, 'rb') as handle:
        county_data.append(pickle.load(handle))

lengthFinal = 631

low_data_90 = []
med_data = []
high_data_90 = []
low_data_50 = []
high_data_50 = []
titles = ['Retail and Recreation', 'Groceries and Pharmacies', 'Parks', 'Transit Stations', 'Workplaces', 'Residences']

for index, data in enumerate(county_data):
    low_90, med, high_90, low_50, high_50 = process_time_series_data(data, titles[index])
    low_data_90.append(low_90)
    med_data.append(med)
    high_data_90.append(high_90)
    low_data_50.append(low_50)
    high_data_50.append(high_50)

times = pd.date_range(start='2020-02-15', end='2021-11-07', periods=lengthFinal)

plt.rcParams.update({'font.size': 28})
fig, axs = plt.subplots(2, 3, figsize=(30, 20))
important_dates = ["2020-03-01", "2021-01-01", "2021-11-01"]
tick_dates = pd.to_datetime(important_dates)
titles = ['Retail and Recreation', 'Groceries and Pharmacies', 'Parks', 'Transit Stations', 'Workplaces', 'Residences']

for i, ax in enumerate(axs.flat):
    ax.tick_params(axis='x', which='major', pad=10)
    ax.tick_params(axis='y', which='major', pad=10)
    ax.fill_between(times, low_data_90[i], high_data_90[i], color='peachpuff', label='90% Confidence Interval')
    ax.fill_between(times, low_data_50[i], high_data_50[i], color='chocolate', label='50% Confidence Interval')
    ax.plot(times, med_data[i], color='black', label='Mean', linewidth=3)
    
    ax.set_title(titles[i], fontsize = 42)

    ax.xaxis.set_major_locator(FixedLocator(mdates.date2num(tick_dates)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.set_xlabel("Date (day)", fontsize=28)
    if i % 3 == 0:
        ax.set_ylabel("Predictability of mobility", fontsize=29)

plt.subplots_adjust(left=0.07,
                    bottom=0.08,
                    right=0.98,
                    top=0.91,
                    wspace=0.2,
                    hspace=0.3)
plt.legend()

save_path_png = "./results/figures/Figure4.png"
plt.savefig(save_path_png, format='png')