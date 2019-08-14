# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Dialog1.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from database_connector import f1db
import bitarray
import matplotlib.pyplot as plt
import time
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FC



class Ui_Dialog(object):

    def __init__(self):
        self.db = f1db()
        self.checkbox  = []
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




    def initData(self):
        self.plot_list = []
        self.pitdata = {}
        self.pitlaps = {}
        self.laptime = {}
        self.acctime = {}
        self.name = {}

    def initialize(self):
        self.hide_pit_eelap = False
        max_year = 0
        for i in self.years_recorded_in_lap_times:
            if i['year']>max_year:
                max_year = i['year']
            self.comboBox.addItem(str(i['year']))
        self.comboBox.setCurrentText(str(max_year))
        year = max_year
        races = self.db.getRacesInAYearRecordedInLaptimes(year)
        for i in races:
            self.comboBox_2.addItem(i['name'])
        latest_race = self.db.getLatestRaceThisYear(year)
        self.comboBox_2.setCurrentText(self.db.getRaceNameByRaceId(latest_race[0]['max(raceId)'])[0]['name'])


    def plotAll(self):
        print('-'*20)
        t0 = time.time()
        self.plotTimeGraph()
        print('Time Graph:',time.time()-t0)
        t1 = time.time()
        self.plotSpaceGapGraph()
        print('Space Graph:',time.time()-t1)
        t2 = time.time()
        self.plotGapGraph()
        print('Time Gap Graph:',time.time()-t2)
        print('Total:',time.time()-t0)
        # pass

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
            self.SpinBox.setMinimum(1)
            # print(self.db.getMaximumLap(raceId[0]['raceId']))
            self.SpinBox.setMaximum(self.max_lap)
            self.SpinBox.setSingleStep(1)
            self.SpinBox_2.setMinimum(1)
            self.SpinBox_2.setMaximum(self.max_lap)
            self.SpinBox_2.setSingleStep(1)
            self.SpinBox_2.setValue(self.max_lap)
            self.SpinBox_2.setEnabled(True)
            self.SpinBox.setEnabled(True)
        else:
            self.SpinBox_2.setEnabled(False)
            self.SpinBox.setEnabled(False)

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
                                pitlaps.append(i['lap']+1)
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
                self.laptimefig.legend(legends,loc=1)
                self.laptimefig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                        bottom=0.13, top=0.91)
                ax.set_xlabel('laps')
                ax.set_ylabel('Laptime: ms',labelpad = 0.5)
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
                        self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'], self.raceId, a[i])
                    else:
                        self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'], self.raceId, a[i])
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
                self.laptimefig.legend(prop={'size':6})
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
                        if timing_pools[i][k]['lap'] >= self.min_cal_lap and timing_pools[i][k]['lap'] <= self.max_cal_lap and timing_pools[j][k]['lap'] >= self.min_cal_lap and timing_pools[j][k]['lap'] <= self.max_cal_lap:
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
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],self.raceId, a[i])
                else:
                    self.acctime[i] = self.db.getLaptimesAccumViaDriverIDRaceIDStints(self.drivers[i]['driverId'],self.raceId, a[i])
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
            self.spacegapfig.legend(prop={'size':6},ncol=4,loc=1)
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
                for j in range(i+1, len(timing_pools)):
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
                        if timing_pools[i][k]['lap'] >= self.min_cal_lap and timing_pools[i][k]['lap'] <= self.max_cal_lap and timing_pools[j][k]['lap'] >= self.min_cal_lap and timing_pools[j][k]['lap'] <= self.max_cal_lap:
                            try:
                                if timing_pools[i][k]['lap'] not in pitlaps and timing_pools[j][k]['lap'] not in pitlaps:
                                    time0 = self.mssmmm2ms(timing_pools[i][k]['time'])
                                    time1 = self.mssmmm2ms(timing_pools[j][k]['time'])
                                    delta_time = time0-time1
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
                    legends.append(name0+' and '+name1)
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
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'], self.raceId, a[i])
                else:
                    self.laptime[i] = self.db.getLaptimesViaDriverIDRaceIDStints(self.drivers[i]['driverId'], self.raceId, a[i])
                if i not in self.name.keys():
                    self.name[i] = self.db.getDriversByDriverID(self.drivers[i]['driverId'])[0]['surname']

            # plot_pool_x = []
            # plot_pool_y = []
            for i in a.keys():
                for j in a.keys():
                    plot_pool_x = []
                    plot_pool_y = []
                    if i>j:
                        for lap in range(self.min_cal_lap,self.max_cal_lap+1):
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
            self.speedgapfig.legend(prop={'size':6},ncol=4)
            self.speedgapfig.subplots_adjust(left=0.18, wspace=0.25, hspace=0.25,
                                             bottom=0.13, top=0.91)
            ax.set_xlabel('laps')
            ax.set_ylabel('Speed Difference: ms', labelpad=0.5)
            self.speedgapfig.legend(legends, loc=1)
            self.canvas_2.draw()  #

    def changeStartLap(self):
        cur_lap = self.SpinBox.value()
        self.SpinBox_2.setMinimum(cur_lap)
        self.min_cal_lap = cur_lap
        self.plotAll()

    def changeEndLap(self):
        self.max_cal_lap = self.SpinBox_2.value()
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
            self.tableWidget.setHorizontalHeaderLabels(['Code', 'Name', 'Grid', 'End', 'Pits','Tyre'])
            self.tableWidget.setRowCount(len(drivers))
            rowcount = 0
            # self.pitstops = self.db.getPitstopsByRaceId(raceId)

            for num in range(len(drivers)):
                i = drivers[num]
                # table_color = QtGui.QPalette()
                # table_color.setColor(QtGui.QPalette.Base, QtGui.QColor(0,0,0))
                pitstops = self.db.getPitstopByRaceIdDriverId(raceId,i['driverId'])
                pitstop_counts = len(pitstops)
                font = QtGui.QFont()
                color = QtGui.QColor(192, 192, 192,128)
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
                            or 78 <= finish_status_Id <= 80 or 82 <= finish_status_Id <= 87 or finish_status_Id == 89 or 91 <= finish_status_Id <= 95\
                            or 98 <= finish_status_Id <= 110 or finish_status_Id == 121 or finish_status_Id == 126 or 129 <= finish_status_Id <= 132\
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
                    label_stint.setPixmap(self.tyre_img[i['tyreName']].scaled(list_height,list_height))
                    label_stint.setAutoFillBackground(True)
                    laps_stint = QtWidgets.QLabel()
                    laps_stint.setFixedWidth(18)
                    laps_stint.setText(str(i['laps']))
                    stint_1 = QtWidgets.QCheckBox()
                    stint_1.setFixedWidth(30)
                    # stint_1.setFixedHeight(list_height)
                    stint_1.setCheckState(QtCore.Qt.Unchecked)
                    stint_1.setObjectName(str(rowcount)+'-'+str(5)+'-'+str(check_count))
                    self.checkbox.append(stint_1)
                    # print(self.checkbox)
                    check_count += 1
                    check_color = QtGui.QPalette()
                    check_color.setColor(QtGui.QPalette.Base,QtGui.QColor(255,255,255))
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
            self.tableWidget.setHorizontalHeaderLabels(['Checked','Code', 'Name', 'Grid', 'End', 'Pits'])
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

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1366, 768)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(1024, 768))
        Dialog.setMaximumSize(QtCore.QSize(3840, 2160))
        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 1061, 631))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(Dialog)

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
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.SpinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.SpinBox.setObjectName("SpinBox")
        self.horizontalLayout_2.addWidget(self.SpinBox)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.SpinBox_2 = QtWidgets.QSpinBox(self.layoutWidget)
        self.SpinBox_2.setObjectName("SpinBox_2")
        self.horizontalLayout_2.addWidget(self.SpinBox_2)
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.layoutWidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 511, 541))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.laptimefig = plt.Figure()
        self.canvas = FC(self.laptimefig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas.sizePolicy().hasHeightForWidth())
        self.canvas.setSizePolicy(sizePolicy)
        self.canvas.setObjectName("canvas")
        self.gridLayout_2.addWidget(self.canvas, 2, 1, 1, 1)

        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.tab_2)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(10, 10, 511, 541))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.speedgapfig = plt.Figure()
        self.canvas_2 = FC(self.speedgapfig)
        self.canvas_2.setObjectName("canvas_2")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas_2.sizePolicy().hasHeightForWidth())
        self.canvas_2.setSizePolicy(sizePolicy)
        self.gridLayout_3.addWidget(self.canvas_2, 2, 1, 1, 1)

        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.tab_3)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(10, 10, 511, 541))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_4.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")

        self.spacegapfig = plt.Figure()
        self.canvas_3 = FC(self.spacegapfig)
        self.canvas_3.setObjectName("canvas_3")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.canvas_3.sizePolicy().hasHeightForWidth())
        self.canvas_3.setSizePolicy(sizePolicy)
        self.gridLayout_4.addWidget(self.canvas_3, 2, 1, 1, 1)

        self.gridLayout.addWidget(self.tabWidget, 1, 1, 1, 1)
        # Dialog.setCentralWidget(self.centralwidget)
        # self.statusbar = QtWidgets.QStatusBar(Dialog)
        # self.statusbar.setObjectName("statusbar")
        # Dialog.setStatusBar(self.statusbar)
        
        self.initialize()
        self.comboBox.currentIndexChanged.connect(self.getRacesInThisYear)
        self.comboBox.currentIndexChanged.connect(self.unlockPushbutton)
        self.comboBox_2.currentIndexChanged.connect(self.unlockPushbutton)
        self.pushButton.clicked.connect(self.getDriversInThisRace)
        self.tableWidget.clicked.connect(self.showPos)


        self.checkBox.clicked.connect(self.hidePitChecked)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.SpinBox.setEnabled(False)
        self.SpinBox_2.setEnabled(False)
        self.pushButton.click()
        self.SpinBox.valueChanged.connect(self.changeStartLap)
        self.SpinBox_2.valueChanged.connect(self.changeEndLap)
        # self.connection()

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "F1 Analyz v0.6.5"))
        self.pushButton.setText(_translate("Dialog", "Search"))
        self.label.setText(_translate("Dialog", "Lap Start"))
        self.label_2.setText(_translate("Dialog", "Lap End"))
        self.checkBox.setText(_translate("Dialog", "Hide pit entry/exit lap"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Lap Time"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Dialog", "Speed Gap"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Dialog", "Car Gap"))

class CommonHelper:
    def __init__(self):
        pass

    @staticmethod
    def readQss(style):
        with open(style, 'r') as f:
            return f.read()

if __name__ == "__main__":
    import sys
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    # qssStyle = CommonHelper.readQss('/home/arc/Downloads/QSS-master/AMOLED.qss')
    # Dialog.setStyleSheet(qssStyle)
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
