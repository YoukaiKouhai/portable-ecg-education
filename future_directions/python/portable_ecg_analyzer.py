# pip install numpy scipy pyqt5 pyqtgraph pyserial reportlab matplotlib sounddevice pyqtgraph pyopengl

import os
import time
import serial
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, cheby1, find_peaks
from scipy.fft import fft
from tkinter import Tk, filedialog
from matplotlib.animation import FuncAnimation

# ===============================
# USER SETTINGS
# ===============================

use_live_acquisition = False
simulate_live_view = True

port = "COM6"
baud = 115200
record_time = 20

Vref = 5
ADCmax = 1023


# ===============================
# CREATE RUN FOLDER
# ===============================

def create_run_folder():

    base = os.getcwd()

    runs = []

    for f in os.listdir(base):
        if f.startswith("RUN_"):
            try:
                runs.append(int(f[4:]))
            except:
                pass

    next_run = 1 if len(runs) == 0 else max(runs) + 1

    folder = os.path.join(base, f"RUN_{next_run:03d}")

    os.makedirs(folder)

    print("Saving data to:", folder)

    return folder


# ===============================
# SERIAL DATA ACQUISITION
# ===============================

def acquire_serial():

    ser = serial.Serial(port, baud)

    start = time.time()

    data = []

    print("Recording...")

    while time.time() - start < record_time:

        line = ser.readline().decode().strip()

        try:

            v1, v2 = map(float, line.split(","))

            data.append([v1, v2])

        except:
            pass

    ser.close()

    print("Recording complete")

    return np.array(data)


# ===============================
# CSV LOADER
# ===============================

def load_csv():

    root = Tk()
    root.withdraw()

    file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if file == "":
        raise Exception("No file selected")

    print("Loading:", file)

    df = pd.read_csv(file)

    leadI = df["leadI"].values
    leadII = df["leadII"].values
    t = df["t"].values

    return leadI, leadII, t


# ===============================
# ADC -> mV
# ===============================

def adc_to_mv(x):

    v = (x / ADCmax) * Vref
    v = v - np.mean(v)
    return v * 1000


# ===============================
# DERIVED LEADS
# ===============================

def derived_leads(I, II):

    leadIII = II - I
    aVR = -(I + II) / 2
    aVL = I - II / 2
    aVF = II - I / 2

    return leadIII, aVR, aVL, aVF


# ===============================
# FILTERS
# ===============================

def simple_kalman(x):

    Q = 0.001
    R = 0.05

    P = 1
    X = x[0]

    out = np.zeros_like(x)

    for i in range(len(x)):

        P = P + Q
        K = P / (P + R)

        X = X + K * (x[i] - X)

        P = (1 - K) * P

        out[i] = X

    return out


def lms_filter(x, ref):

    mu = 0.01
    w = 0

    y = np.zeros_like(x)

    for n in range(len(x)):

        y[n] = x[n] - w * ref[n]

        w = w + mu * y[n] * ref[n]

    return y


def butter_bandpass(x, Fs):

    b, a = butter(4, [0.5/(Fs/2), 40/(Fs/2)], btype='band')

    return filtfilt(b, a, x)


def cheby_notch(x, Fs):

    b, a = cheby1(4, 1, [59/(Fs/2), 61/(Fs/2)], btype='bandstop')

    return filtfilt(b, a, x)


# ===============================
# HEART RATE
# ===============================

def estimate_hr(ecg, Fs):

    signal = ecg - np.mean(ecg)

    peaks, _ = find_peaks(
        signal,
        height=0.5*np.max(signal),
        distance=int(0.4*Fs)
    )

    RR = np.diff(peaks) / Fs

    HR = 60 / np.mean(RR)

    return HR, peaks


# ===============================
# REAL TIME ECG GUI
# ===============================

def live_view(t, leads, Fs):

    names = ["Lead I","Lead II","Lead III","aVR","aVL","aVF"]

    fig, axs = plt.subplots(6,1,figsize=(10,8))

    lines = []

    for i in range(6):

        line, = axs[i].plot([],[],'k')

        axs[i].set_ylabel(names[i])
        axs[i].grid(True)

        lines.append(line)

    axs[-1].set_xlabel("Time (s)")

    window = 2

    def update(frame):

        for i in range(6):

            lines[i].set_data(t[:frame], leads[i][:frame])

            axs[i].set_xlim(max(0,t[frame]-window), t[frame])

        return lines

    ani = FuncAnimation(
        fig,
        update,
        frames=len(t),
        interval=1000/Fs,
        blit=False
    )

    plt.show()


# ===============================
# FILTER PERFORMANCE
# ===============================

def evaluate_filter(folder, Fs):

    files = [
        "bandpass_filtered.csv",
        "butterworth_filtered.csv",
        "chebyshev_notch_filtered.csv",
        "kalman_filtered.csv",
        "adaptive_filtered.csv"
    ]

    labels = [
        "Bandpass",
        "Butterworth",
        "Chebyshev",
        "Kalman",
        "Adaptive"
    ]

    SNR = []
    baseline = []
    powerline = []

    for f in files:

        path = os.path.join(folder,f)

        if not os.path.exists(path):
            continue

        df = pd.read_csv(path)

        ecg = df["leadII"].values

        signal_power = np.var(ecg)

        noise = ecg - pd.Series(ecg).rolling(int(Fs*0.2)).mean()

        noise_power = np.var(noise)

        SNR.append(10*np.log10(signal_power/noise_power))

        b,a = butter(2,0.5/(Fs/2),'low')

        baseline_component = filtfilt(b,a,ecg)

        baseline.append(np.var(baseline_component))

        fdata = np.abs(fft(ecg))

        freqs = np.arange(len(fdata))*Fs/len(fdata)

        idx = np.where((freqs>58)&(freqs<62))

        powerline.append(np.mean(fdata[idx]))

    results = pd.DataFrame({
        "Filter":labels,
        "SNR_dB":SNR,
        "Baseline":baseline,
        "Powerline":powerline
    })

    results.to_csv(os.path.join(folder,"filter_performance.csv"))

    print(results)


# ===============================
# MAIN
# ===============================

run_folder = create_run_folder()

if use_live_acquisition:

    data = acquire_serial()

    leadI_raw = data[:,0]
    leadII_raw = data[:,1]

    t = np.linspace(0,record_time,len(data))

else:

    leadI_raw, leadII_raw, t = load_csv()

Fs = len(leadI_raw)/t[-1]

print("Sampling Rate:",Fs)

leadI = adc_to_mv(leadI_raw)
leadII = adc_to_mv(leadII_raw)

leadIII,aVR,aVL,aVF = derived_leads(leadI,leadII)

HR, peaks = estimate_hr(leadII, Fs)

print("Estimated HR:",HR,"BPM")

signals = [leadI,leadII,leadIII,aVR,aVL,aVF]

if simulate_live_view:
    live_view(t,signals,Fs)

df = pd.DataFrame({
    "t":t,
    "leadI":leadI,
    "leadII":leadII,
    "leadIII":leadIII,
    "aVR":aVR,
    "aVL":aVL,
    "aVF":aVF
})

df.to_csv(os.path.join(run_folder,"filtered_ecg.csv"),index=False)

evaluate_filter(run_folder,Fs)