import numpy as np
import matplotlib.pyplot as plt

# ---------- SETTINGS ----------
FILE_NAME = "22.98,125.94,332.txt"
START_TIME_CUT = 0  # Seconds to remove for Kalman stabilization
INTERVAL_SIZE = 5    # Detail view window (seconds)

# ---------- PARSER ----------
def parse_dual_ecg(filename):
    hr, ecg1, ecg2, sr = [], [], [], []
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                # Format: HR, Filtered1, Filtered2, SamplingRate
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    hr.append(float(parts[0]))
                    ecg1.append(float(parts[1]))
                    ecg2.append(float(parts[2]))
                    sr.append(float(parts[3]))
            except:
                continue

    return np.array(hr), np.array(ecg1), np.array(ecg2), np.array(sr)

# ---------- LOAD AND PROCESS ----------
hr, ecg1, ecg2, sr_list = parse_dual_ecg(FILE_NAME)

if len(ecg1) == 0:
    print("Error: No data loaded. Check the file path and format.")
else:
    # Calculate Time Axis using the average sampling rate
    avg_sr = np.mean(sr_list)
    time = np.arange(len(ecg1)) / avg_sr
    start_idx = int(START_TIME_CUT * avg_sr)

    # ---------- PLOT 1: DUAL OVERVIEW (STABILIZED) ----------
    if len(ecg1) > start_idx:
        fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

        # Module 1 Plot
        ax_top.plot(time[start_idx:], ecg1[start_idx:], color='blue', label='Lead 1 (A0)')
        ax_top.set_title(f"Dual-Lead ECG Overview (Avg SR: {avg_sr:.1f} Hz)")
        ax_top.set_ylabel("Amplitude")
        ax_top.legend(loc='upper right')
        ax_top.grid(True, alpha=0.3)

        # Module 2 Plot
        ax_bot.plot(time[start_idx:], ecg2[start_idx:], color='darkred', label='Lead 2 (A1)')
        ax_bot.set_xlabel("Time (seconds)")
        ax_bot.set_ylabel("Amplitude")
        ax_bot.legend(loc='upper right')
        ax_bot.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        # ---------- PLOT 2: SYNCHRONIZED 5s SNAPSHOT ----------
        # This is vital to show that both modules are capturing the SAME heartbeat
        t_start = time[start_idx] + 10  # Pick a spot 10s after stabilization
        t_end = t_start + INTERVAL_SIZE
        mask = (time >= t_start) & (time < t_end)

        if np.any(mask):
            plt.figure(figsize=(14, 6))
            plt.plot(time[mask], ecg1[mask], label='Module 1', color='blue', alpha=0.8)
            plt.plot(time[mask], ecg2[mask], label='Module 2', color='red', alpha=0.8)
            plt.title(f"Synchronized Detail View: {t_start:.1f}s to {t_end:.1f}s")
            plt.xlabel("Time (s)")
            plt.ylabel("Filtered Amplitude")
            plt.legend()
            plt.grid(which='both', linestyle='--', alpha=0.5)
            plt.show()

    else:
        print("Data is too short to cut 30 seconds.")

# Assuming you have already loaded 'ecg1' (Lead I) and 'ecg2' (Lead II)
# From your parse_dual_ecg function

# 1. Calculate Derived Leads
lead1 = ecg1
lead2 = ecg2
lead3 = lead2 - lead1

avr = -(lead1 + lead2) / 2
avl = lead1 - (lead2 / 2)
avf = lead2 - (lead1 / 2)

# 2. Plotting the 6-Lead Layout
fig, axs = plt.subplots(3, 2, figsize=(15, 10), sharex=True)

# Column 1: Standard Leads
axs[0, 0].plot(time[mask], lead1[mask], color='blue')
axs[0, 0].set_title("Lead I")

axs[1, 0].plot(time[mask], lead2[mask], color='red')
axs[1, 0].set_title("Lead II")

axs[2, 0].plot(time[mask], lead3[mask], color='green')
axs[2, 0].set_title("Lead III")

# Column 2: Augmented Leads
axs[0, 1].plot(time[mask], avr[mask], color='purple')
axs[0, 1].set_title("aVR")

axs[1, 1].plot(time[mask], avl[mask], color='orange')
axs[1, 1].set_title("aVL")

axs[2, 1].plot(time[mask], avf[mask], color='brown')
axs[2, 1].set_title("aVF")

for ax in axs.flat:
    ax.grid(True, alpha=0.3)
    ax.set_ylabel("Amp")

plt.xlabel("Time (s)")
plt.tight_layout()
plt.show()

# ---------- CALCULATE ALL 6 LEADS ----------
# Base leads from your 2 modules
L1 = ecg1
L2 = ecg2

# Derived Limb Leads
L3 = L2 - L1
aVR = -(L1 + L2) / 2
aVL = L1 - (L2 / 2)
aVF = L2 - (L1 / 2)

# ---------- PLOT OVERLAP ----------
plt.figure(figsize=(15, 7))

# Define time window for the snapshot (5 seconds)
# Using 'mask' from the previous step
t_segment = time[mask]

plt.plot(t_segment, L1[mask],   label='Lead I',   color='blue',       alpha=0.7)
plt.plot(t_segment, L2[mask],   label='Lead II',  color='red',        alpha=0.7)
plt.plot(t_segment, L3[mask],   label='Lead III', color='green',      alpha=0.7)
plt.plot(t_segment, aVR[mask],  label='aVR',      color='purple',     alpha=0.8, linestyle='--') # Inverted lead
plt.plot(t_segment, aVL[mask],  label='aVL',      color='orange',     alpha=0.7)
plt.plot(t_segment, aVF[mask],  label='aVF',      color='darkgoldenrod', alpha=0.7)

plt.title("6-Lead Synchronized Overlap (Full Heart Vector)", fontsize=14)
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Filtered Amplitude (Mapped Units)", fontsize=12)

# Place legend outside to keep the graph clean
plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
plt.grid(True, which='both', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.show()