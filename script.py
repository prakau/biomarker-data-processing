import pandas as pd
import pickle
import numpy as np
from scipy.signal import correlate

# Paths to the data files
metadata_file = 'X_Metadata.xlsx'
raw_data_file = 'x_raw.pickle'
background_data_file = 'X_background.pickle'

# Function to load data from pickle files
def load_pickle(file_path):
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

# Load metadata
metadata = pd.read_excel(metadata_file)
print("Metadata Loaded")
print(metadata.head())

# Load raw data
raw_data = load_pickle(raw_data_file)
if raw_data is None:
    print("Failed to load raw data.")
    exit()
print("Raw Data Keys:", raw_data.keys())

# Load background data
background_data = load_pickle(background_data_file)
if background_data is None:
    print("Failed to load background data.")
    exit()
print("Background Data Keys:", background_data.keys())

# Function to normalize data
def normalize_data(data):
    if data is None or len(data) == 0:
        return None
    mean = np.mean(data, axis=0)
    std = np.std(data, axis=0)
    return (data - mean) / std

# Normalize data
normalized_raw_data = {key: normalize_data(value['matrix']) for key, value in raw_data.items()}
normalized_background_data = {key: normalize_data(value['matrix']) for key, value in background_data.items()}
print("Normalized Raw Data Sample:\n", next(iter(normalized_raw_data.values())))
print("Normalized Background Data Sample:\n", next(iter(normalized_background_data.values())))

# Function to align scans using cross-correlation
def align_scans(scan1, scan2):
    if scan1 is None or scan2 is None:
        return None
    correlation = correlate(scan1, scan2, mode='full')
    shift_index = np.argmax(correlation) - (len(scan1) - 1)
    aligned_scan2 = np.roll(scan2, shift_index, axis=0)
    return aligned_scan2

# Filter metadata to include only available keys
available_keys = set(normalized_raw_data.keys()).intersection(set(metadata['filename']))
filtered_metadata = metadata[metadata['filename'].isin(available_keys)]
print("Filtered Metadata:\n", filtered_metadata)

# Aligning the scans
aligned_raw_data = {}
for sensor in filtered_metadata['filename'].str.split('_').str[0].unique():
    scans = [normalized_raw_data.get(f"{sensor}_{i}") for i in range(3)]
    print(f"Aligning scans for sensor {sensor}: {scans}")
    if all(scan is not None for scan in scans):
        aligned_scans = [scans[0]]
        for scan in scans[1:]:
            aligned_scan = align_scans(aligned_scans[0], scan)
            if aligned_scan is not None:
                aligned_scans.append(aligned_scan)
            else:
                print(f"Failed to align scan for sensor {sensor}.")
        aligned_raw_data[sensor] = np.mean(aligned_scans, axis=0)
    else:
        print(f"Skipping sensor {sensor} due to missing scan data.")
print("Aligned Raw Data Keys:", aligned_raw_data.keys())

# Debugging: Print aligned raw data for verification
for sensor, data in aligned_raw_data.items():
    print(f"Aligned Data for {sensor}:\n", data)

# Subtracting the background
background_subtracted_data = {}
for sensor in aligned_raw_data.keys():
    raw_scan = aligned_raw_data[sensor]
    background_scan = normalized_background_data.get(sensor, np.zeros_like(raw_scan))
    print(f"Processing sensor: {sensor}")
    print(f"Raw Scan Available: {raw_scan is not None}")
    print(f"Background Scan Available: {background_scan is not None}")
    if raw_scan is not None:
        subtracted_scan = raw_scan - background_scan
        subtracted_scan[subtracted_scan < 0] = 0  # Replace negative values with zero
        background_subtracted_data[sensor] = subtracted_scan
    else:
        print(f"Skipping sensor {sensor} due to missing raw scan data.")
print("Background Subtracted Data Keys:", background_subtracted_data.keys())

# Aggregating data from the same sensor
aggregated_data = {}
for sensor in background_subtracted_data.keys():
    aggregated_data[sensor] = background_subtracted_data[sensor]
print("Aggregated Data Keys:", aggregated_data.keys())

# Convert the processed data back to the same structure as the original raw data
processed_data = {key: {'matrix': value} for key, value in aggregated_data.items()}

# Save the processed data to a CSV file
output_csv_file = 'processed_biomarker_x_data_cleaned.csv'
processed_data_df = pd.DataFrame.from_dict({key: value['matrix'].flatten() for key, value in processed_data.items()}, orient='index')
processed_data_df.to_csv(output_csv_file)
print(f"Processed data saved to {output_csv_file}")
