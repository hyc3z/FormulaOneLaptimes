import pymysql
import os
import time
import sqlite3
# import
import subprocess
import sys
"""
return -1: Network error, Can't update db.
return 2: File is missing
return 3: File is corrupted
return 4: File not exist or unexpected end of file
"""



class f1db:

    def dict_factory(self, cursor, row):
        d = {}
        for index, col in enumerate(cursor.description):
            d[col[0]] = row[index]
        return d

    def __init__(self,dbtype='sqlite3', host='localhost', port=3306, db='f1', user='root', passwd='aqwe6kj3', charset='utf8'):
        # 建立连接
        if dbtype == 'mysql':
            self.passwd = passwd
            self.host = host
            self.port = port
            self.db = db
            self.user = user
            self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
            # 创建游标，操作设置为字典类型
            self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        elif dbtype == 'sqlite3':
            self.conn = sqlite3.connect(os.path.join(os.getcwd(), 'f1.db'))
            self.conn.row_factory = self.dict_factory
            self.cur = self.conn.cursor()
        # self.init_all_data()

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()

    def query(self,sql):
        start_time = time.time()
        try:
            start_time = time.time()
            self.cur.execute(sql)
            print('Data obtained.', (time.time() - start_time) * 1000, 'ms')
            return self.cur.fetchall()
        except pymysql.err.ProgrammingError:
            print('Data not exist.')
            return None

    def init_all_data(self):
        self.circuits = self.query('SELECT * from circuits')
        self.constructorResults = self.query('SELECT * from constructorResults')
        self.constructors = self.query('SELECT * from constructors')
        self.constructorStandings = self.query('SELECT * from constructorStandings')
        self.drivers = self.query('SELECT * from drivers')
        self.driverStandings = self.query('SELECT * from driverStandings')
        self.lapTimes = self.query('SELECT * from lapTimes')
        self.pitStops = self.query('SELECT * from pitStops')
        self.qualifying = self.query('SELECT * from qualifying')
        self.races = self.query('SELECT * from races')
        self.results = self.query('SELECT * from results')
        self.seasons = self.query('SELECT * from seasons')
        self.status = self.query('SELECT * from status')

    def createStints(self):
        self.cur.execute('DROP table if exists stints')
        self.cur.execute('create table stints(driverId int, driverNum int, raceId int,lap_on int, stint int,laps int, tyre int)')
        for i in range(1010, 1022):
            # print(i)
            drivers = self.getDriversByRaceID(i)
            for k in drivers:
                self.cur.execute('insert into stints(driverId, driverNum, raceId, lap_on, stint) values('+str(k['driverId'])+','+str(k['number'])+','+str(i)+','+str(1)+','+str(1)+')')
            data = self.getPitstopsByRaceId(i)
            for j in data:
                driverid = j['driverId']
                num = self.getDriverNumByDriverId(driverid)
                if num is not None:
                    num = num[0]['number']
                lap_on = j['lap']
                stint = j['stop']+1
                # print('insert into stints(driverId, raceId, lap_on, stint) values('+str(driverid)+','+str(i)+','+str(lap_on)+','+str(stint)+')')
                self.cur.execute('insert into stints(driverId, driverNum, raceId, lap_on, stint) values('+str(driverid)+','+str(num)+','+str(i)+','+str(lap_on)+','+str(stint)+')')

        self.conn.commit()

    def execute(self,sql):
        start_time = time.time()
        try:
            os.system('mysql -u '+self.user+' --password='+self.passwd +' '+self.db+ " < "+sql)
        except:
            print('Error')
        print('Done.',(time.time()-start_time)*1000,'ms')

    def getPitstopsByRaceId(self,raceId):
        self.cur.execute('select * from pitStops where raceId='+str(raceId))
        return self.cur.fetchall()

    def getDriverNumByDriverId(self, driverId):
        self.cur.execute('select number from drivers where driverId='+str(driverId))
        return self.cur.fetchall()

    def getPitstopByRaceIdDriverId(self, raceId, driverId):
        self.cur.execute('select stop,lap from pitStops where raceId='+str(raceId)+' and driverId='+str(driverId))
        return self.cur.fetchall()

    def getAllYearsRecordedInLaptimes(self):
        self.cur.execute('select year from races where raceId in (SELECT raceId from lapTimes where lap=1 and position=1 order by raceId asc) group by year order by year asc')
        return self.cur.fetchall()

    def getAllRaceNameRecordedInLaptimes(self):
        self.cur.execute('select name from races where raceId in (SELECT raceId from lapTimes where lap=1 and position=1) group by name order by name asc')
        return self.cur.fetchall()

    def getRacesInAYearRecordedInLaptimes(self,year):
        self.cur.execute('select name from races where year='+str(year)+' order by name asc')
        return self.cur.fetchall()

    # This is truly beautiful, isn't it
    def getLaptimesAccumViaRaceIdDriverId(self,raceId,driverId):
        self.cur.execute('select driverId,raceId,lap, (select sum(milliseconds) from lapTimes where lap<=tt.lap and raceId = tt.raceId and driverId = tt.driverId) as timeElapsed from lapTimes as tt where driverId='+str(driverId)+' and raceId='+str(raceId))
        return self.cur.fetchall()

    def getLatestRaceThisYear(self,year):
        self.cur.execute('select max(raceId) from races where year='+str(year)+' and raceId in (select raceId from lapTimes)')
        return self.cur.fetchall()

    def getRaceNameByRaceId(self,raceId):
        self.cur.execute('select name from races where raceId='+str(raceId))
        return self.cur.fetchall()

    def getRaceIDByYearName(self,year,name):
        self.cur.execute('SELECT * from races where year='+str(year)+' and name="'+name+'"')
        return self.cur.fetchall()

    def getRaceIDByYearRound(self,year,round):
        self.cur.execute('SELECT * from races where year='+str(year)+' and round='+str(round))
        return self.cur.fetchall()

    def getDriversByDriverID(self,DriverId):
        self.cur.execute('select code,forename,surname,driverId from drivers where driverId='+str(DriverId))
        return self.cur.fetchall()

    def getDriversByRaceID(self,RaceID):
        self.cur.execute('select code,forename,surname,driverId,number from drivers where driverId in (SELECT driverId from lapTimes where lap=1 and raceId='+str(RaceID)+') order by forename asc')
        return self.cur.fetchall()

    def getGridByRaceID(self,raceID):
        self.cur.execute('select driverId from results where raceId='+str(raceID)+' order by position is null,position asc')
        return self.cur.fetchall()

    def getStartposByRaceIDDriverID(self,raceID,driverID):
        self.cur.execute('select position from qualifying where raceId='+str(raceID)+' and driverId='+str(driverID))
        return  self.cur.fetchall()

    # def getResultStandingByRaceID(self,raceID):
    #     self.cur.execute('select code,forename,surname from drivers where driverId in (select driverId from results where raceId='+str(raceID)+' and driverId in (SELECT driverId from lapTimes where lap=1 and raceId='+str(raceID)+') order by position asc)')
    #     return self.cur.fetchall()

    def getFinishStatusNameByStatusID(self,statusId):
        self.cur.execute('select status from status where statusId='+str(statusId))
        return self.cur.fetchall()



    def getResultStatusIDByRaceIDandDriverID(self,raceID, driverId):
        # self.cur.execute('select status from status where statusId in (select statusId from results where raceId='+str(raceID)+' order by position asc)')
        self.cur.execute('select statusId from results where raceId='+str(raceID)+' and driverId='+str(driverId)+' order by position asc')
        return self.cur.fetchall()

    def getResultStandingByRaceIDandDriverId(self,raceID, driverId):
        # self.cur.execute('select status from status where statusId in (select statusId from results where raceId='+str(raceID)+' order by position asc)')
        self.cur.execute('select position from results where raceId='+str(raceID)+' and driverId='+str(driverId))
        return self.cur.fetchall()

    def getDriverIdViaName(self, forename, surname):
        self.cur.execute('select driverId from drivers where forename="'+forename+'" and surname="'+surname+'"')
        return self.cur.fetchall()

    def getLaptimesViaDriverIDRaceID(self, driverId, raceId):
        self.cur.execute('select time,lap from lapTimes where raceId='+str(raceId)+' and driverId='+str(driverId))
        return self.cur.fetchall()

    def getMaximumLap(self,raceId):
        self.cur.execute('SELECT max(lap) from lapTimes where raceId='+str(raceId))
        return self.cur.fetchall()

    def saveLapTimesCsv(self,raceID,savedir):
        csv = 'Driver'
        self.cur.execute('SELECT max(lap) from lapTimes where raceId='+str(raceID))
        lapcount = self.cur.fetchall()[0]['max(lap)']
        for i in range(1,lapcount+1):
            csv += ','
            csv += str(i)
        csv += '\n'
        self.cur.execute('SELECT driverId from lapTimes where raceId=' + str(raceID) + ' and lap=1 order by driverId desc')
        driver_ids = self.cur.fetchall()
        driver_names_matchup = {}
        for item in driver_ids:
            self.cur.execute('SELECT * from drivers where driverId='+str(item['driverId']))
            result = self.cur.fetchall()
            if result[0]['code'] is not None:
                driver_names_matchup[item['driverId']] = result[0]['forename']+' '+result[0]['surname']+' ('+result[0]['code']+')'
            else:
                driver_names_matchup[item['driverId']] = result[0]['forename']+' '+result[0]['surname']

        for i in driver_names_matchup:
            self.cur.execute('SELECT time from lapTimes where raceId='+str(raceID)+' and driverId='+str(i)+' order by lap asc')
            line_raw = self.cur.fetchall()
            line = driver_names_matchup[i]
            for i in line_raw:
                line += ','
                line += i['time']
            line += '\n'
            csv += line

        self.cur.execute('SELECT year,name from races where raceId='+str(raceID))
        filename_raw = self.cur.fetchall()
        filename = str(filename_raw[0]['year'])+' '+str(filename_raw[0]['name'])+'.csv'
        try:
            f = open(os.path.join(savedir,str(filename_raw[0]['year']),filename),'w+')
        except FileNotFoundError:
            os.system('mkdir '+os.path.join(savedir,str(filename_raw[0]['year'])))
            f = open(os.path.join(savedir,str(filename_raw[0]['year']),filename),'w+')
        f.write(csv)
        print(os.path.join(savedir,str(filename_raw[0]['year']),filename),'Done')

    def saveLaptimesCsvALL(self,save_dir):
        self.cur.execute('SELECT raceId from lapTimes where lap=1 and position=1 order by raceId asc')
        raceIds = self.cur.fetchall()
        for i in raceIds:
            self.saveLapTimes(i['raceId'],savedir=save_dir)



if __name__ == '__main__':
    db = f1db()
    # db.getLapTimes(90, 'Laptimes')
    # print(db.getResultStandingByRaceIDandDriverId(1021,1))
    # db.createStints()

