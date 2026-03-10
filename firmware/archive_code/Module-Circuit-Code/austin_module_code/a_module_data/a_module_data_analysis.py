import numpy as np
import matplotlib.pyplot as plt

# ---------- FILE NAMES ----------
BUTTER_FILE = "butterworth.txt"
CHEBY_FILE = "chebyshev.txt"
CLEAN_FILE = "clean.txt"


# ---------- GENERIC PARSER ----------
def parse_file(filename):
    hr, hrv, value = [], [], []

    with open(filename, 'r') as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                hr.append(float(parts[0]))
                hrv.append(float(parts[1]))
                value.append(float(parts[2]))
            except:
                continue  # skip malformed lines

    return np.array(hr), np.array(hrv), np.array(value)


# ---------- LOAD DATA ----------
but_hr, but_hrv, but_ecg = parse_file(BUTTER_FILE)
cheb_hr, cheb_hrv, cheb_ecg = parse_file(CHEBY_FILE)
kal_hr, kal_hrv, kal_ecg = parse_file(CLEAN_FILE)


# ---------- CREATE SAMPLE INDEX AXIS ----------
t_but = np.arange(len(but_ecg))
t_cheb = np.arange(len(cheb_ecg))
t_kal = np.arange(len(kal_ecg))


# ---------- STACKED ECG PLOTS ----------
fig, axs = plt.subplots(3, 1, figsize=(12, 8))

axs[0].plot(t_but, but_ecg)
axs[0].set_title("Butterworth")
axs[0].set_ylabel("Amplitude")
axs[0].grid(True)

axs[1].plot(t_cheb, cheb_ecg)
axs[1].set_title("Chebyshev")
axs[1].set_ylabel("Amplitude")
axs[1].grid(True)

axs[2].plot(t_kal, kal_ecg)
axs[2].set_title("clean")
axs[2].set_xlabel("Sample Index")
axs[2].set_ylabel("Amplitude")
axs[2].grid(True)

plt.tight_layout()
plt.show()


# ---------- HR COMPARISON ----------
plt.figure(figsize=(10, 5))

plt.plot(but_hr, label="Butterworth")
plt.plot(cheb_hr, label="Chebyshev")
plt.plot(kal_hr, label="clean")

plt.title("Heart Rate Comparison")
plt.xlabel("Sample Index")
plt.ylabel("HR (BPM)")
plt.legend()
plt.grid(True)
plt.show()
