# F1_Analyz

Wheel-to-wheel battles, pitstops, pushing the car to the limit every single milisecond.


This project is made with the purpose of analyzing F1 laptimes, provides multiple ways of plotting and showing the laptime difference.

Data of the project is provided by [ Chris Newell](https://github.com/jcnewell)'s [ergast-f1-api](https://github.com/jcnewell/ergast-f1-api),
the website is [	https://ergast.com](	https://ergast.com). A big thanks to Chris for the tremendous work, so that precious data of F1 can be utilized.

The data contains multiple tables all in a MySQL db, and will be updated after each race. Currently the database the project is using contains data from F1 2019 Hungarian Grand Prix.

Requirements

`$ pip3 install pyqt5 requests matplotlib bitarray`

You may set up a native MySQL environment, and create the needed database via the .sql file provided by ergast.com , but since it is no easy job, I've used the [mysql2sqlite](https://github.com/dumblob/mysql2sqlite) to generate a sqlite db, and you may download the db that comes with 0.2.1 version
[here](https://github.com/Hycdog/F1_Analyz/releases/download/0.2.1/f1.db).

Currently some data in 1996 is not available.

After installing the requirements, and having a f1.db file under project directory, you may run

`$ python3 gui.py`
   
to start the software.

Current version: 0.2.1 

The project is in a very early stage, and a lot of features and algorithms are needed. Please join in the project if you're also a F1 lover, and just want to dig a little deeper. We need your help!

![Image text](https://github.com/Hycdog/img_folder/blob/master/Screenshot%20from%202019-08-10%2001-38-34.png)

 