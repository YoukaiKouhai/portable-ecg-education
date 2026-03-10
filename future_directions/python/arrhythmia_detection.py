import numpy as np
from scipy.signal import find_peaks

class ArrhythmiaDetector:

    def __init__(self, Fs):
        self.Fs = Fs

    def detect(self, ecg):

        ecg = ecg - np.mean(ecg)

        peaks,_ = find_peaks(
            ecg,
            height=0.5*np.max(ecg),
            distance=int(0.4*self.Fs)
        )

        if len(peaks) < 3:
            return "Unknown", peaks

        rr = np.diff(peaks) / self.Fs

        hr = 60 / np.mean(rr)

        irregular = np.std(rr)

        if irregular > 0.15:
            rhythm = "Possible PVC / Arrhythmia"

        elif hr > 110:
            rhythm = "Tachycardia"

        elif hr < 50:
            rhythm = "Bradycardia"

        else:
            rhythm = "Normal"

        return rhythm, peaks