import sys
import serial
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg


# ===============================
# SERIAL STREAM
# ===============================

class SerialStream(QtCore.QThread):

    new_data = QtCore.pyqtSignal(float, float)

    def __init__(self, port="COM6", baud=115200):
        super().__init__()
        self.ser = serial.Serial(port, baud)
        self.running = True

    def run(self):

        while self.running:

            try:
                line = self.ser.readline().decode().strip()

                v1, v2 = map(float, line.split(","))

                self.new_data.emit(v1, v2)

            except:
                pass

    def stop(self):

        self.running = False
        self.ser.close()


# ===============================
# SIGNAL PROCESSOR
# ===============================

class SignalProcessor:

    def __init__(self, Fs=500):

        self.Fs = Fs

    def adc_to_mv(self, x):

        Vref = 5
        ADCmax = 1023

        v = (x/ADCmax)*Vref
        v -= np.mean(v)

        return v*1000

    def bandpass(self, x):

        b,a = butter(4,[0.5/(self.Fs/2),40/(self.Fs/2)],btype='band')

        return filtfilt(b,a,x)

    def hr_detect(self, ecg):

        ecg = ecg - np.mean(ecg)

        peaks,_ = find_peaks(
            ecg,
            height=0.5*np.max(ecg),
            distance=int(0.4*self.Fs)
        )

        if len(peaks) < 2:
            return 0

        rr = np.diff(peaks)/self.Fs

        return 60/np.mean(rr)


# ===============================
# ARRHYTHMIA DETECTOR
# ===============================

class ArrhythmiaDetector:

    def detect(self, hr):

        if hr == 0:
            return "No Signal"

        if hr < 50:
            return "Bradycardia"

        if hr > 110:
            return "Tachycardia"

        return "Normal"


# ===============================
# ECG GUI
# ===============================

class ECGMonitor(QtWidgets.QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Portable ECG Monitor")

        self.processor = SignalProcessor()
        self.detector = ArrhythmiaDetector()

        self.buffer = np.zeros(2000)

        self.index = 0

        # Plot widget
        self.plot = pg.PlotWidget()

        self.setCentralWidget(self.plot)

        self.plot.setYRange(-2,2)

        self.plot.showGrid(x=True,y=True)

        self.curve = self.plot.plot(pen='g')

        # ECG grid paper style
        self.plot.getPlotItem().getAxis('left').setPen('r')
        self.plot.getPlotItem().getAxis('bottom').setPen('r')

        # Heart rate label
        self.hr_label = QtWidgets.QLabel("HR: -- BPM")

        self.hr_label.setStyleSheet("font-size:24px;color:red")

        # Arrhythmia label
        self.arr_label = QtWidgets.QLabel("Status: --")

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.plot)
        layout.addWidget(self.hr_label)
        layout.addWidget(self.arr_label)

        # Filter toggle
        self.filter_btn = QtWidgets.QPushButton("Toggle Filter")

        self.filter_btn.setCheckable(True)

        layout.addWidget(self.filter_btn)

        container = QtWidgets.QWidget()

        container.setLayout(layout)

        self.setCentralWidget(container)

        # Serial
        self.serial = SerialStream()

        self.serial.new_data.connect(self.update_ecg)

        self.serial.start()

        # Timer for HR
        self.timer = QtCore.QTimer()

        self.timer.timeout.connect(self.update_hr)

        self.timer.start(1000)

    def update_ecg(self, v1, v2):

        mv = self.processor.adc_to_mv(np.array([v2]))[0]

        if self.filter_btn.isChecked():
            mv = self.processor.bandpass(np.array([mv]))[0]

        self.buffer = np.roll(self.buffer,-1)

        self.buffer[-1] = mv

        self.curve.setData(self.buffer)

    def update_hr(self):

        hr = self.processor.hr_detect(self.buffer)

        self.hr_label.setText(f"HR: {hr:.0f} BPM")

        status = self.detector.detect(hr)

        self.arr_label.setText(f"Status: {status}")


# ===============================
# MAIN
# ===============================

def main():

    app = QtWidgets.QApplication(sys.argv)

    win = ECGMonitor()

    win.resize(1000,600)

    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()