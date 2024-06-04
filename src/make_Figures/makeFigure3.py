import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

file_paths = [
    "./data/intermediate_data/countyRetail_And_Recreation.pickle",
    "./data/intermediate_data/countyGrocery_And_Pharmacy.pickle",
    "./data/intermediate_data/countyParks.pickle",
    "./data/intermediate_data/countyTransit_Stations.pickle",
    "./data/intermediate_data/countyWorkplaces.pickle",
    "./data/intermediate_data/countyResidential.pickle",
]

categories = ['Retail and Recreation', 'Groceries and Pharmacies', 'Parks', 'Transit Stations', 'Workplaces', 'Residences']
colors = ['black', 'saddlebrown', 'darkgreen', 'indigo', 'darkred', 'darkblue']

plt.rcParams.update({'font.size': 28})
fig, axs = plt.subplots(2, 3, figsize=(30, 20))

for idx, file_path in enumerate(file_paths):
    with open(file_path, 'rb') as handle:
        data = pickle.load(handle) 

    category_spectra = []

    for key, time_series in data.items():
        time_series = time_series[:631]
        if not np.isnan(time_series).any():
            time_series = time_series - np.mean(time_series)
            n = len(time_series)
            
            # Create custom period array from 1 to 365 days
            custom_periods = np.arange(1, 366)
            
            # Compute the DFT for the custom periods
            custom_dft = np.array([np.sum(time_series * np.exp(-2j * np.pi * (1/p) * np.arange(n))) for p in custom_periods])
            power = (np.abs(custom_dft)**2) / n
            category_spectra.append(power)

    mean_spectrum = np.mean(category_spectra, axis=0) / 1000
    periods = custom_periods

    # Find peaks
    peaks, properties = find_peaks(mean_spectrum, prominence=0.05)
    
    # Select the 4 most prominent peaks
    if len(peaks) > 4:
        sorted_indices = np.argsort(properties['prominences'])[::-1] 
        top_indices = sorted_indices[:4]  # Select the top 4
        peaks = peaks[top_indices]
    
    peak_periods = periods[peaks]
    peak_powers = mean_spectrum[peaks]

    # Find the highest point in the spectrum
    highest_power = np.max(mean_spectrum)
    highest_index = np.argmax(mean_spectrum)
    highest_period = periods[highest_index]

    # Plot
    ax = axs[idx // 3, idx % 3]
    ax.plot(periods, mean_spectrum, color=colors[idx], linewidth=3)
    ax.plot(peak_periods, peak_powers, 'ro')  # Plot peaks
    ax.plot(highest_period, highest_power, 'ro')  # Plot the highest point
    ax.set_title(categories[idx], fontsize=42)
    ax.set_xlabel('Period (days)', fontsize=28)
    ax.set_ylabel('Normalized Power (thousands)', fontsize=28)
    ax.set_xscale('linear')
    ax.set_yscale('linear')

    # Label the peaks with their periods
    for period, power in zip(peak_periods, peak_powers):
        ax.text(period, power, f'{int(period)}', fontsize=16, color='black', ha='left', va='bottom')

    # Label the highest point
    ax.text(highest_period, highest_power, f'{int(highest_period)}', fontsize=16, color='black', ha='left', va='bottom')

plt.subplots_adjust(left=0.07, bottom=0.08, right=0.93, top=0.91, wspace=0.2, hspace=0.2)

save_path_png = "./results/figures/Figure3.png"
plt.savefig(save_path_png, format='png')