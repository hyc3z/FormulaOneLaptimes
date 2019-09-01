import os
import sys
import subprocess
import time


def testRunnable(filename,time_length):
    dir = os.path.join(os.getcwd(),'',filename)
    try:
        process = subprocess.Popen(['python3', dir], stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        time.sleep(time_length)
        process.kill()
    except Exception as e:
        print(e)


def testdb():
    pass


def test():
    testRunnable('gui.py',5)


if __name__ == '__main__':
    test()