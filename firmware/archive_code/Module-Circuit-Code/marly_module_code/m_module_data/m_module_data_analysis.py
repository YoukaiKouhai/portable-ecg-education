import numpy as np
import matplotlib.pyplot as plt

# ---------- FILE NAMES ----------
BUTTER_FILE = "butterworth.txt"
CHEBY_FILE = "chebyshev.txt"
KALMAN_FILE = "kalman.txt"


# ---------- PARSERS ----------

def parse_butterworth(filename):
    hr, hrv, ecg, sr = [], [], [], []
    
    with open(filename, 'r') as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                hr.append(float(parts[0].split(':')[1]))
                hrv.append(float(parts[1].split(':')[1]))
                ecg.append(float(parts[2].split(':')[1]))
                sr.append(float(parts[3].split(':')[1].replace(" Hz", "")))
            except:
                continue

    return np.array(hr), np.array(hrv), np.array(ecg), np.array(sr)


def parse_chebyshev(filename):
    hr, hrv, filtered, sr, raw = [], [], [], [], []
    
    with open(filename, 'r') as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                hr.append(float(parts[0]))
                hrv.append(float(parts[1]))
                filtered.append(float(parts[2]))
                sr.append(float(parts[3]))
                raw.append(float(parts[4]))
            except:
                continue

    return np.array(hr), np.array(hrv), np.array(filtered), np.array(sr), np.array(raw)


def parse_kalman(filename):
    hr, hrv, filtered, sr = [], [], [], []
    
    with open(filename, 'r') as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                hr.append(float(parts[0]))
                hrv.append(float(parts[1]))
                filtered.append(float(parts[2]))
                sr.append(float(parts[3]))
            except:
                continue

    return np.array(hr), np.array(hrv), np.array(filtered), np.array(sr)


# ---------- LOAD DATA ----------

but_hr, but_hrv, but_ecg, but_sr = parse_butterworth(BUTTER_FILE)
cheb_hr, cheb_hrv, cheb_ecg, cheb_sr, cheb_raw = parse_chebyshev(CHEBY_FILE)
kal_hr, kal_hrv, kal_ecg, kal_sr = parse_kalman(KALMAN_FILE)


# ---------- CREATE TIME AXES ----------
# Use sampling rate from first entry if available

def create_time_axis(signal, sampling_rate):
    if len(sampling_rate) > 0:
        sr = sampling_rate[0]
    else:
        sr = 250  # default fallback
    return np.arange(len(signal)) / sr


t_but = create_time_axis(but_ecg, but_sr)
t_cheb = create_time_axis(cheb_ecg, cheb_sr)
t_kal = create_time_axis(kal_ecg, kal_sr)


# ---------- PLOT ECG SIGNALS (STACKED TOP / MIDDLE / BOTTOM) ----------

fig, axs = plt.subplots(3, 1, figsize=(12, 8))  # removed sharex=True

# Top: Butterworth
axs[0].plot(t_but, but_ecg)
axs[0].set_title("Butterworth Filter")
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Amplitude")
axs[0].grid(True)

# Middle: Chebyshev
axs[1].plot(t_cheb, cheb_ecg)
axs[1].set_title("Chebyshev Filter")
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Amplitude")
axs[1].grid(True)

# Bottom: Kalman
axs[2].plot(t_kal, kal_ecg)
axs[2].set_title("Kalman Filter")
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Amplitude")
axs[2].grid(True)

plt.tight_layout()
plt.show()




# ---------- OPTIONAL: Plot HR Comparison ----------

plt.figure(figsize=(10, 5))
plt.plot(but_hr, label="Butterworth HR")
plt.plot(cheb_hr, label="Chebyshev HR")
plt.plot(kal_hr, label="Kalman HR")
plt.title("Heart Rate Comparison")
plt.xlabel("Sample Index")
plt.ylabel("HR (BPM)")
plt.legend()
plt.grid(True)
plt.show()

# ---------- CHEBYSHEV SEGMENTED PLOTS ----------

sections = [
    (0, 20),
    (20, 40),
    (40, 60),
    (60, 80),
    (80, 100),
    (100, t_cheb[-1])
]

for start, end in sections:
    mask = (t_cheb >= start) & (t_cheb < end)
    
    if np.any(mask):  # Only plot if data exists in that range
        plt.figure(figsize=(10, 4))
        plt.plot(t_cheb[mask], cheb_ecg[mask])
        plt.title(f"Chebyshev Filter: {start}–{end} sec")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
