# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow1.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from F1_Analyz import f1db
import bitarray
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC

class Ui_MainWindow(object):

    def __init__(self):
        self.db = f1db()
        self.years_recorded_in_lap_times = self.db.getAllYearsRecordedInLaptimes()
        self.race_names_recorded_in_lap_times = self.db.getAllRaceNameRecordedInLaptimes()

    def initialize(self):
        for i in self.years_recorded_in_lap_times:
            self.comboBox.addItem(str(i['year']))
        year = self.comboBox.currentText()
        races = self.db.getRacesInAYearRecordedInLaptimes(year)
        for i in races:
            self.comboBox_2.addItem(i['name'])

    def getRacesInThisYear(self):
        self.comboBox_2.clear()
        year = self.comboBox.currentText()
        races = self.db.getRacesInAYearRecordedInLaptimes(year)
        for i in races:
            self.comboBox_2.addItem(i['name'])

    def getDriversInThisRace(self):
        year = self.comboBox.currentText()
        race_name = self.comboBox_2.currentText()
        raceId = self.db.getRaceIDByYearName(year, race_name)
        drivers_id = self.db.getGridByRaceID(raceId[0]['raceId'])
        self.initTable(drivers_id, raceId[0]['raceId'])

    def showPos(self):
        length = self.tableWidget.rowCount()
        curstate = bitarray.bitarray(length)
        curstate.setall(False)
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(i, 4).checkState():
                curstate[i] = 1
        if bitarray.bitdiff(curstate, self.laststate):
            self.laststate = curstate
            # print(self.laststate)
            t = time.time()
            self.plotGraph()
            print('Plot graph:',time.time()-t,'seconds.')

    def mssmmm2ms(self,time):
        minute = 0
        if ':' in time:
            sep = time.split(':')
            minute = int(sep[0])
            time = sep[1]
        if '.' in time:
            sep = time.split('.')
            second = int(sep[0])
            millisecond = int(sep[1])
        else:
            second = int(time)
            millisecond = 0
        return millisecond+1000*second+60000*minute

    def plotGraph(self):
        # TODO: Can still be optimized
        try:
            self.fig.clear()
            ax = self.fig.add_subplot(111)
            ax.cla()
            legends = []
            length = len(self.drivers)
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing = self.db.getLaptimesViaDriverIDRaceID(driver['driverId'], self.raceId)
                    plot_pool_x = []
                    plot_pool_y = []
                    for k in timing:
                        time = self.mssmmm2ms(k['time'])
                        plot_pool_x.append(k['lap'])
                        plot_pool_y.append(time)
                    name = self.db.getDriversByDriverID(driver['driverId'])[0]['surname']
                    ax.plot(plot_pool_x, plot_pool_y, marker=',')
                    legends.append(name)
            self.fig.legend(legends,loc=5)
            self.canvas.draw()  #
        except Exception as e:
            print(e)


    def initTable(self, drivers, raceId):
        self.tableWidget.setColumnCount(5)
        self.laststate = bitarray.bitarray(len(drivers))
        self.lastplotedstate = bitarray.bitarray(len(drivers))
        self.drivers = drivers
        self.raceId = raceId
        self.laststate.setall(False)
        self.lastplotedstate.setall(False)
        self.tableWidget.horizontalHeader().setStretchLastSection(False)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        # self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tableWidget.setHorizontalHeaderLabels(['Code', 'Name', 'Grid', 'Result', 'Checked'])
        self.tableWidget.setRowCount(len(drivers))
        rowcount = 0
        for num in range(len(drivers)):
            i = drivers[num]
            font = QtGui.QFont()
            color = QtGui.QColor(255, 255, 255)
            finish_pos_raw = self.db.getResultStandingByRaceIDandDriverId(raceId, i['driverId'])
            finish_pos = finish_pos_raw[0]['position']
            start_pos_raw = self.db.getStartposByRaceIDDriverID(raceId,i['driverId'])
            try:
                start_pos = start_pos_raw[0]['position']
            except IndexError:
                start_pos = ''
            finish_status_Id = self.db.getResultStatusIDByRaceIDandDriverID(raceId, i['driverId'])[0]['statusId']
            finish_status = self.db.getFinishStatusNameByStatusID(finish_status_Id)[0]['status']
            driver_detail = self.db.getDriversByDriverID(i['driverId'])
            if finish_pos is not None:
                if finish_pos == 1:
                    color = QtGui.QColor(255, 215, 0, 128)
                elif finish_pos == 2:
                    color = QtGui.QColor(192, 192, 192, 128)
                elif finish_pos == 3:
                    color = QtGui.QColor(198, 145, 69, 128)
                elif 4 <= finish_pos <= 10:
                    color = QtGui.QColor(0, 255, 229, 128)
            else:
                color = QtGui.QColor(64, 64, 64, 128)

            if start_pos == 1:
                font.setBold(True)
            item0 = QtWidgets.QTableWidgetItem(str(driver_detail[0]['code']))
            item0.setFont(font)
            item0.setBackground(color)
            if finish_pos is None:
                item0.setForeground(QtGui.QColor(255, 255, 255))
            item0.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(rowcount, 0, item0)
            item1 = QtWidgets.QTableWidgetItem(driver_detail[0]['forename'] + ' ' + driver_detail[0]['surname'])
            item1.setFont(font)
            item1.setBackground(color)
            if finish_pos is None:
                item1.setForeground(QtGui.QColor(255, 255, 255))
            item1.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(rowcount, 1, item1)
            startpos = QtWidgets.QTableWidgetItem(str(start_pos))
            startpos.setBackground(color)
            startpos.setFont(font)
            if finish_pos is None:
                startpos.setForeground(QtGui.QColor(255, 255, 255))
            startpos.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(rowcount, 2, startpos)
            if finish_pos is not None:
                finishpos = QtWidgets.QTableWidgetItem(str(finish_pos))
            else:
                if finish_status_Id == 2:
                    finishpos = QtWidgets.QTableWidgetItem("DSQ")
                elif 3 <= finish_status_Id <= 10 or 20 <= finish_status_Id <= 44 or 46 <= finish_status_Id <= 49 or finish_status_Id == 51 \
                        or finish_status_Id == 54 or finish_status_Id == 56 or 59 <= finish_status_Id <= 61 or 63 <= finish_status_Id <= 76 \
                        or 78 <= finish_status_Id <= 80 or 82 <= finish_status_Id <= 87 or finish_status_Id == 89 or 91 <= finish_status_Id <= 95\
                        or 98 <= finish_status_Id <= 110 or finish_status_Id == 121 or finish_status_Id == 126 or 129 <= finish_status_Id <= 132\
                        or 135 <= finish_status_Id <= 137:
                    finishpos = QtWidgets.QTableWidgetItem("RET")
                elif finish_status_Id == 62:
                    finishpos = QtWidgets.QTableWidgetItem("NC")
                elif finish_status_Id == 77:
                    finishpos = QtWidgets.QTableWidgetItem("107")
                elif finish_status_Id == 81:
                    finishpos = QtWidgets.QTableWidgetItem("DNQ")
                elif finish_status_Id == 90:
                    finishpos = QtWidgets.QTableWidgetItem("NR")
                elif finish_status_Id == 96:
                    finishpos = QtWidgets.QTableWidgetItem("EX")
                elif finish_status_Id == 97:
                    finishpos = QtWidgets.QTableWidgetItem("DNPQ")
            finishpos.setFont(font)
            finishpos.setBackground(color)
            if finish_pos is None:
                finishpos.setForeground(QtGui.QColor(255, 255, 255))
            finishpos.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(rowcount, 3, finishpos)
            check = QtWidgets.QTableWidgetItem()
            check.setCheckState(QtCore.Qt.Unchecked)
            if start_pos == 'DNS':
                check.setFlags(
                    QtCore.Qt.ItemIsSelectable)
            self.tableWidget.setItem(rowcount, 4, check)
            rowcount += 1

    # def setupUi(self, MainWindow):
    #     MainWindow.setObjectName("MainWindow")
    #     MainWindow.resize(1102, 691)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
    #     MainWindow.setSizePolicy(sizePolicy)
    #     MainWindow.setMinimumSize(QtCore.QSize(800, 600))
    #     MainWindow.setMaximumSize(QtCore.QSize(8000, 6000))
    #     self.centralwidget = QtWidgets.QWidget(MainWindow)
    #     self.centralwidget.setObjectName("centralwidget")
    #     self.widget = QtWidgets.QWidget(self.centralwidget)
    #     self.widget.setGeometry(QtCore.QRect(20, 20, 1061, 631))
    #     self.widget.setObjectName("widget")
    #     self.gridLayout = QtWidgets.QGridLayout(self.widget)
    #     self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
    #     self.gridLayout.setContentsMargins(0, 0, 0, 0)
    #     self.gridLayout.setObjectName("gridLayout")
    #     self.horizontalLayout = QtWidgets.QHBoxLayout()
    #     self.horizontalLayout.setObjectName("horizontalLayout")
    #     self.comboBox = QtWidgets.QComboBox(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
    #     self.comboBox.setSizePolicy(sizePolicy)
    #     self.comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
    #     self.comboBox.setCurrentText("")
    #     self.comboBox.setObjectName("comboBox")
    #     self.horizontalLayout.addWidget(self.comboBox)
    #     self.comboBox_2 = QtWidgets.QComboBox(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
    #     self.comboBox_2.setSizePolicy(sizePolicy)
    #     self.comboBox_2.setMaximumSize(QtCore.QSize(16777215, 30))
    #     self.comboBox_2.setObjectName("comboBox_2")
    #     self.horizontalLayout.addWidget(self.comboBox_2)
    #     self.pushButton = QtWidgets.QPushButton(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
    #     self.pushButton.setSizePolicy(sizePolicy)
    #     self.pushButton.setMaximumSize(QtCore.QSize(16777215, 30))
    #     self.pushButton.setObjectName("pushButton")
    #     self.horizontalLayout.addWidget(self.pushButton)
    #     self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
    #     self.graphicsView = QtWidgets.QGraphicsView(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
    #     self.graphicsView.setSizePolicy(sizePolicy)
    #     self.graphicsView.setObjectName("graphicsView")
    #     self.gridLayout.addWidget(self.graphicsView, 0, 1, 2, 1)
    #     self.tableWidget = QtWidgets.QTableWidget(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
    #     self.tableWidget.setSizePolicy(sizePolicy)
    #     self.tableWidget.setObjectName("tableWidget")
    #     self.tableWidget.setColumnCount(0)
    #     self.tableWidget.setRowCount(0)
    #     self.gridLayout.addWidget(self.tableWidget, 1, 0, 2, 1)
    #     self.canvas = QtWidgets.QGraphicsView(self.widget)
    #     sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
    #     self.canvas.setSizePolicy(sizePolicy)
    #     self.canvas.setObjectName("canvas")
    #     self.gridLayout.addWidget(self.canvas, 2, 1, 1, 1)
    #     MainWindow.setCentralWidget(self.centralwidget)
    #     self.statusbar = QtWidgets.QStatusBar(MainWindow)
    #     self.statusbar.setObjectName("statusbar")
    #     MainWindow.setStatusBar(self.statusbar)
    #     self.retranslateUi(MainWindow)
    #     QtCore.QMetaObject.connectSlotsByName(MainWindow)
    #     self.initialize()
    #     self.comboBox.currentIndexChanged.connect(self.getRacesInThisYear)
    #     self.pushButton.clicked.connect(self.getDriversInThisRace)
    #     self.tableWidget.clicked.connect(self.showPos)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1366, 768)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1366, 768))
        MainWindow.setMaximumSize(QtCore.QSize(1366, 768))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 1061, 631))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.comboBox.setCurrentText("")
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 1, 0, 2, 1)
        self.fig = plt.Figure()
        self.canvas = FC(self.fig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)
        self.canvas.setObjectName("canvas")
        self.gridLayout.addWidget(self.canvas, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.initialize()
        self.comboBox.currentIndexChanged.connect(self.getRacesInThisYear)
        self.pushButton.clicked.connect(self.getDriversInThisRace)
        self.tableWidget.clicked.connect(self.showPos)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "F1 Analyz v0.2.1"))
        self.pushButton.setText(_translate("MainWindow", "Search"))


if __name__ == "__main__":
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
