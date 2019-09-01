
from PyQt6 import QtCharts, QtCore



class CustomedQChartView(QtCharts.QChartView):

    Signal_pos = QtCore.pyqtSignal(QtCore.QPointF)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

