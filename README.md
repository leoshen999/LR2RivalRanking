# LR2 Rival Ranking

## Pre-built Executable
Latest released executable version:  ```v1.4.3```.  
The download link is [__>> HERE <<__](https://github.com/leoshen999/LR2RivalRanking/releases/download/v1.4.3/LR2RivalRanking.v1.4.3.zip).

It's built and tested on Windows 7 SP1 64bits with Python 2.7.  

## Overview
LR2 Rival Ranking(LR2RR) is a plug-in of Lunatic Rave 2(LR2).

When LR2RR is running, the ranking in LR2 will be replaced.  
The new ranking will only show the score of your rivals and yourself.  
It's easier to compare the scores with your rivals.

Now we have a new feature about homepage modifcation of LR2 after v1.4.  
You can see your scores among difficulty tables and compare with your rivals.

## Installation
The following tools or packages are needed to compile the python script:
* Python 2.7
* PyQt4
* lxml
* win32api
* py2exe

After installing all of above, just simply run:
```python
python LR2RivalRanking.py
```

Or if you want to build a portable executable, please run:
```python
python Setup.py
```
A single executable file ```LR2RivalRanking.exe``` will be located in the generated ```dist\``` folder.

The program is only tested on Windows 7 and 8.  
I'm not sure whether other platforms are well-supported or not.

## Usage
run ```LR2RivalRanking.py``` or ```LR2RivalRanking.exe``` with administrator privilege *before* LR2.

If LR2 has been started before LR2RRR, please close LR2 first.  
(LR2RR needs to take the login procedure of LR2 to get the rival list of current player.)

Special function keys: **F1** - **F5**  
For more detail, the usage guide will be shown when the app starts.

If the webpage modification function doesn't work properly, please refresh your webpage.  
If it's still not work, please check the browser DNS settings.

The rival data is saved in ```%APPDATA%\LR2RR```.  
You can delete this folder if you want to clean the previous saved data.

If the program is not closed correctly, it may cause connection error to LR2IR.  
When the problem happens, just turn on LR2RR and close it again.  
If it's still not solved, please check your hosts setting.  
(```%SystemRoot%\System32\drivers\etc\hosts```)

The rivals can be registered on the LR2IR website:  
http://www.dream-pro.info/~lavalse/LR2IR/search.cgi

## History
Please refer to ```CHANGELOG``` for more information.

## TODO
* In near future (v1.4.x):
  * Consider to use another table sorting library
  * Add webpage exception handler
  * CSS design or more extended functions
  * Add score comparison with arbitrary two players
* should be done someday (v1.5 or farther):
  * Add user configurations
  * Support manually logging
  * Add more exception handler
  * Separate database lock and console lock
  * Unlock multiple access to database
* not sure whether to implement:
  * Remove not played record in ranking
  * Add rival recommended song list

## Credits
Author: Leo Shen (LR2IR: [121168 うまい焼鴨](http://www.dream-pro.info/~lavalse/LR2IR/search.cgi?mode=mypage&playerid=121168))

Part of the code is copied from GNQG's lr2irproxy.  
(https://github.com/GNQG/lr2irproxy)   
The basis code and the main idea help me a lot.

Some css design of webpage extension difficulty table is referred to XYZ's BMS clear lamp.  
(http://xyzzz.net/bms/clearlamp.php)  
Sorry about that I can't read Korean, but the layout of clear lamp manager is beautiful!

The font in the program is from Salauyou's Consolas High Line.  
(https://github.com/Salauyou/Consolas-High-Line)  
The font is awesome on aligning the text heights of different fonts!

The icon of the cloud is from Vecteezy's Cloud Computing.  
(http://www.vecteezy.com/)  
Thanks for the great art works.

## License
MIT License   
Copyright (c) 2016 leoshen999