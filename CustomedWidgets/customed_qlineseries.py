

from PyQt6 import QtCharts, QtCore


class CustomedQLineSeries(QtCharts.QLineSeries):
    Signal_click = QtCore.pyqtSignal(str, str, list, QtCore.QPointF, QtCore.QPointF, float, int)
    Signal_name_hovered = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self.emitclick)
        self.hovered.connect(self.highlighted)
        self.hovered.connect(self.emitnameHovered)

    def emitclick(self):
        self.Signal_click.emit(self.name(), self.objectName(), self.getAllpoints(), self.getMaxY(),
                                      self.getMinY(), self.getAvgVal(), self.Count())

    def emitnameHovered(self):
        self.Signal_name_hovered.emit(self.name())

    def getAllpoints(self):
        return list(self.points())

    def highlighted(self, point, state):
        if state:
            pen = self.pen()
            pen.setWidth(5)
            color = self.color()
            pen.setBrush(color)
            self.setPen(pen)
        else:
            pen = self.pen()
            pen.setWidth(2)
            color = self.color()
            pen.setBrush(color)
            self.setPen(pen)

    def getMaxY(self):
        curval = 0
        curpt = None
        for i in self.getAllpoints():
            if curpt is None:
                curpt = i
                curval = i.y()
            else:
                if i.y() > curval:
                    curpt = i
                    curval = i.y()
        return curpt

    def getMinY(self):
        curval = 0
        curpt = None
        for i in self.getAllpoints():
            if curpt is None:
                curpt = i
                curval = i.y()
            else:
                if i.y() < curval:
                    curpt = i
                    curval = i.y()
        return curpt

    def getAvgVal(self):
        sum = 0
        for i in self.getAllpoints():
            sum += i.y()
        if self.count():
            sum /= self.count()
        return sum

    def getMinX(self):
        curval = 0
        curpt = None
        for i in self.getAllpoints():
            if curpt is None:
                curpt = i
                curval = i.x()
            else:
                if i.x() < curval:
                    curpt = i
                    curval = i.x()
        return curpt

    def getMaxX(self):
        curval = 0
        curpt = None
        for i in self.getAllpoints():
            if curpt is None:
                curpt = i
                curval = i.x()
            else:
                if i.x() > curval:
                    curpt = i
                    curval = i.x()
        return curpt

    def Count(self):
        return self.count()
