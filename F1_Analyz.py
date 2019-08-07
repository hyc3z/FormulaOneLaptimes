import pymysql
import os
import time
# import
import subprocess
import sys
"""
return -1: Network error, Can't update db.
return 2: File is missing
return 3: File is corrupted
return 4: File not exist or unexpected end of file
"""


def duplicate_renamer(filename):
    duplicate_name = 0
    if os.path.exists(filename):
        duplicate_name += 1
        while os.path.exists(filename + '.' + str(duplicate_name)):
            duplicate_name += 1
    if not duplicate_name:
        return filename
    else:
        return filename + '.' + str(duplicate_name)


def duplicate_latest(filename):
    duplicate_name = 0
    if os.path.exists(filename):
        duplicate_name += 1
        while os.path.exists(filename + '.' + str(duplicate_name)):
            duplicate_name += 1
    if not duplicate_name:
        return None
    else:
        if duplicate_name == 1:
            return filename
        else:
            return filename + '.' + str(duplicate_name-1)


def download_db(filename,retry_count=3):
    file_name = duplicate_renamer(filename)
    ret = 1
    error_count = 0
    while ret and error_count < retry_count:
        ret = os.system('wget http://ergast.com/downloads/' + file_name)
        if ret:
            error_count += 1
            print('Network Error.Retrying...', error_count)
    if error_count == retry_count:
        return -1
    if not os.path.exists(file_name):
        return 2
    return 0


def updatedb(download=True,retry_count=3,filename='f1db.sql.gz'):
    if download:
        returncode = download_db(retry_count=retry_count,filename=filename)
        if returncode != 0:
            return returncode
    file_name = duplicate_latest(filename)
    sql_name = duplicate_renamer('f1db.sql')
    ret = os.system('gunzip -c '+file_name+' > '+sql_name)
    print(ret)
    if ret != 0:
        if ret == 256:
            return 4
        if ret == 512:
            return 3

class f1db:

    def __init__(self, host='localhost', port=3306, db='f1', user='root', passwd='aqwe6kj3', charset='utf8'):
        # 建立连接
        self.passwd = passwd
        self.host = host
        self.port = port
        self.db = db
        self.user = user
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset=charset)
        # 创建游标，操作设置为字典类型
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
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

    def execute(self,sql):
        start_time = time.time()
        try:
            os.system('mysql -u '+self.user+' --password='+self.passwd +' '+self.db+ " < "+sql)
        except:
            print('Error')
        print('Done.',(time.time()-start_time)*1000,'ms')

    def searchRaceID(self,year,round):
        self.cur.execute('SELECT * from races where year='+str(year)+' and round='+str(round))
        return self.cur.fetchall()

    def getLapTimes(self,raceID,savedir):
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

    def getLaptimesALL(self,save_dir):
        self.cur.execute('SELECT raceId from lapTimes where lap=1 and position=1 order by raceId asc')
        raceIds = self.cur.fetchall()
        for i in raceIds:
            self.getLapTimes(i['raceId'],savedir=save_dir)



if __name__ == '__main__':
    db = f1db()
    # db.getLapTimes(90, 'Laptimes')
    db.getLaptimesALL(os.path.join(os.getcwd(),'Laptimes'))

