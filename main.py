#!/usr/bin/python 
#Created in Python 3.3.0
#Created by Marc2540

from time import time
from time import sleep
from math import ceil
#from urllib  import urlretrieve
import urllib.request
import json
from random import choice
#time.time() gets time since the epoch
#time.sleep() will pause for 'x' seconds
#math.ceil() rounds out time() float to an int

oneWeekInSeconds = 604800 #change if you want to change run frequency
lastRunTime=0

#checks if config.txt exists. Creates it if it doesn't exist.
try:
    with open('config.txt') as f: pass
except:
    print ('Config file doesn\'t exist. Creating it.')
    f = open('config.txt','a')
    f.close()
del f

configFile_Read= open("config.txt", "r") #defines the config file, and opens in 'read' mode.
for lastRunTime in configFile_Read:
    if "lastRunTime=" in lastRunTime:
        print (lastRunTime[12:]) #debugging


def SinceLastRun():
    """
    Finds out how much time has passed since last run and,
    if one week has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if time() >= (int(lastRunTime[12:]) + oneWeekInSeconds):
        return askUrl()
    #You should comment out this else-statement if you're running it on startup.
    else:
        print ('According to config.txt, it hasn\'t been 1 week since last run.')
        sleep(2)
        goAheadAnyway = input ('Want to continue anyway? (Y/N) ')
        if goAheadAnyway.upper() == 'Y':
            return askUrl()
        elif goAheadAnyway.upper() == 'N':
            print ('Aborted.')
            sleep(2)
            exit()
        else:
            print ('I didn\'t understand you, try again.')
            return SinceLastRun()

def write_time_to_config_file():
    """Writes the current time to the config file and tells the user that the program is done"""
    configFile_Write= open("config.txt", "w") #opens it in 'write' mode
    configFile_Write.write("lastRunTime=" + str(ceil(time())))
    configFile_Write.close()
    sleep(1)
    
    print ('Wrote time to config file. Program done.')

    
def askUrl():
    """Asks which subreddit you want to pull from and fixes the formatting of the http request"""
    askForSubreddit = input('Which subreddit do you want to pull from? (e.g. r/pics) ')
    if str(askForSubreddit) == '':
        print ('Please try again.')
        askUrl()
    elif askForSubreddit.startswith('/') and askForSubreddit.endswith('/'):
        finalUrl = 'http://reddit.com' + askForSubreddit + '.json'
    elif askForSubreddit.startswith('/'):
        finalUrl = 'http://reddit.com' + askForSubreddit + '/.json'
    elif askForSubreddit.startswith('r') and askForSubreddit.endswith('/'):
        finalUrl = 'http://reddit.com/' + askForSubreddit + '.json'
    elif askForSubreddit.startswith('r') and not askForSubreddit.endswith('/'):
        finalUrl = 'http://reddit.com/' + askForSubreddit + '/.json'
    else:
        print ('I didn\'t understand you. Are you sure you\'re writing it correctly? (e.g r/pics, /r/pics or /r/pics/)')
        askUrl()
    write_time_to_config_file()
    print (finalUrl) #debugging

    response = urllib.request.urlopen(finalUrl)
    content = response.read()
    data = json.loads(content.decode("utf8"))
#    print(data)  #debugging

    i=0
    while i < 25:
        print (i)  #debugging
        img = data['data']['children'][i]['data']
#        print (img)   #debugging
        print ('')
        sleep(1)
        i += 1
        fileType = img['url'].lower()[-3:]
        domain = img['url'].lower().split("/")[-2]
        allowedType = fileType == 'png' or fileType == 'jpg'
        print (img['is_self'])
        print (img['url'])
        print ('Filetype = ' + fileType)
        print (allowedType)
        print (img['url'].split("/")[-1])
        print (domain)
        sleep(1)
        if img['is_self'] == True:
            print ('Image is a self-post. Skipped')
        elif allowedType == False:
            print ('Image isn\'t a png or jpg. Skipped')
        elif domain != 'i.imgur.com':
            print ('Image isn\'t hosted on imgur.com, skipping to avoid 404 errors.')
        else:
            p = img['url'].split("/")[-1]
            urllib.request.urlretrieve(img['url'],p)
            print ("Saved new image as " + p)
        
        
        



    #the following code is from reddit user u/Jonno_FTW and edited to suit my needs: (doesn't work in python 3.3)
    #http://www.reddit.com/r/wallpapers/comments/138qi2/i_have_a_script_that_randomizes_wallpapers_from/c71tqti
"""
    while 1:
        img = choice(page['data']['children'])
        if img['is_self'] or img['url'].lower() not in ['png','jpg']:
            continue
        else:
            p = img['url'].split("/")[-1]
            urlretrieve(img['url'],p)
            print ("Saved new image as",p)
            break
"""

#SinceLastRun() #runs the script

askUrl()
