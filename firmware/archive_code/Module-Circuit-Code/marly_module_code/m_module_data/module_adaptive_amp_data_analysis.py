import numpy as np
import matplotlib.pyplot as plt

# ---------- SETTINGS ----------
FILE_NAME = "kalman_2.18.26_v1.txt"
START_TIME_CUT = 0  # Adjust as needed (30s is standard for stabilization)
INTERVAL_SIZE = 1    # Set to 5 seconds per snapshot for high detail

# ---------- PARSER ----------
def parse_ecg_data(filename):
    hr, hrv, filtered, sr = [], [], [], []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    hr.append(float(parts[0]))
                    hrv.append(float(parts[1]))
                    filtered.append(float(parts[2]))
                    sr_val = str(parts[3]).replace(" Hz", "")
                    sr.append(float(sr_val))
            except Exception:
                continue

    return np.array(hr), np.array(hrv), np.array(filtered), np.array(sr)

# ---------- LOAD AND PROCESS ----------
hr, hrv, ecg, sr_list = parse_ecg_data(FILE_NAME)

if len(ecg) == 0:
    print("Error: No data loaded. Check file format.")
else:
    sampling_rate = sr_list[0] if len(sr_list) > 0 else 500
    time = np.arange(len(ecg)) / sampling_rate
    start_idx = int(START_TIME_CUT * sampling_rate)

    print(f"File Duration: {time[-1]:.2f} seconds")

    # ---------- PLOT 1: FULL OVERVIEW ----------
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(time, ecg, color='gray', alpha=0.4, label='Initial Data')
    ax1.axvspan(0, START_TIME_CUT, color='red', alpha=0.1, label='Stabilization Period')
    ax1.set_title(f"ECG Processing Overview: {FILE_NAME}")
    ax1.set_ylabel("Amplitude")
    ax1.legend()
    ax1.grid(True)

    if len(ecg) > start_idx:
        ax2.plot(time[start_idx:], ecg[start_idx:], color='blue', label='Kalman Stabilized')
        ax2.set_title(f"Stabilized Signal (Data after {START_TIME_CUT}s)")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Amplitude")
        ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

    # ---------- PLOT 2: HEART RATE HISTORY ----------
    plt.figure(figsize=(10, 4))
    plt.plot(time[start_idx:], hr[start_idx:], color='red', linewidth=1.5)
    plt.title("Calculated Heart Rate (BPM) - Post-Stabilization")
    plt.xlabel("Time (s)")
    plt.ylabel("BPM")
    plt.ylim([40, 180]) 
    plt.grid(True)
    plt.show()

    # ---------- SEGMENTED PLOTS (5s Snapshots) ----------
    if len(ecg) > start_idx:
        clean_time = time[start_idx:]
        clean_ecg = ecg[start_idx:]
        
        duration = clean_time[-1] - clean_time[0]
        num_segments = int(duration / INTERVAL_SIZE)
        
        print(f"Generating {num_segments} snapshots of {INTERVAL_SIZE} seconds each...")

        # Loop through data in 5-second jumps
        for i in range(num_segments): 
            seg_start = clean_time[0] + (i * INTERVAL_SIZE)
            seg_end = seg_start + INTERVAL_SIZE
            
            mask = (clean_time >= seg_start) & (clean_time < seg_end)
            
            if np.any(mask):
                plt.figure(figsize=(12, 4))
                plt.plot(clean_time[mask], clean_ecg[mask], color='darkgreen', linewidth=1)
                plt.title(f"ECG Detail View: {seg_start:.1f}s to {seg_end:.1f}s")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
                plt.grid(which='both', linestyle='--', linewidth=0.5)
                plt.tight_layout()
                plt.show()