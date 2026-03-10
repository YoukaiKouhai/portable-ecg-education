import numpy as np

class ECGRecorder:

    def __init__(self):
        self.data = []

    def add(self, value):
        self.data.append(value)

    def save(self, filename):

        np.savetxt(filename, self.data, delimiter=",")

    def load(self, filename):

        self.data = np.loadtxt(filename, delimiter=",")

    def playback(self):

        for v in self.data:
            yield v