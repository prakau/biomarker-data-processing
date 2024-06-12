# Biomarker Data Processing

This project processes biomarker concentration data to handle drift and background noise, ensuring accurate and reliable readings. The script normalizes the data, aligns the scans, subtracts the background signal, and handles negative values appropriately.

## Files

- `BiomarkerX_Metadata.xlsx`: Metadata for the biomarker samples.
- `bio_x_raw.pickle`: Raw data samples.
- `bio_x_background.pickle`: Background data samples.

## Steps

1. **Normalize Data:** Standardizes the data for consistency.
2. **Align Scans:** Uses cross-correlation to align scans from the same sensor.
3. **Subtract Background:** Removes the background signal from the raw data.
4. **Handle Negative Values:** Replaces negative values with zero.
5. **Aggregate Data:** Combines data from the same sensor to enhance robustness.

## Usage

1. Place the metadata, raw data, and background data files in the same directory as the script.
2. Run the script using Python 3.

```sh
python script.py
```

## Dependencies

Install the required packages using:

```sh
pip install -r requirements.txt
```

## Output

The processed data is saved to `processed_biomarker_x_data_cleaned.csv`.
