#Created in Python 3.3.0
#Created by Marc2540

from time import time
from time import sleep
from os.path import isfile
#time.time() gets time since the epoch
#time.sleep() will pause for 'x' seconds

oneWeekInSeconds = 604800 #change if you want to change run frequency


#checks if config.txt exists. Creates it if it doesn't exist.
try:
    with open('config.txt') as f: pass
except:
    print ('Config file doesn\'t exist. Creating it.')
    f = open('config.txt','a')
    f.close()
configFile_Read= open("config.txt", "r") #defines the config file, and opens in 'read' mode.
configFile_Write= open("config.txt", "r+") #opens it in 'read'+'write' mode

lastRunTime=0

def fts_lrt():
    """
    fts_lrt = Find time since last runtime
    Import the last run time from settings file
    """
    for line in configFile_Read:
        if "lastRunTime" in line:
            return lastRunTime
    print (lastRunTime) #debugging


#this function is done (I think)
def SinceLastRun():
    """
    Finds out how much time has passed since last run and,
    if one week has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    fts_lrt()
    if time() >= (lastRunTime + oneWeekInSeconds):
        return goAhead()
    else:
        print ('According to config.txt, it hasn\'t been 1 week since last run.')
        sleep(2)
        goAheadAnyway = input ('Want to continue anyway? (Y/N) ')
        if goAheadAnyway.upper() == 'Y':
            return goAhead()
        elif goAheadAnyway.upper() == 'N':
            print ('Aborted.')
        else:
            return SinceLastRun()


def goAhead():
    print('Not done')


def write_time_to_config_file():
    """Writes the current time to the config file and tells the user that the program is done"""
    configFile_Write.write(str(time()))
    sleep(1)
    configFile_Write.close()
    
    print ('Completed')
    


SinceLastRun() #runs the script
