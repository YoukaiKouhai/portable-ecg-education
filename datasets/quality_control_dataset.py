import os
import re
from datetime import datetime
import numpy as np
import pandas as pd
from scipy import stats

# --- CONFIGURATION ---
TARGET_PREFIX = "RUN"
FILE_NAME = "raw_6lead.csv"
LEAD_COLUMNS = ["leadI", "leadII", "leadIII", "aVR", "aVL", "aVF"]


def is_data_good(file_path):
    """Evaluates the quality of the ECG data.

    Returns True if good, False if bad.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Check if all required lead columns exist
        if not all(col in df.columns for col in LEAD_COLUMNS):
            print(f"  [!] Missing required ECG lead columns in {file_path}")
            return False

        # Require enough rows to evaluate quality
        if len(df) < 10:
            print(f"  [!] Bad Quality: Not enough rows ({len(df)}) in {file_path}.")
            return False

        # --- QUALITY CHECKS ---
        for col in LEAD_COLUMNS:
            signal = pd.to_numeric(df[col], errors="coerce")
            signal = signal.dropna()

            if signal.empty:
                print(f"  [!] Bad Quality: Lead {col} has no numeric samples.")
                return False

            # 1. Check for flatlines (Standard Deviation near 0 means no signal)
            if signal.std() < 1.0:
                print(f"  [!] Bad Quality: Flatline detected in {col}.")
                return False

            # 2. Check for extreme noise/spikes (Z-score outlier check)
            if len(signal) >= 2:
                z_scores = np.abs(stats.zscore(signal))
                if np.nanmax(z_scores) > 10:
                    print(f"  [!] Bad Quality: Extreme noise/spikes in {col}.")
                    return False

            # 3. Check for missing data (NaNs)
            missing_ratio = df[col].isnull().sum() / len(df)
            if missing_ratio > 0.1:
                print(f"  [!] Bad Quality: Too many missing values in {col} ({missing_ratio:.0%}).")
                return False

        return True

    except Exception as e:
        print(f"  [!] Error reading file {file_path}: {e}")
        return False


def find_ecg_file(folder_path):
    raw_path = os.path.join(folder_path, FILE_NAME)
    if os.path.exists(raw_path):
        return raw_path

    for entry in os.listdir(folder_path):
        if entry.lower().endswith(".csv"):
            return os.path.join(folder_path, entry)

    return None


def rename_run_folders():
    # Use the script directory so the script works even when run from another folder
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Find all items in the directory
    for item in os.listdir(current_dir):
        item_path = os.path.join(current_dir, item)

        # Check if it's a directory and starts with "RUN"
        if os.path.isdir(item_path) and item.startswith(TARGET_PREFIX):
            csv_path = find_ecg_file(item_path)
            if csv_path is None:
                print(f"Skipping {item}: no CSV ECG file found inside.")
                continue

            print(f"Processing folder: {item} using file {os.path.basename(csv_path)}...")

            # Evaluate data quality
            if is_data_good(csv_path):
                # Use creation time when available, fallback to modification time
                timestamp = os.path.getctime(csv_path)
                if timestamp == 0:
                    timestamp = os.path.getmtime(csv_path)
                dt_object = datetime.fromtimestamp(timestamp)

                # Format as YYYYMMDD_HHMMSS (safe for folder names across OS)
                new_folder_name = dt_object.strftime("%Y-%m-%d_%H-%M-%S")
                new_folder_path = os.path.join(current_dir, new_folder_name)

                # Handle potential folder name collisions
                counter = 1
                original_new_path = new_folder_path
                while os.path.exists(new_folder_path):
                    new_folder_path = f"{original_new_path}_{counter}"
                    counter += 1

                # Rename the folder
                os.rename(item_path, new_folder_path)
                print(
                    f"  [+] Success! Renamed '{item}' to '{os.path.basename(new_folder_path)}'"
                )
            else:
                print(
                    f"  [-] Keeping original name '{item}' due to poor data quality."
                )


if __name__ == "__main__":
    rename_run_folders()