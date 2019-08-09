import os


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


if __name__ == '__main__':
    updatedb()
