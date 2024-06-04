import numpy as np
import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

file_paths = [
    "./data/intermediate_data/countyRetail_And_Recreation_smooth.pickle",
    "./data/intermediate_data/countyGrocery_And_Pharmacy_smooth.pickle",
    "./data/intermediate_data/countyParks_smooth.pickle",
    "./data/intermediate_data/countyTransit_Stations_smooth.pickle",
    "./data/intermediate_data/countyWorkplaces_smooth.pickle",
    "./data/intermediate_data/countyResidential_smooth.pickle",
]

categories = ['Retail and Recreation', 'Groceries and Pharmacies', 'Parks', 'Transit Stations', 'Workplaces', 'Residences']
colors = ['black', 'brown', 'green', 'purple', 'red', 'blue']

all_data = []
labels = []

for idx, file_path in enumerate(file_paths):
    with open(file_path, 'rb') as handle:
        county_data = pickle.load(handle) 
        for key, value in county_data.items():
            if not any(np.isnan(value)):
                all_data.append(value)
                labels.append(colors[idx])

# Convert to DataFrame and drop any rows with NaNs (if any)
all_data = pd.DataFrame(all_data).dropna()

# Standardize the data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(all_data)

# Apply t-SNE
tsne = TSNE(n_components=2, random_state=42)
data_reduced = tsne.fit_transform(data_scaled)

plt.figure(figsize=(14, 10))  # Increase the figure size

# Plotting
for i, category in enumerate(categories):
    idx = [index for index, val in enumerate(labels) if val == colors[i]]
    plt.scatter(data_reduced[idx, 0], data_reduced[idx, 1], c=colors[i], label=category, alpha=0.5)

plt.title('t-SNE Visualization of Processed County-Level Community Mobility Reports Data', fontsize=17)
plt.xlabel('t-SNE Dimension 1', fontsize=13)
plt.ylabel('t-SNE Dimension 2', fontsize=13)
plt.legend(loc='upper left', fontsize=13)

save_path_png = "./results/figures/Figure2A.png"
plt.savefig(save_path_png, format='png')