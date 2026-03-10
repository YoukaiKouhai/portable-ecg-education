import numpy as np
import matplotlib.pyplot as plt

# ---------- SETTINGS ----------
FILE_NAME = "pure_adaptive_amp_2.23.26_v1_butter.txt"  # Your saved file name
START_TIME_CUT = 30         # Seconds to remove for stabilization
SNAPSHOT_SIZE = 5           # Snapshot duration in seconds

# ---------- PARSER ----------
def parse_labelled_file(filename):
    ecg_values = []
    sampling_rates = []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                # Format: "ECG:23.45,SR:501.20"
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    # Extract number after "ECG:"
                    val_ecg = float(parts[0].split(':')[1])
                    # Extract number after "SR:"
                    val_sr = float(parts[1].split(':')[1])
                    
                    ecg_values.append(val_ecg)
                    sampling_rates.append(val_sr)
            except (IndexError, ValueError):
                continue # Skip lines like "leads off" or headers

    return np.array(ecg_values), np.array(sampling_rates)

# ---------- LOAD DATA ----------
ecg, sr_history = parse_labelled_file(FILE_NAME)

if len(ecg) == 0:
    print("Error: No data found. Check if the file contains 'ECG:' labels.")
else:
    # Use the average measured sampling rate from the file
    avg_sr = np.mean(sr_history)
    print(f"Measured Average Sampling Rate: {avg_sr:.2f} Hz")
    
    # Create time axis
    time = np.arange(len(ecg)) / avg_sr
    start_idx = int(START_TIME_CUT * avg_sr)

    # ---------- PLOT 1: FULL DATA VS STABILIZED ----------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Full data showing the cut
    ax1.plot(time, ecg, color='gray', alpha=0.3)
    ax1.axvspan(0, START_TIME_CUT, color='red', alpha=0.1, label='Stabilization Period')
    ax1.set_title(f"Full Signal Overview (Avg SR: {avg_sr:.1f} Hz)")
    ax1.set_ylabel("Amplitude")
    ax1.legend()
    ax1.grid(True)

    # Stabilized Data
    if len(ecg) > start_idx:
        ax2.plot(time[start_idx:], ecg[start_idx:], color='blue', linewidth=1)
        ax2.set_title(f"Butterworth Filtered Signal (After {START_TIME_CUT}s)")
        ax2.set_xlabel("Time (seconds)")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

    # ---------- PLOT 2: DETAILED 5s SNAPSHOTS ----------
    if len(ecg) > start_idx:
        clean_time = time[start_idx:]
        clean_ecg = ecg[start_idx:]
        
        # Calculate how many 5s segments we have
        total_clean_duration = clean_time[-1] - clean_time[0]
        num_segments = int(total_clean_duration / SNAPSHOT_SIZE)
        
        # We'll plot a maximum of 5 segments to avoid too many windows
        for i in range(min(num_segments, 5)):
            t_start = clean_time[0] + (i * SNAPSHOT_SIZE)
            t_end = t_start + SNAPSHOT_SIZE
            
            mask = (clean_time >= t_start) & (clean_time < t_end)
            
            plt.figure(figsize=(12, 4))
            plt.plot(clean_time[mask], clean_ecg[mask], color='darkgreen')
            plt.title(f"ECG Close-up: {t_start:.1f}s to {t_end:.1f}s")
            plt.xlabel("Time (s)")
            plt.ylabel("Filtered Amplitude")
            plt.grid(which='both', linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.show()