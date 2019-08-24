# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets, QtChart
from database_connector import f1db
import bitarray
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC

class CustomedQLineSeries(QtChart.QLineSeries):

    Signal_click = QtCore.pyqtSignal(str,list,QtCore.QPointF,QtCore.QPointF,float,int)
    Signal_name_hovered = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicked.connect(self.emitclick)
        self.hovered.connect(self.highlighted)
        self.hovered.connect(self.emitnameHovered)

    def emitclick(self):
        self.Signal_click.emit(self.name(),self.getAllpoints(),self.getMaxpoint(),self.getMinpoint(),self.getAvgpoint(),self.getStintlength())

    def emitnameHovered(self):
        self.Signal_name_hovered.emit(self.name())

    def getAllpoints(self):
        return list(self.pointsVector())

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

    def getMaxpoint(self):
        curval = 0
        curpt = None
        for i in self.getAllpoints():
            if curpt is None:
                curpt = i
                curval = i.y()
            else:
                if i.y()>curval:
                    curpt = i
                    curval = i.y()
        return curpt

    def getMinpoint(self):
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

    def getAvgpoint(self):
        sum = 0
        for i in self.getAllpoints():
            sum += i.y()
        if self.count():
            sum /= self.count()
        return sum

    def getStintlength(self):
        return self.count()

class CustomedQChartView(QtChart.QChartView):

    Signal_pos = QtCore.pyqtSignal(QtCore.QPointF)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)


class Ui_Dialog(QtWidgets.QDialog):

    def __init__(self, plot_type='QtChart', parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        self.plot_type = plot_type
        self.db = f1db()
        self.checkbox = []
        self.checkbox_legacy = []
        self.years_recorded_in_lap_times = self.db.getAllYearsRecordedInLaptimes()
        self.race_names_recorded_in_lap_times = self.db.getAllRaceNameRecordedInLaptimes()
        self.soft_img = QtGui.QPixmap('Imgs/soft.PNG')
        self.soft_used_img = QtGui.QPixmap('Imgs/soft_used.PNG')
        self.medium_img = QtGui.QPixmap('Imgs/medium.PNG')
        self.medium_used_img = QtGui.QPixmap('Imgs/medium_used.PNG')
        self.hard_img = QtGui.QPixmap('Imgs/hard.PNG')
        self.hard_used_img = QtGui.QPixmap('Imgs/hard_used.PNG')
        self.inter_img = QtGui.QPixmap('Imgs/inter.PNG')
        self.inter_used_img = QtGui.QPixmap('Imgs/inter_used.PNG')
        self.wet_img = QtGui.QPixmap('Imgs/wet.PNG')
        self.wet_used_img = QtGui.QPixmap('Imgs/wet_used.PNG')
        self.tyre_img = {}
        self.tyre_img['hard'] = (self.hard_img)
        self.tyre_img['hard_used'] = (self.hard_used_img)
        self.tyre_img['inter'] = (self.inter_img)
        self.tyre_img['inter_used'] = (self.inter_used_img)
        self.tyre_img['medium'] = (self.medium_img)
        self.tyre_img['medium_used'] = (self.medium_used_img)
        self.tyre_img['soft'] = (self.soft_img)
        self.tyre_img['soft_used'] = (self.soft_used_img)
        self.tyre_img['wet'] = (self.wet_img)
        self.tyre_img['wet_used'] = (self.wet_used_img)
        self.plot_list = []
        self.pitdata = {}
        self.pitlaps = {}
        self.laptime = {}
        self.acctime = {}
        self.name = {}
        self.on_graph_lines = False
        self.m_tooltip = None
        self.hovered_name = None


    def initData(self):
        self.plot_list = []
        self.pitdata = {}
        self.pitlaps = {}
        self.laptime = {}
        self.acctime = {}
        self.name = {}

    def tooltip(self, point, state):
        if state:
            self.on_graph_lines = True
            self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.setToolTip(self.hovered_name+'\n'+str(point.x())+','+str(point.y()))
        else:
            self.on_graph_lines = False
            self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            self.setToolTip('')


    def incrop(self):
        curop = self.windowOpacity()
        if curop >= 1:
            self.timer.timeout.disconnect()
        else:
            curop += 0.01
            self.setWindowOpacity(curop)
            self.repaint()

    def decrop(self):
        curop = self.windowOpacity()
        # if curop <= 1
        # set 1 to disable fade out effect when mouse leaves the window
        if curop <= 0.9:
            self.timer.timeout.disconnect()
        else:
            curop -= 0.01
            self.setWindowOpacity(curop)
            self.repaint()

    def switchtab2_left(self):
        self.tabWidget_2.setCurrentIndex(1)

    def switchtab1_left(self):
        self.tabWidget_2.setCurrentIndex(0)


    def QLineClickedTiming(self, name, QPointslist, maxpt,minpt,avgval,length):

        self.label_left_1.setText("Fastest Lap")
        self.label_left_2.setText("Average Lap")
        self.label_left_3.setText( "Slowest Lap")
        self.label_left_4.setText( "Duration")
        self.label_left_5.setText("Laptime Detail")
        self.setupDetailedTiming(QPointslist)
        self.label_right_1.setText(self.ms2mssmmm(minpt.y()))
        self.label_right_2.setText(self.ms2mssmmm(avgval))
        self.label_right_3.setText(self.ms2mssmmm(maxpt.y()))
        self.label_right_4.setText(str(length))
        self.switchtab2_left()


    def QLineClickedSpace(self, name, QPointslist, maxpt,minpt,avgval,length):

        self.switchtab2_left()
        # self.setupDetailedTiming(QPointslist)
        # self.label_right_1.setText(self.ms2mssmmm(minpt.y()))
        # self.label_right_2.setText(self.ms2mssmmm(avgval))
        # self.label_right_3.setText(self.ms2mssmmm(maxpt.y()))
        # self.label_right_4.setText(str(length))

    def QLineClickedGap(self, name, QPointslist, maxpt,minpt,avgval,length):

        self.switchtab2_left()
        # self.setupDetailedTiming(QPointslist)
        # self.label_right_1.setText(self.ms2mssmmm(minpt.y()))
        # self.label_right_2.setText(self.ms2mssmmm(avgval))
        # self.label_right_3.setText(self.ms2mssmmm(maxpt.y()))
        # self.label_right_4.setText(str(length))


    def setupDetailedTiming(self, QPointslist):
        self.detailedTiming.setColumnCount(2)
        self.detailedTiming.setRowCount(len(QPointslist))
        self.detailedTiming.setHorizontalHeaderLabels(['Lap', 'Timing',])
        rowcount = 0
        for i in QPointslist:
            item0 = QtWidgets.QTableWidgetItem(str(int(i.x())))
            # item0.setFont(font)
            # item0.setBackground(color)
            # item0.setForeground(QtGui.QColor(255, 255, 255))
            item0.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.detailedTiming.setItem(rowcount, 0, item0)
            item1 = QtWidgets.QTableWidgetItem(self.ms2mssmmm((int(i.y()))))
            # item0.setFont(font)
            # item0.setBackground(color)
            # item0.setForeground(QtGui.QColor(255, 255, 255))
            item1.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.detailedTiming.setItem(rowcount, 1, item1)
            rowcount += 1

    def enterEvent(self, event):
        self.timer = QtCore.QTimer()
        self.timer.start(5)
        self.timer.timeout.connect(self.incrop)

    def leaveEvent(self, event):
        self.timer = QtCore.QTimer()
        self.timer.start(5)
        self.timer.timeout.connect(self.decrop)

    def storeHoveredName(self, name):
        self.hovered_name = name

    def initialize(self):
        self.hide_pit_eelap = False
        max_year = 0
        for i in self.years_recorded_in_lap_times:
            if i['year'] > max_year:
                max_year = i['year']
            self.comboBox.addItem(str(i['year']))
        self.comboBox.setCurrentText(str(max_year))
        year = max_year
        races = self.db.getRacesInAYearRecordedInLaptimes(year)
        for i in races:
            self.comboBox_2.addItem(i['name'])
        latest_race = self.db.getLatestRaceThisYear(year)
        self.comboBox_2.setCurrentText(self.db.getRaceNameByRaceId(latest_race[0]['max(raceId)'])[0]['name'])

    def plotTimeGraph(self):
        # try:
        self.laptimefig.clear()
        ax = self.laptimefig.add_subplot(111)
        # ax.cla()
        ax.grid()
        legends = []
        length = len(self.drivers)
        if self.status == 'lap':
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]

                    timing = self.db.getLaptimesViaDriverIDRaceID(driver['driverId'], self.raceId)
                    pitlaps = []
                    pitdata = self.db.getPitstopByRaceIdDriverId(self.raceId, driver['driverId'])
                    if len(pitdata):
                        for i in pitdata:
                            pitlaps.append(i['lap'])
                            pitlaps.append(i['lap'] + 1)
                    plot_pool_x = []
                    plot_pool_y = []
                    for k in timing:
                        if k['lap'] >= self.min_cal_lap and k['lap'] <= self.max_cal_lap:
                            if k['lap'] not in pitlaps:
                                time0 = self.mssmmm2ms(k['time'])
                                plot_pool_x.append(k['lap'])
                                plot_pool_y.append(time0)
                            else:
                                if not self.hide_pit_eelap:
                                    time0 = self.mssmmm2ms(k['time'])
                                    plot_pool_x.append(k['lap'])
                                    plot_pool_y.append(time0)
                    name = self.db.getDriversByDriverID(driver['driverId'])[0]['surname']
                    ax.plot(plot_pool_x, plot_pool_y, marker=',')
                    legends.append(name)
            self.laptimefig.legend(legends, loc=1)
            self.laptimefig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                            bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Laptime: ms', labelpad=0.5)
            self.canvas.draw()  #
        elif self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.laptime.keys():
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                else:
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']
            # plot_pool_x = []
            # plot_pool_y = []
            for k in a.keys():
                plot_pool_x = []
                plot_pool_y = []
                for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                    if lap in self.laptime[k].keys():
                        if lap not in self.pitlaps[k]:
                            time0 = self.laptime[k][lap]
                            plot_pool_x.append(lap)
                            plot_pool_y.append(time0)
                        else:
                            if not self.hide_pit_eelap:
                                time0 = self.laptime[k][lap]
                                plot_pool_x.append(lap)
                                plot_pool_y.append(time0)
                # plot_pool_x.append(None)
                # plot_pool_y.append(None)
                ax.plot(plot_pool_x, plot_pool_y, label=self.name[k])
            # ax.scatter(plot_pool_x, plot_pool_y)
            # ax.plot(plot_pool_x, plot_pool_y, marker=',                            ')
            # self.laptimefig.legend(legends, loc=1)
            self.laptimefig.legend(prop={'size': 6})
            self.laptimefig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                            bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Laptime: ms', labelpad=0.5)
            self.canvas.draw()  #

    # except Exception as e:
    #     print(e)

    def plotSpaceGapGraph(self):
        # try:
        self.spacegapfig.clear()
        ax = self.spacegapfig.add_subplot(111)
        # ax.cla()
        ax.grid()
        legends = []
        length = len(self.drivers)
        timing_pools = []
        driver_pools = []
        if self.status == 'lap':
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing_accum = self.db.getLaptimesAccumViaRaceIdDriverId(self.raceId, driver['driverId'])
                    # print(timing_accum)
                    timing_pools.append(timing_accum)
                    driver_pools.append(driver)

            for i in range(len(timing_pools)):
                for j in range(i + 1, len(timing_pools)):
                    plot_pool_x = []
                    plot_pool_y = []
                    pitlaps = []
                    pitdata_i = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[i]['driverId'])
                    pitdata_j = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[j]['driverId'])
                    if len(pitdata_i):
                        for pi in pitdata_i:
                            pitlaps.append(pi['lap'])
                            pitlaps.append(pi['lap'] + 1)
                    if len(pitdata_j):
                        for pj in pitdata_j:
                            pitlaps.append(pj['lap'])
                            pitlaps.append(pj['lap'] + 1)
                    for k in range(len(timing_pools[i])):
                        if timing_pools[i][k]['lap'] >= self.min_cal_lap and timing_pools[i][k]['lap'] <= self.max_cal_lap:
                            try:
                                if timing_pools[i][k]['lap'] not in pitlaps and timing_pools[j][k]['lap'] not in pitlaps:
                                    time0 = timing_pools[i][k]['timeElapsed']
                                    time1 = timing_pools[j][k]['timeElapsed']
                                    delta_time = time0 - time1
                                    plot_pool_x.append(timing_pools[i][k]['lap'])
                                    plot_pool_y.append(delta_time)
                                else:
                                    if not self.hide_pit_eelap:
                                        time0 = timing_pools[i][k]['timeElapsed']
                                        time1 = timing_pools[j][k]['timeElapsed']
                                        delta_time = time0 - time1
                                        plot_pool_x.append(timing_pools[i][k]['lap'])
                                        plot_pool_y.append(delta_time)
                            except IndexError:
                                pass
                    name0 = self.db.getDriversByDriverID(driver_pools[i]['driverId'])[0]['surname']
                    name1 = self.db.getDriversByDriverID(driver_pools[j]['driverId'])[0]['surname']
                    ax.plot(plot_pool_x, plot_pool_y)
                    legends.append(name0 + ' and ' + name1)
            self.spacegapfig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                             bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Gap: ms', labelpad=0.5)
            self.spacegapfig.legend(legends, loc=1)
            self.canvas_3.draw()  #
            # except Exception as e:
            #     print(e)
        elif self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.acctime.keys():
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                      self.raceId, a[i])
                else:
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                      self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']
            # plot_pool_x = []
            # plot_pool_y = []
            for i in a.keys():
                for j in a.keys():
                    if i > j:
                        plot_pool_x = []
                        plot_pool_y = []
                        for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                            if lap in self.acctime[i].keys() and lap in self.acctime[j].keys():
                                if lap not in self.pitlaps[i] and lap not in self.pitlaps[j]:
                                    diff = self.acctime[i][lap] - self.acctime[j][lap]
                                    plot_pool_x.append(lap)
                                    plot_pool_y.append(diff)
                                else:
                                    if not self.hide_pit_eelap:
                                        diff = self.acctime[i][lap] - self.acctime[j][lap]
                                        plot_pool_x.append(lap)
                                        plot_pool_y.append(diff)
                        ax.plot(plot_pool_x, plot_pool_y, label=self.name[i] + ' and ' + self.name[j])
                        # plot_pool_x.append(None)
                        # plot_pool_y.append(None)
            # ax.scatter(plot_pool_x, plot_pool_y)
            self.spacegapfig.legend(prop={'size': 6}, ncol=4, loc=1)
            self.spacegapfig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                             bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Gap: ms', labelpad=0.5)
            self.spacegapfig.legend(legends, loc=1)
            self.canvas_3.draw()  #

    def plotGapGraph(self):
        # try:
        self.speedgapfig.clear()
        ax = self.speedgapfig.add_subplot(111)
        # ax.cla()
        ax.grid()
        legends = []
        length = len(self.drivers)
        timing_pools = []
        driver_pools = []
        pitdata = {}
        if self.status == 'lap':
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing = self.db.getLaptimesViaDriverIDRaceID(driver['driverId'], self.raceId)
                    timing_pools.append(timing)
                    driver_pools.append(driver)
            for i in range(len(timing_pools)):
                for j in range(i + 1, len(timing_pools)):
                    plot_pool_x = []
                    plot_pool_y = []
                    pitlaps = []
                    pitdata_i = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[i]['driverId'])
                    pitdata_j = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[j]['driverId'])
                    if len(pitdata_i):
                        for pi in pitdata_i:
                            pitlaps.append(pi['lap'])
                            pitlaps.append(pi['lap'] + 1)
                    if len(pitdata_j):
                        for pj in pitdata_j:
                            pitlaps.append(pj['lap'])
                            pitlaps.append(pj['lap'] + 1)
                    for k in range(len(timing_pools[i])):
                        if timing_pools[i][k]['lap'] >= self.min_cal_lap and timing_pools[i][k]['lap'] <= self.max_cal_lap:
                            try:
                                if timing_pools[i][k]['lap'] not in pitlaps and timing_pools[j][k]['lap'] not in pitlaps:
                                    time0 = self.mssmmm2ms(timing_pools[i][k]['time'])
                                    time1 = self.mssmmm2ms(timing_pools[j][k]['time'])
                                    delta_time = time0 - time1
                                    plot_pool_x.append(timing_pools[i][k]['lap'])
                                    plot_pool_y.append(delta_time)
                                else:
                                    if not self.hide_pit_eelap:
                                        time0 = self.mssmmm2ms(timing_pools[i][k]['time'])
                                        time1 = self.mssmmm2ms(timing_pools[j][k]['time'])
                                        delta_time = time0 - time1
                                        plot_pool_x.append(timing_pools[i][k]['lap'])
                                        plot_pool_y.append(delta_time)
                            except IndexError:
                                pass
                    name0 = self.db.getDriversByDriverID(driver_pools[i]['driverId'])[0]['surname']
                    name1 = self.db.getDriversByDriverID(driver_pools[j]['driverId'])[0]['surname']
                    ax.plot(plot_pool_x, plot_pool_y, marker=',')
                    # ax.scatter(plot_pool_x, plot_pool_y, marker=',')
                    legends.append(name0 + ' and ' + name1)
            self.speedgapfig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                             bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Speed Difference: ms', labelpad=0.5)
            self.speedgapfig.legend(legends, loc=1)
            self.canvas_2.draw()  #
            # except Exception as e:
            #     print(e)
        elif self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.laptime.keys():
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                else:
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']

            # plot_pool_x = []
            # plot_pool_y = []
            for i in a.keys():
                for j in a.keys():
                    plot_pool_x = []
                    plot_pool_y = []
                    if i > j:
                        for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                            if lap in self.laptime[i].keys() and lap in self.laptime[j].keys():
                                if lap not in self.pitlaps[i] and lap not in self.pitlaps[j]:
                                    diff = self.laptime[i][lap] - self.laptime[j][lap]
                                    plot_pool_x.append(lap)
                                    plot_pool_y.append(diff)
                                else:
                                    if not self.hide_pit_eelap:
                                        diff = self.laptime[i][lap] - self.laptime[j][lap]
                                        plot_pool_x.append(lap)
                                        plot_pool_y.append(diff)
                        ax.plot(plot_pool_x, plot_pool_y, label=self.name[i] + ' and ' + self.name[j])
                        # plot_pool_x.append(None)
                        # plot_pool_y.append(None)
            # ax.plot(plot_pool_x, plot_pool_y)
            self.speedgapfig.legend(prop={'size': 6}, ncol=4)
            self.speedgapfig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                             bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Speed Difference: ms', labelpad=0.5)
            self.speedgapfig.legend(legends, loc=1)
            self.canvas_2.draw()  #

    def plotTimeGraphQChart(self):
        self.timegraph = QtChart.QChart()
        self.timegraph.setAcceptHoverEvents(True)

        if self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.laptime.keys():
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId,
                                                                                 a[i])
                else:
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId,
                                                                                 a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']
            for k in a.keys():
                plot_pool = CustomedQLineSeries()
                for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                    if lap in self.laptime[k].keys():
                        if lap not in self.pitlaps[k]:
                            time0 = self.laptime[k][lap]
                            plot_pool.append(lap, time0)
                        else:
                            if not self.hide_pit_eelap:
                                time0 = self.laptime[k][lap]
                                plot_pool.append(lap, time0)
                plot_pool.setName(self.name[k])
                plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                plot_pool.Signal_click.connect(self.QLineClickedTiming)
                plot_pool.hovered.connect(self.tooltip)
                # plot_pool.hovered.connect(self.chartView.showTooltip)
                self.timegraph.addSeries(plot_pool)
        elif self.status == 'lap':
            length = len(self.drivers)
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing = self.db.getLaptimesViaDriverIDRaceID(driver['driverId'], self.raceId)
                    pitlaps = []
                    pitdata = self.db.getPitstopByRaceIdDriverId(self.raceId, driver['driverId'])
                    if len(pitdata):
                        for i in pitdata:
                            pitlaps.append(i['lap'])
                            pitlaps.append(i['lap'] + 1)
                    plot_pool = CustomedQLineSeries()
                    for k in timing:
                        if self.min_cal_lap <= k['lap'] <= self.max_cal_lap:
                            if k['lap'] not in pitlaps:
                                time0 = self.mssmmm2ms(k['time'])
                                plot_pool.append(k['lap'], time0)
                            else:
                                if not self.hide_pit_eelap:
                                    time0 = self.mssmmm2ms(k['time'])
                                    plot_pool.append(k['lap'], time0)
                    name = self.db.getDriversByDriverID(driver['driverId'])[0]['surname']
                    plot_pool.setName(name)
                    plot_pool.Signal_click.connect(self.QLineClickedTiming)
                    plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                    plot_pool.hovered.connect(self.tooltip)
                    self.timegraph.addSeries(plot_pool)

        # x_axis = QtChart.QValueAxis()
        # x_axis.setTickCount(6)
        # x_axis.setMinorTickCount(6)
        # y_axis = QtChart.QValueAxis()
        # y_axis.setTickCount(6)
        # y_axis.setMinorTickCount(6)
        # c.setAxisX(x_axis)
        # c.setAxisY(y_axis)
        self.timegraph.createDefaultAxes()
        # self.m_coordX_timegraph = QtWidgets.QGraphicsSimpleTextItem(self.timegraph)
        # self.m_coordX_timegraph.setPos(self.timegraph.size().width() / 2 - 50, self.timegraph.size().height())
        # self.m_coordX_timegraph.setText("X: ")
        # self.m_coordY_timegraph =QtWidgets.QGraphicsSimpleTextItem(self.timegraph)
        # self.m_coordY_timegraph.setPos(self.timegraph.size().width() / 2 + 50, self.timegraph.size().height())
        # self.m_coordY_timegraph.setText("Y: ")
        self.chartView.setChart(self.timegraph)
        return

    def plotSpaceGapGraphQChart(self):
        self.spacegapgraph = QtChart.QChart()
        if self.status == 'lap':
            timing_pools = []
            driver_pools = []
            length = len(self.drivers)
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing_accum = self.db.getLaptimesAccumViaRaceIdDriverId(self.raceId, driver['driverId'])
                    # print(timing_accum)
                    timing_pools.append(timing_accum)
                    driver_pools.append(driver)
            for i in range(len(timing_pools)):
                for j in range(i + 1, len(timing_pools)):
                    plot_pool = CustomedQLineSeries()
                    pitlaps = []
                    pitdata_i = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[i]['driverId'])
                    pitdata_j = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[j]['driverId'])
                    if len(pitdata_i):
                        for pi in pitdata_i:
                            pitlaps.append(pi['lap'])
                            pitlaps.append(pi['lap'] + 1)
                    if len(pitdata_j):
                        for pj in pitdata_j:
                            pitlaps.append(pj['lap'])
                            pitlaps.append(pj['lap'] + 1)
                    for k in range(len(timing_pools[i])):
                        if self.min_cal_lap <= timing_pools[i][k]['lap'] <= self.max_cal_lap:
                            try:
                                if timing_pools[i][k]['lap'] not in pitlaps and timing_pools[j][k]['lap'] not in pitlaps:
                                    time0 = timing_pools[i][k]['timeElapsed']
                                    time1 = timing_pools[j][k]['timeElapsed']
                                    delta_time = time0 - time1
                                    plot_pool.append(timing_pools[i][k]['lap'], delta_time)
                                else:
                                    if not self.hide_pit_eelap:
                                        time0 = timing_pools[i][k]['timeElapsed']
                                        time1 = timing_pools[j][k]['timeElapsed']
                                        delta_time = time0 - time1
                                        plot_pool.append(timing_pools[i][k]['lap'], delta_time)
                            except IndexError:
                                pass
                    name0 = self.db.getDriversByDriverID(driver_pools[i]['driverId'])[0]['surname']
                    name1 = self.db.getDriversByDriverID(driver_pools[j]['driverId'])[0]['surname']
                    plot_pool.setName(name0 + ' and ' + name1)
                    plot_pool.Signal_click.connect(self.QLineClickedSpace)
                    plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                    plot_pool.hovered.connect(self.tooltip)
                    self.spacegapgraph.addSeries(plot_pool)
            # except Exception as e:
            #     print(e)
        elif self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.acctime.keys():
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                      self.raceId, a[i])
                else:
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                      self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']
            for i in a.keys():
                for j in a.keys():
                    if i > j:
                        plot_pool = CustomedQLineSeries()
                        for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                            if lap in self.acctime[i].keys() and lap in self.acctime[j].keys():
                                if lap not in self.pitlaps[i] and lap not in self.pitlaps[j]:
                                    diff = self.acctime[i][lap] - self.acctime[j][lap]
                                    plot_pool.append(lap, diff)
                                else:
                                    if not self.hide_pit_eelap:
                                        diff = self.acctime[i][lap] - self.acctime[j][lap]
                                        plot_pool.append(lap, diff)
                        plot_pool.setName(self.name[i] + ' and ' + self.name[j])
                        plot_pool.Signal_click.connect(self.QLineClickedSpace)
                        plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                        plot_pool.hovered.connect(self.tooltip)
                        self.spacegapgraph.addSeries(plot_pool)
        self.spacegapgraph.createDefaultAxes()
        self.chartView_2.setChart(self.spacegapgraph)

    def plotGapGraphQChart(self):
        self.timegapgraph = QtChart.QChart()
        if self.status == 'lap':
            length = len(self.drivers)
            timing_pools = []
            driver_pools = []
            pitdata = {}
            for i in range(length):
                if self.laststate[i]:
                    driver = self.drivers[i]
                    timing = self.db.getLaptimesViaDriverIDRaceID(driver['driverId'], self.raceId)
                    timing_pools.append(timing)
                    driver_pools.append(driver)
            for i in range(len(timing_pools)):
                for j in range(i + 1, len(timing_pools)):
                    plot_pool = CustomedQLineSeries()
                    pitlaps = []
                    pitdata_i = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[i]['driverId'])
                    pitdata_j = self.db.getPitstopByRaceIdDriverId(self.raceId, driver_pools[j]['driverId'])
                    if len(pitdata_i):
                        for pi in pitdata_i:
                            pitlaps.append(pi['lap'])
                            pitlaps.append(pi['lap'] + 1)
                    if len(pitdata_j):
                        for pj in pitdata_j:
                            pitlaps.append(pj['lap'])
                            pitlaps.append(pj['lap'] + 1)
                    for k in range(len(timing_pools[i])):
                        if self.min_cal_lap <= timing_pools[i][k]['lap'] <= self.max_cal_lap:
                            try:
                                if timing_pools[i][k]['lap'] not in pitlaps and timing_pools[j][k][
                                    'lap'] not in pitlaps:
                                    time0 = self.mssmmm2ms(timing_pools[i][k]['time'])
                                    time1 = self.mssmmm2ms(timing_pools[j][k]['time'])
                                    delta_time = time0 - time1
                                    plot_pool.append(timing_pools[i][k]['lap'], delta_time)
                                else:
                                    if not self.hide_pit_eelap:
                                        time0 = self.mssmmm2ms(timing_pools[i][k]['time'])
                                        time1 = self.mssmmm2ms(timing_pools[j][k]['time'])
                                        delta_time = time0 - time1
                                        plot_pool.append(timing_pools[i][k]['lap'], delta_time)
                            except IndexError:
                                pass
                    name0 = self.db.getDriversByDriverID(driver_pools[i]['driverId'])[0]['surname']
                    name1 = self.db.getDriversByDriverID(driver_pools[j]['driverId'])[0]['surname']
                    plot_pool.setName(name0 + ' and ' + name1)
                    plot_pool.Signal_click.connect(self.QLineClickedGap)
                    plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                    plot_pool.hovered.connect(self.tooltip)
                    self.timegapgraph.addSeries(plot_pool)
            # except Exception as e:
            #     print(e)
        elif self.status == 'stint':
            a = {}
            for i in self.plot_list:
                if int(i[0]) not in a.keys():
                    a[int(i[0])] = []
                    a[int(i[0])].append(i[2])
                else:
                    a[int(i[0])].append(i[2])
            for i in a.keys():
                if i not in self.pitdata.keys():
                    self.pitdata[i] = self.db.getPitstopByRaceIdDriverId(self.raceId, self.drivers[i]['driverId'])
                    self.pitlaps[i] = []
                for pi in self.pitdata[i]:
                    self.pitlaps[i].append(pi['lap'])
                    self.pitlaps[i].append(pi['lap'] + 1)
                if i not in self.laptime.keys():
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                else:
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'],
                                                                                 self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']

            for i in a.keys():
                for j in a.keys():
                    if i > j:
                        plot_pool = CustomedQLineSeries()
                        for lap in range(self.min_cal_lap, self.max_cal_lap + 1):
                            if lap in self.laptime[i].keys() and lap in self.laptime[j].keys():
                                if lap not in self.pitlaps[i] and lap not in self.pitlaps[j]:
                                    diff = self.laptime[i][lap] - self.laptime[j][lap]
                                    plot_pool.append(lap, diff)
                                else:
                                    if not self.hide_pit_eelap:
                                        diff = self.laptime[i][lap] - self.laptime[j][lap]
                                        plot_pool.append(lap, diff)
                        plot_pool.setName(self.name[i] + ' and ' + self.name[j])
                        plot_pool.Signal_click.connect(self.QLineClickedGap)
                        plot_pool.Signal_name_hovered.connect(self.storeHoveredName)
                        plot_pool.hovered.connect(self.tooltip)
                        self.timegapgraph.addSeries(plot_pool)
        self.timegapgraph.createDefaultAxes()
        self.chartView_3.setChart(self.timegapgraph)

    def plotAll(self):
        # print('-' * 20)
        if self.plot_type == 'QtChart':
            t0 = time.time()
            self.label_5.setText('Plotting Time Graph...')
            self.label_5.repaint()
            self.plotTimeGraphQChart()
            # print('Time Graph(QtChart):', time.time() - t0)
            t1 = time.time()
            self.label_5.setText('Plotting Car Gap Graph...')
            self.label_5.repaint()
            self.plotSpaceGapGraphQChart()
            # print('Space Graph(QtChart):', time.time() - t1)
            t2 = time.time()
            self.label_5.setText('Plotting Time Gap Graph...')
            self.label_5.repaint()
            self.plotGapGraphQChart()
            # print('Time Gap Graph(QtChart):', time.time() - t2)
            text0 = 'Plot Graph(QtChart):' + str(time.time() - t0)
            # print(text0)
            self.label.setText(text0)
            self.label_5.setText('')
            self.label_5.repaint()

            # self.chartView.setMouseTracking(True)
            # self.chartView_2.setMouseTracking(True)
            # self.chartView_3.setMouseTracking(True)
            # self.tab.setMouseTracking(True)
            # self.tab_2.setMouseTracking(True)
            # self.tab_3.setMouseTracking(True)
            # self.tabWidget.setMouseTracking(True)

        elif self.plot_type == 'matplotlib':
            t0 = time.time()
            self.plotTimeGraph()
            self.label_5.setText('Plotting Time Graph...')
            self.label_5.repaint()
            t1 = time.time()
            self.plotSpaceGapGraph()
            self.label_5.setText('Plotting Car Gap Graph...')
            self.label_5.repaint()
            t2 = time.time()
            self.plotGapGraph()
            self.label_5.setText('Plotting Time Gap Graph...')
            self.label_5.repaint()
            text0 = 'Plot Graph(matplotlib.pyplot):' + str(time.time() - t0)
            print(text0)
            self.label.setText(text0)
            self.label_5.setText('')
            self.label_5.repaint()
        self.setMouseTracking(True)

    def hidePitChecked(self):
        boolean = self.checkBox.checkState()
        self.hide_pit_eelap = bool(boolean)
        # print(self.hide_pit_eelap)
        self.plotAll()

    def getRacesInThisYear(self):
        self.comboBox_2.clear()
        year = self.comboBox.currentText()
        races = self.db.getRacesInAYearRecordedInLaptimes(year)
        for i in races:
            self.comboBox_2.addItem(i['name'])

    def unlockPushbutton(self):
        self.pushButton.setEnabled(True)

    def checkAll(self):
        self.checkBox_2.setEnabled(False)
        self.checkBox_2.repaint()
        if self.checkBox_2.checkState():
            if self.status == 'stint':
                plot_list = []
                for i in self.checkbox:
                    i.setCheckState(QtCore.Qt.Checked)
                    string = i.objectName().split('-')
                    plot_list.append(string)
                self.plot_list = plot_list
            elif self.status == 'lap':
                for i in range(self.tableWidget.rowCount()):
                    self.tableWidget.item(i, 0).setCheckState(QtCore.Qt.Checked)
                self.laststate.setall(True)
        else:
            if self.status == 'stint':
                for i in self.checkbox:
                    i.setCheckState(QtCore.Qt.Unchecked)
                self.plot_list = []
            elif self.status == 'lap':
                for i in range(self.tableWidget.rowCount()):
                    self.tableWidget.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
                self.laststate.setall(False)
        self.plotAll()
        self.checkBox_2.setEnabled(True)
        self.checkBox_2.repaint()

    def getDriversInThisRace(self):
        # self.canvas_2.clear()
        # self.spacegapfig.clear()
        # self.speedgapfig.clear()
        self.pushButton.setEnabled(False)
        self.checkbox = []
        year = self.comboBox.currentText()
        race_name = self.comboBox_2.currentText()
        raceId = self.db.getRaceIDByYearName(year, race_name)
        drivers_id = self.db.getGridByRaceID(raceId[0]['raceId'])
        # self.pitdata = self.db.getPitstopsByRaceId(raceId[0]['raceId'])
        self.initTable(drivers_id, raceId[0]['raceId'])
        self.max_lap = self.db.getMaximumLap(raceId[0]['raceId'])[0]['max(lap)']
        self.max_cal_lap = self.max_lap
        # print(self.max_lap)
        self.min_lap = 1
        self.min_cal_lap = self.min_lap
        if self.max_lap is not None:
            self.spinBox.setMinimum(1)
            # print(self.db.getMaximumLap(raceId[0]['raceId']))
            self.spinBox.setMaximum(self.max_lap)
            self.spinBox.setSingleStep(1)
            self.spinBox_2.setMinimum(1)
            self.spinBox_2.setMaximum(self.max_lap)
            self.spinBox_2.setSingleStep(1)
            self.spinBox_2.setValue(self.max_lap)
            self.spinBox_2.setEnabled(True)
            self.spinBox.setEnabled(True)
        else:
            self.spinBox_2.setEnabled(False)
            self.spinBox.setEnabled(False)

    def showPos(self):

        length = self.tableWidget.rowCount()
        curstate = bitarray.bitarray(length)
        curstate.setall(False)
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(i, 0).checkState():
                curstate[i] = 1
        if bitarray.bitdiff(curstate, self.laststate):
            self.laststate = curstate
            # print(self.laststate)
            self.plotAll()

    def mssmmm2ms(self, time):
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
        return millisecond + 1000 * second + 60000 * minute

    def ms2mssmmm(self, time):
        minute = int(time/60000)
        second = int((time-minute*60000)/1000)
        millisecond = int(time-minute*60000-second*1000)
        if minute >= 1:
            retstr = str(minute)+':'
        else:
            retstr = ''
        retstr += str(second)
        retstr += '.'
        if millisecond < 100:
            retstr += '0'
        if millisecond < 10:
            retstr += '0'
        retstr += str(millisecond)

        return retstr

    def changeStartLap(self):
        cur_lap = self.spinBox.value()
        self.spinBox_2.setMinimum(cur_lap)
        self.min_cal_lap = cur_lap
        self.plotAll()

    def changeEndLap(self):
        self.max_cal_lap = self.spinBox_2.value()
        self.plotAll()

    def tyreClicked(self):
        plot_list = []
        for i in self.checkbox:
            # print(i.objectName())
            if i.checkState():
                string = i.objectName().split('-')
                plot_list.append(string)
        self.plot_list = plot_list
        self.plotAll()

    def initTable(self, drivers, raceId):
        self.switchtab1_left()
        stint_data = self.db.getTyreStintByRaceId(raceId)
        if len(stint_data):
            self.initData()
            self.status = 'stint'
            self.tableWidget.clearContents()
            self.tableWidget.setColumnCount(6)
            self.laststate = bitarray.bitarray(len(drivers))
            self.lastplotedstate = bitarray.bitarray(len(drivers))
            self.drivers = drivers
            self.raceId = raceId
            self.laststate.setall(False)
            self.lastplotedstate.setall(False)
            self.tableWidget.verticalHeader().setVisible(False)
            self.tableWidget.horizontalHeader().setStretchLastSection(False)
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.setHorizontalHeaderLabels(['C', 'Code', 'Name', 'Grid', 'Result', 'Pitstops','Tyre'])
            self.tableWidget.setHorizontalHeaderLabels(['Code', 'Name', 'Grid', 'End', 'Pits', 'Tyre'])
            self.tableWidget.setRowCount(len(drivers))
            rowcount = 0
            # self.pitstops = self.db.getPitstopsByRaceId(raceId)

            for num in range(len(drivers)):
                i = drivers[num]
                # table_color = QtGui.QPalette()
                # table_color.setColor(QtGui.QPalette.Base, QtGui.QColor(0,0,0))
                pitstops = self.db.getPitstopByRaceIdDriverId(raceId, i['driverId'])
                pitstop_counts = len(pitstops)
                font = QtGui.QFont()
                color = QtGui.QColor(192, 192, 192, 128)
                finish_pos_raw = self.db.getResultStandingByRaceIDandDriverId(raceId, i['driverId'])
                finish_pos = finish_pos_raw[0]['position']
                start_pos_raw = self.db.getStartposByRaceIDDriverID(raceId, i['driverId'])
                try:
                    start_pos = start_pos_raw[0]['position']
                except IndexError:
                    start_pos = ''
                finish_status_Id = self.db.getResultStatusIDByRaceIDandDriverID(raceId, i['driverId'])[0]['statusId']
                finish_status = self.db.getFinishStatusNameByStatusID(finish_status_Id)[0]['status']
                driver_detail = self.db.getDriversByDriverID(i['driverId'])
                check = QtWidgets.QTableWidgetItem()
                check.setCheckState(QtCore.Qt.Unchecked)
                check.setBackground(color)
                if finish_pos is not None:
                    if finish_pos == 1:
                        color = QtGui.QColor(255, 215, 0, 128)
                    elif finish_pos == 2:
                        color = QtGui.QColor(128, 128, 128, 128)
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

                check.setBackground(color)
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
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif 3 <= finish_status_Id <= 10 or 20 <= finish_status_Id <= 44 or 46 <= finish_status_Id <= 49 or finish_status_Id == 51 \
                            or finish_status_Id == 54 or finish_status_Id == 56 or 59 <= finish_status_Id <= 61 or 63 <= finish_status_Id <= 76 \
                            or 78 <= finish_status_Id <= 80 or 82 <= finish_status_Id <= 87 or finish_status_Id == 89 or 91 <= finish_status_Id <= 95 \
                            or 98 <= finish_status_Id <= 110 or finish_status_Id == 121 or finish_status_Id == 126 or 129 <= finish_status_Id <= 132 \
                            or 135 <= finish_status_Id <= 137:
                        finishpos = QtWidgets.QTableWidgetItem("RET")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 62:
                        finishpos = QtWidgets.QTableWidgetItem("NC")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 77:
                        finishpos = QtWidgets.QTableWidgetItem("107")
                        check.setFlags(
                            QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 81:
                        finishpos = QtWidgets.QTableWidgetItem("DNQ")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 90:
                        finishpos = QtWidgets.QTableWidgetItem("NR")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 96:
                        finishpos = QtWidgets.QTableWidgetItem("EX")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 97:
                        finishpos = QtWidgets.QTableWidgetItem("DNPQ")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                finishpos.setFont(font)
                finishpos.setBackground(color)
                if finish_pos is None:
                    finishpos.setForeground(QtGui.QColor(255, 255, 255))
                finishpos.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(rowcount, 3, finishpos)
                pitstops = QtWidgets.QTableWidgetItem(str(pitstop_counts))
                # pitstops.setCheckState(QtCore.Qt.Unchecked)
                pitstops.setFont(font)
                pitstops.setBackground(color)
                pitstops.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if finish_pos is None:
                    pitstops.setForeground(QtGui.QColor(255, 255, 255))
                self.tableWidget.setItem(rowcount, 4, pitstops)

                list_height = 20
                # tyre_stints = [{'lap_on':1,'laps':1,'tyre':0},{'lap_on':2,'laps':18,'tyre':3},{'lap_on':2,'laps':18,'tyre':3},{'lap_on':2,'laps':18,'tyre':3},{'lap_on':2,'laps':18,'tyre':3},{'lap_on':20,'laps':32,'tyre':4},{'lap_on':52,'laps':54,'tyre':6},{'lap_on':106,'laps':60,'tyre':8}]
                tyre_stints = self.db.getTyreStintsByRaceIdDriverId(raceId, i['driverId'])
                layout_tyres = QtWidgets.QHBoxLayout()
                layout_tyres.setAlignment(QtCore.Qt.AlignLeft)
                pal = QtGui.QPalette()
                pal.setColor(QtGui.QPalette.Base, color)
                check_count = 0
                for i in tyre_stints:
                    label_stint = QtWidgets.QLabel()
                    label_stint.setFixedWidth(20)
                    label_stint.setPixmap(self.tyre_img[i['tyreName']].scaled(list_height, list_height))
                    label_stint.setAutoFillBackground(True)
                    laps_stint = QtWidgets.QLabel()
                    laps_stint.setFixedWidth(18)
                    laps_stint.setText(str(i['laps']))
                    stint_1 = QtWidgets.QCheckBox()
                    stint_1.setFixedWidth(30)
                    # stint_1.setFixedHeight(list_height)
                    stint_1.setCheckState(QtCore.Qt.Unchecked)
                    stint_1.setObjectName(str(rowcount) + '-' + str(5) + '-' + str(check_count))
                    self.checkbox.append(stint_1)
                    # print(self.checkbox)
                    check_count += 1
                    check_color = QtGui.QPalette()
                    check_color.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
                    stint_1.setPalette(check_color)
                    layout_tyres.addWidget(label_stint, QtCore.Qt.AlignLeft)
                    layout_tyres.addWidget(laps_stint, QtCore.Qt.AlignLeft)
                    layout_tyres.addWidget(stint_1, QtCore.Qt.AlignLeft)
                cellWidget = QtWidgets.QWidget()
                cellWidget.setLayout(layout_tyres)
                cellWidget.setAutoFillBackground(True)
                cellWidget.setPalette(pal)
                self.tableWidget.setCellWidget(rowcount, 5, cellWidget)
                # self.tableWidget.setItem(rowcount, 0, check)
                self.tableWidget.resizeRowToContents(rowcount)
                rowcount += 1
            self.connection()
        else:
            self.status = 'lap'
            self.tableWidget.clearContents()
            self.tableWidget.setColumnCount(6)
            self.laststate = bitarray.bitarray(len(drivers))
            self.lastplotedstate = bitarray.bitarray(len(drivers))
            self.drivers = drivers
            self.raceId = raceId
            self.laststate.setall(False)
            self.lastplotedstate.setall(False)
            self.tableWidget.verticalHeader().setVisible(False)
            self.tableWidget.horizontalHeader().setStretchLastSection(False)
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            # self.tableWidget.setHorizontalHeaderLabels(['C', 'Code', 'Name', 'Grid', 'Result', 'Pitstops','Tyre'])
            self.tableWidget.setHorizontalHeaderLabels(['Checked', 'Code', 'Name', 'Grid', 'End', 'Pits'])
            self.tableWidget.setRowCount(len(drivers))
            rowcount = 0
            # self.pitstops = self.db.getPitstopsByRaceId(raceId)

            for num in range(len(drivers)):
                i = drivers[num]
                # table_color = QtGui.QPalette()
                # table_color.setColor(QtGui.QPalette.Base, QtGui.QColor(0,0,0))
                pitstops = self.db.getPitstopByRaceIdDriverId(raceId, i['driverId'])
                pitstop_counts = len(pitstops)
                font = QtGui.QFont()
                color = QtGui.QColor(192, 192, 192, 128)
                finish_pos_raw = self.db.getResultStandingByRaceIDandDriverId(raceId, i['driverId'])
                finish_pos = finish_pos_raw[0]['position']
                start_pos_raw = self.db.getStartposByRaceIDDriverID(raceId, i['driverId'])
                try:
                    start_pos = start_pos_raw[0]['position']
                except IndexError:
                    start_pos = ''
                finish_status_Id = self.db.getResultStatusIDByRaceIDandDriverID(raceId, i['driverId'])[0]['statusId']
                finish_status = self.db.getFinishStatusNameByStatusID(finish_status_Id)[0]['status']
                driver_detail = self.db.getDriversByDriverID(i['driverId'])
                check = QtWidgets.QTableWidgetItem()
                check.setCheckState(QtCore.Qt.Unchecked)
                check.setBackground(color)
                if finish_pos is not None:
                    if finish_pos == 1:
                        color = QtGui.QColor(255, 215, 0, 128)
                    elif finish_pos == 2:
                        color = QtGui.QColor(128, 128, 128, 128)
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
                self.tableWidget.setItem(rowcount, 1, item0)
                item1 = QtWidgets.QTableWidgetItem(driver_detail[0]['forename'] + ' ' + driver_detail[0]['surname'])
                item1.setFont(font)
                item1.setBackground(color)
                if finish_pos is None:
                    item1.setForeground(QtGui.QColor(255, 255, 255))
                item1.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(rowcount, 2, item1)
                startpos = QtWidgets.QTableWidgetItem(str(start_pos))
                startpos.setBackground(color)
                startpos.setFont(font)
                if finish_pos is None:
                    startpos.setForeground(QtGui.QColor(255, 255, 255))
                startpos.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(rowcount, 3, startpos)
                if finish_pos is not None:
                    finishpos = QtWidgets.QTableWidgetItem(str(finish_pos))
                else:
                    if finish_status_Id == 2:
                        finishpos = QtWidgets.QTableWidgetItem("DSQ")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif 3 <= finish_status_Id <= 10 or 20 <= finish_status_Id <= 44 or 46 <= finish_status_Id <= 49 or finish_status_Id == 51 \
                            or finish_status_Id == 54 or finish_status_Id == 56 or 59 <= finish_status_Id <= 61 or 63 <= finish_status_Id <= 76 \
                            or 78 <= finish_status_Id <= 80 or 82 <= finish_status_Id <= 87 or finish_status_Id == 89 or 91 <= finish_status_Id <= 95 \
                            or 98 <= finish_status_Id <= 110 or finish_status_Id == 121 or finish_status_Id == 126 or 129 <= finish_status_Id <= 132 \
                            or 135 <= finish_status_Id <= 137:
                        finishpos = QtWidgets.QTableWidgetItem("RET")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 62:
                        finishpos = QtWidgets.QTableWidgetItem("NC")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 77:
                        finishpos = QtWidgets.QTableWidgetItem("107")
                        check.setFlags(
                            QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 81:
                        finishpos = QtWidgets.QTableWidgetItem("DNQ")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 90:
                        finishpos = QtWidgets.QTableWidgetItem("NR")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 96:
                        finishpos = QtWidgets.QTableWidgetItem("EX")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                    elif finish_status_Id == 97:
                        finishpos = QtWidgets.QTableWidgetItem("DNPQ")
                        # check.setFlags(
                        #     QtCore.Qt.ItemIsSelectable)
                finishpos.setFont(font)
                finishpos.setBackground(color)
                if finish_pos is None:
                    finishpos.setForeground(QtGui.QColor(255, 255, 255))
                finishpos.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(rowcount, 4, finishpos)
                pitstops = QtWidgets.QTableWidgetItem(str(pitstop_counts))
                # pitstops.setCheckState(QtCore.Qt.Unchecked)
                pitstops.setFont(font)
                pitstops.setBackground(color)
                pitstops.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if finish_pos is None:
                    pitstops.setForeground(QtGui.QColor(255, 255, 255))
                self.tableWidget.setItem(rowcount, 5, pitstops)
                check = QtWidgets.QTableWidgetItem()
                check.setCheckState(QtCore.Qt.Unchecked)
                check.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                check.setBackground(color)
                self.tableWidget.setItem(rowcount, 0, check)
                rowcount += 1

    def connection(self):
        for i in self.checkbox:
            i.clicked.connect(self.tyreClicked)

    def toggleButton(self):
        if self.radioButton.isChecked():
            self.plot_type = 'QtChart'
            self.chartView.setVisible(True)
            self.canvas.setVisible(False)
            self.chartView_2.setVisible(True)
            self.canvas_2.setVisible(False)
            self.chartView_3.setVisible(True)
            self.canvas_3.setVisible(False)
            self.plotAll()

        elif self.radioButton_2.isChecked():
            self.plot_type = 'matplotlib'
            self.chartView.setVisible(False)
            self.canvas.setVisible(True)
            self.chartView_2.setVisible(False)
            self.canvas_2.setVisible(True)
            self.chartView_3.setVisible(False)
            self.canvas_3.setVisible(True)
            self.plotAll()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(1366, 768)

        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setObjectName("layoutWidget")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)
        self.spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox.sizePolicy().hasHeightForWidth())
        self.spinBox.setSizePolicy(sizePolicy)
        self.spinBox.setMaximumSize(QtCore.QSize(16777215, 30))
        self.spinBox.setObjectName("spinBox")
        self.gridLayout_2.addWidget(self.spinBox, 0, 1, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBox_2.sizePolicy().hasHeightForWidth())
        self.spinBox_2.setSizePolicy(sizePolicy)
        self.spinBox_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout_2.addWidget(self.spinBox_2, 0, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.checkBox.setSizePolicy(sizePolicy)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 1, 1, 1, 1)

        self.radioButton = QtWidgets.QRadioButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.radioButton.setSizePolicy(sizePolicy)
        self.radioButton.setObjectName("radioButton")
        self.gridLayout_2.addWidget(self.radioButton, 1, 2, 1, 1)

        self.radioButton_2 = QtWidgets.QRadioButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.checkBox.sizePolicy().hasHeightForWidth())
        self.radioButton_2.setSizePolicy(sizePolicy)
        self.radioButton_2.setObjectName("radioButton_2")
        self.gridLayout_2.addWidget(self.radioButton_2, 1, 3, 1, 1)

        self.gridLayout.addLayout(self.gridLayout_2, 2, 1, 1, 1)

        self.tabWidget_2 = QtWidgets.QTabWidget(self.layoutWidget)
        self.tabWidget_2.setObjectName("tabWidget_2")

        self.tab_left_1 = QtWidgets.QWidget()
        self.tab_left_1.setObjectName("tab_left_1")
        self.gridLayout_tab_left_1 = QtWidgets.QGridLayout(self.tab_left_1)
        self.gridLayout_tab_left_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tab_left_1.setObjectName("gridLayout_tab_left_1")


        self.tableWidget = QtWidgets.QTableWidget(self.tab_left_1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tabWidget_2.addTab(self.tab_left_1, "")

        self.tab_left_2 = QtWidgets.QWidget()
        self.tab_left_2.setObjectName("tab_left_2")
        self.gridLayout_tab_left_2 = QtWidgets.QGridLayout(self.tab_left_2)
        self.gridLayout_tab_left_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tab_left_2.setObjectName("gridLayout_tab_left_2")
        self.label_left_1 = QtWidgets.QLabel(self.tab_left_2)
        self.label_left_1.setObjectName("label_left_1")
        self.gridLayout_tab_left_2.addWidget(self.label_left_1, 0, 0, 1, 1)
        self.label_left_2 = QtWidgets.QLabel(self.tab_left_2)
        self.label_left_2.setObjectName("label_left_2")
        self.gridLayout_tab_left_2.addWidget(self.label_left_2, 1, 0, 1, 1)
        self.label_left_3 = QtWidgets.QLabel(self.tab_left_2)
        self.label_left_3.setObjectName("label_left_3")
        self.gridLayout_tab_left_2.addWidget(self.label_left_3, 2, 0, 1, 1)
        self.label_left_4 = QtWidgets.QLabel(self.tab_left_2)
        self.label_left_4.setObjectName("label_left_4")
        self.gridLayout_tab_left_2.addWidget(self.label_left_4, 3, 0, 1, 1)
        self.label_left_5 = QtWidgets.QLabel(self.tab_left_2)
        self.label_left_5.setObjectName("label_left_5")
        self.gridLayout_tab_left_2.addWidget(self.label_left_5, 4, 0, 1, 1)

        self.label_right_1 = QtWidgets.QLabel(self.tab_left_2)
        self.label_right_1.setObjectName("label_right_1")
        self.gridLayout_tab_left_2.addWidget(self.label_right_1, 0, 1, 1, 1)
        self.label_right_2 = QtWidgets.QLabel(self.tab_left_2)
        self.label_right_2.setObjectName("label_right_2")
        self.gridLayout_tab_left_2.addWidget(self.label_right_2, 1, 1, 1, 1)
        self.label_right_3 = QtWidgets.QLabel(self.tab_left_2)
        self.label_right_3.setObjectName("label_right_3")
        self.gridLayout_tab_left_2.addWidget(self.label_right_3, 2, 1, 1, 1)
        self.label_right_4 = QtWidgets.QLabel(self.tab_left_2)
        self.label_right_4.setObjectName("label_right_4")
        self.gridLayout_tab_left_2.addWidget(self.label_right_4, 3, 1, 1, 1)
        self.detailedTiming = QtWidgets.QTableWidget(self.tab_left_2)
        self.detailedTiming.setObjectName("detailedTiming")
        self.detailedTiming.setColumnCount(0)
        self.detailedTiming.setRowCount(0)
        self.gridLayout_tab_left_2.addWidget(self.detailedTiming, 4, 1, 1, 1)
        self.tabWidget_2.addTab(self.tab_left_1, "")
        self.tabWidget_2.addTab(self.tab_left_2, "")


        self.gridLayout.addWidget(self.tabWidget_2, 1, 0, 1, 1)

        self.tabWidget = QtWidgets.QTabWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout_tab_left_1.addWidget(self.tableWidget, 0, 0, 1, 1)

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        self.gridLayout_tab_1 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_tab_1.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tab_1.setObjectName("gridLayout_tab_1")

        # if self.plot_type == 'QtChart':
        self.chartView = CustomedQChartView(self.tab)
        self.chartView.setObjectName("chartView")
        self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)
        self.gridLayout_tab_1.addWidget(self.chartView, 0, 0, 1, 1)

        # elif self.plot_type == 'matplotlib':
        self.laptimefig = plt.Figure()
        self.canvas = FC(self.laptimefig)
        self.canvas.setObjectName("canvas")
        self.gridLayout_tab_1.addWidget(self.canvas, 0, 0, 1, 1)

        if self.plot_type == 'QtChart':
            self.chartView.setVisible(True)
            # self.chartView.setMouseTracking(True)
            self.canvas.setVisible(False)
            # self.canvas.setMouseTracking(False)
        else:
            self.chartView.setVisible(False)
            # self.chartView.setMouseTracking(False)
            self.canvas.setVisible(True)
            # self.canvas.setMouseTracking(True)

        self.tableWidget_tab1 = QtWidgets.QTableWidget()
        self.tableWidget_tab1.setSizePolicy(sizePolicy)
        self.tableWidget_tab1.setObjectName("tableWidget_tab1")
        self.tableWidget_tab1.setColumnCount(0)
        self.tableWidget_tab1.setRowCount(0)
        # self.gridLayout_tab_1.addWidget(self.tableWidget_tab1, 0, 1, 1, 1)
        # self.gridLayout_tab_1.setColumnStretch(0, 2)
        # self.gridLayout_tab_1.setColumnStretch(1, 1)

        self.tabWidget.addTab(self.tab, "")

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")

        self.gridLayout_tab_2 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_tab_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tab_2.setObjectName("gridLayout_tab_2")

        # if self.plot_type == 'QtChart':
        self.chartView_2 = CustomedQChartView(self.tab_2)
        self.chartView_2.setObjectName("chartView_2")
        self.chartView_2.setRenderHint(QtGui.QPainter.Antialiasing)
        self.gridLayout_tab_2.addWidget(self.chartView_2, 0, 0, 1, 1)

        # elif self.plot_type == 'matplotlib':
        self.speedgapfig = plt.Figure()
        self.canvas_2 = FC(self.speedgapfig)
        self.canvas_2.setObjectName("canvas_2")
        self.gridLayout_tab_2.addWidget(self.canvas_2, 0, 0, 1, 1)

        if self.plot_type == 'QtChart':
            self.chartView_2.setVisible(True)
            self.canvas_2.setVisible(False)
        else:
            self.chartView_2.setVisible(False)
            self.canvas_2.setVisible(True)

        self.tableWidget_tab2 = QtWidgets.QTableWidget()
        self.tableWidget_tab2.setSizePolicy(sizePolicy)
        self.tableWidget_tab2.setObjectName("tableWidget_tab2")
        self.tableWidget_tab2.setColumnCount(0)
        self.tableWidget_tab2.setRowCount(0)
        # self.gridLayout_tab_2.addWidget(self.tableWidget_tab2, 0, 1, 1, 1)
        # self.gridLayout_tab_2.setColumnStretch(0, 2)
        # self.gridLayout_tab_2.setColumnStretch(1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")

        self.gridLayout_tab_3 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_tab_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_tab_3.setObjectName("gridLayout_tab_3")

        self.chartView_3 = CustomedQChartView(self.tab_3)
        self.chartView_3.setObjectName("chartView_3")
        self.chartView_3.setRenderHint(QtGui.QPainter.Antialiasing)
        self.gridLayout_tab_3.addWidget(self.chartView_3, 0, 0, 1, 1)

        # elif self.plot_type == 'matplotlib':
        self.spacegapfig = plt.Figure()
        self.canvas_3 = FC(self.spacegapfig)
        self.canvas_3.setObjectName("canvas_3")
        self.gridLayout_tab_3.addWidget(self.canvas_3, 0, 0, 1, 1)

        if self.plot_type == 'QtChart':
            self.chartView_3.setVisible(True)
            self.canvas_3.setVisible(False)
        else:
            self.chartView_3.setVisible(False)
            self.canvas_3.setVisible(True)

        self.tableWidget_tab3 = QtWidgets.QTableWidget()
        self.tableWidget_tab3.setSizePolicy(sizePolicy)
        self.tableWidget_tab3.setObjectName("tableWidget_tab1")
        self.tableWidget_tab3.setColumnCount(0)
        self.tableWidget_tab3.setRowCount(0)
        # self.gridLayout_tab_3.addWidget(self.tableWidget_tab3, 0, 1, 1, 1)
        # self.gridLayout_tab_3.setColumnStretch(0, 2)
        # self.gridLayout_tab_3.setColumnStretch(1, 1)

        self.tabWidget.addTab(self.tab_3, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.comboBox = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox.sizePolicy().hasHeightForWidth())
        self.comboBox.setSizePolicy(sizePolicy)
        self.comboBox.setMaximumSize(QtCore.QSize(16777215, 40))
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.comboBox_2 = QtWidgets.QComboBox(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_2.sizePolicy().hasHeightForWidth())
        self.comboBox_2.setSizePolicy(sizePolicy)
        self.comboBox_2.setMaximumSize(QtCore.QSize(16777215, 40))
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout.addWidget(self.comboBox_2)
        self.pushButton = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setMaximumSize(QtCore.QSize(16777215, 40))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_5 = QtWidgets.QLabel(self.layoutWidget)
        self.label_5.setObjectName("label_5")
        self.gridLayout_4.addWidget(self.label_5, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)
        self.checkBox_2 = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_2.setMaximumSize(QtCore.QSize(16777215, 30))
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout_4.addWidget(self.checkBox_2, 0, 1, 1, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_4)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)

        self.initialize()
        self.comboBox.currentIndexChanged.connect(self.getRacesInThisYear)
        self.comboBox.currentIndexChanged.connect(self.unlockPushbutton)
        self.comboBox_2.currentIndexChanged.connect(self.unlockPushbutton)
        self.pushButton.clicked.connect(self.getDriversInThisRace)
        self.tableWidget.clicked.connect(self.showPos)

        self.checkBox.clicked.connect(self.hidePitChecked)
        self.checkBox_2.clicked.connect(self.checkAll)
        self.radioButton.toggled.connect(self.toggleButton)
        self.radioButton_2.toggled.connect(self.toggleButton)
        self.spinBox.setEnabled(False)
        self.spinBox.setEnabled(False)
        self.spinBox_2.setEnabled(False)
        self.pushButton.click()
        self.spinBox.valueChanged.connect(self.changeStartLap)
        self.spinBox_2.valueChanged.connect(self.changeEndLap)
        self.radioButton.setChecked(True)
        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "F1 Analyz v0.8.0 dev3"))
        self.label.setText(_translate("Dialog", "Ready."))
        self.label_2.setText(_translate("Dialog", "StartLap:"))
        self.label_3.setText(_translate("Dialog", "FinishLap:"))
        self.label_4.setText(_translate("Dialog", "PitEntry/Exit"))
        self.label_5.setText(_translate("Dialog", ""))
        self.checkBox.setText(_translate("Dialog", "Hide"))
        self.checkBox_2.setText(_translate("Dialog", "Check All"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Lap Time"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Speed Gap"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Car Gap"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_left_1), _translate("Dialog", "Result"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_left_2), _translate("Dialog", "Analyz"))
        self.pushButton.setText(_translate("Dialog", "Go"))
        self.radioButton.setText(_translate("Dialog", "QtChart"))
        self.radioButton_2.setText(_translate("Dialog", "Matplotlib"))
        self.label_left_1.setText(_translate("Dialog", ""))
        self.label_left_2.setText(_translate("Dialog", ""))
        self.label_left_3.setText(_translate("Dialog", ""))
        self.label_left_4.setText(_translate("Dialog", ""))
        self.label_left_5.setText(_translate("Dialog", ""))



if __name__ == "__main__":
    import sys

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_Dialog(plot_type='QtChart')
    ui.setupUi()
    ui.show()
    sys.exit(app.exec_())
