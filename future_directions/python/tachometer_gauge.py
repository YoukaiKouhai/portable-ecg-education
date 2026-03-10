import pyqtgraph as pg
from PyQt5 import QtWidgets

class Tachometer(pg.PlotWidget):

    def __init__(self):

        super().__init__()

        self.setYRange(0,180)
        self.setXRange(0,1)

        self.bar = pg.BarGraphItem(x=[0.5], height=[0], width=0.3)

        self.addItem(self.bar)

    def update_hr(self, hr):

        self.bar.setOpts(height=[hr])