import pyqtgraph as pg

def apply_ecg_grid(plot):

    plot.showGrid(x=True,y=True)

    plot.getPlotItem().getAxis('left').setPen('r')
    plot.getPlotItem().getAxis('bottom').setPen('r')

    plot.getViewBox().setBackgroundColor((255,240,240))