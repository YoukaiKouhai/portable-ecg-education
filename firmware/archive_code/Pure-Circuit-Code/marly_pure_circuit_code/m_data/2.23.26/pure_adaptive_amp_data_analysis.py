import numpy as np
import matplotlib.pyplot as plt

FILE_NAME = "pure_adaptive_amp_2.23.26_v7.txt"

# -------- LOAD DATA --------
ecg_values = []

with open(FILE_NAME, 'r') as f:
    for line in f:
        try:
            value = float(line.strip())
            ecg_values.append(value)
        except:
            # Skip non-numeric lines (like sampling rate printouts)
            continue

ecg_values = np.array(ecg_values)

print("Total samples loaded:", len(ecg_values))


# -------- CREATE TIME AXIS --------
# You used delay(2) → ~500 Hz sampling
sampling_rate = 500 # adjust if needed

time = np.arange(len(ecg_values)) / sampling_rate


# -------- PLOT --------
plt.figure(figsize=(12, 5))
plt.plot(time, ecg_values)
plt.title("ECG Signal - Adaptive Amplifier (Kalman Filtered)")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()

# -------- LOAD DATA --------
ecg_values = []

with open(FILE_NAME, 'r') as f:
    for line in f:
        try:
            # If your file has commas (HR, HRV, Signal), take the 3rd index [2]
            # If it is just a single value per line, use float(line.strip())
            parts = line.strip().split(',')
            if len(parts) >= 3:
                value = float(parts[2]) # Taking the Filtered Signal column
            else:
                value = float(parts[0])
            ecg_values.append(value)
        except:
            continue

ecg_values = np.array(ecg_values)
print("Total samples loaded:", len(ecg_values))

# -------- CONSTANTS --------
sampling_rate = 500  # 500 Hz
start_time_seconds = 5
start_index = start_time_seconds * sampling_rate

# -------- CREATE TIME AXIS --------
time = np.arange(len(ecg_values)) / sampling_rate

# -------- PLOT 1: FULL DATA --------
plt.figure(figsize=(12, 10))

plt.subplot(2, 1, 1)
plt.plot(time, ecg_values, color='gray', alpha=0.5)
plt.axvspan(0, start_time_seconds, color='red', alpha=0.1, label='Stabilization Period')
plt.title("Full ECG Signal (Including Initial Noise)")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

# -------- PLOT 2: STABILIZED DATA (AFTER 30 SECONDS) --------
# Slice the data to remove the first 15,000 samples
if len(ecg_values) > start_index:
    clean_time = time[start_index:]
    clean_values = ecg_values[start_index:]

    plt.subplot(2, 1, 2)
    plt.plot(clean_time, clean_values, color='blue')
    plt.title(f"Stabilized ECG Signal (After {start_time_seconds}s)")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True)
else:
    print("Warning: Data is shorter than 30 seconds!")

plt.tight_layout()
plt.show()