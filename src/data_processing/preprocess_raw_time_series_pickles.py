import numpy as np
import pickle

def smooth(TSDict, threshold, remove_outliers):
    smoothed = {}
    window_size = 7
    for key, value in TSDict.items():
        value = value[:660]
        smoothed_values = []
        for i in range(len(value)):
            window_start = max(0, i - window_size // 2)
            window_end = min(len(value), i + window_size // 2 + 1)
            window = value[window_start:window_end]
            window_median = np.median(window)
            if not remove_outliers or abs(value[i] - window_median) < threshold:
                smoothed_values.append(value[i])
            else:
                smoothed_values.append(window_median)
        smoothed[key] = smoothed_values
    return smoothed

def process_pickle_files(pickle_files, base_path, outlier_threshold):
    for file in pickle_files:
        with open(f'{base_path}{file}.pickle', 'rb') as handle:
            data = pickle.load(handle)
        smoothed_data = smooth(data, outlier_threshold, remove_outliers=True)
        with open(f'{base_path}{file}_smooth.pickle', 'wb') as handle:
            pickle.dump(smoothed_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    pickle_files = [
        'countyRetail_And_Recreation',
        'countyGrocery_And_Pharmacy',
        'countyParks',
        'countyTransit_Stations',
        'countyWorkplaces',
        'countyResidential'
    ]
    base_path = './data/intermediate_data/'
    outlier_threshold = 1

    process_pickle_files(pickle_files, base_path, outlier_threshold)
