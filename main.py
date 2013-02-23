#!/usr/bin/python 
#Created in Python 3.3.0
#Created by Marc2540

from time import time
from time import sleep
from math import ceil
import urllib.request
import json
"""
time.time() gets time since the epoch
time.sleep() will pause for 'x' seconds
math.ceil() rounds out time() float to an int
urllib.request lets me pull things from websites.
the json library lets me decode .json.
"""

#settings
debug = False
frequencyCheck = 604800 #change if you want to change run frequency (in seconds) default = 604800 (1 week) 
fixedUrl = 'empty' #will use this url and wont ask for subreddit. NO ERROR CHECKING. Default is 'empty'
skipFrequencyCheck = False #default = False
skipWriteToConfig = False #default = False
runWithoutConfigFile = False #Script wont make, read, nor write to config.txt   default = False
configFileName= 'config.txt' #default = 'config.txt'



lastRunTime = 0



if runWithoutConfigFile == True:
    skipFrequencyCheck = True
    skipWriteToConfig = True
else:
    if len(configFileName) < 2 or len(configFileName) > 100:
        configFileName = 'config.txt'
        print ('Invalid config file name, reverted to "config.txt".')
    #checks if config.txt exists. Creates it if it doesn't exist.
    try:
        with open(configFileName) as f: pass
    except:
        print ('Config file doesn\'t exist. Creating it.')
        f = open(configFileName,'w')
        f.write('lastRunTime=0')
        f.close()
    del f

    configFile_Read = open(configFileName, "r") #defines the config file, and opens in 'read' mode.
    for lastRunTime in configFile_Read:
        if "lastRunTime=" in lastRunTime:
            if debug == True: #debug check
                print ('')
                print ('Last runtime was ' + lastRunTime[12:])
                sleep(5)
    configFile_Read.close()

def SinceLastRun():
    """
    Finds out how much time has passed since last run and,
    if one week has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if skipFrequencyCheck == True:
        askUrl()
    else:
        try:
            if time() >= (int(lastRunTime[12:]) + frequencyCheck):
                askUrl()
            else:
                print ('According to config.txt, it hasn\'t been 1 week since last run.')
                goAheadAnyway = input ('Want to continue anyway? (Y/N) ')
                if goAheadAnyway.upper() == 'Y':
                    askUrl()
                elif goAheadAnyway.upper() == 'N':
                    print ('Aborted.')
                    sleep(2)
                    exit()
                else:
                    print ('I didn\'t understand you, try again.')
                    SinceLastRun()
        except:
            print ('If you aborted the program, ignore this.')
            print ('If you didn\'t, then there is invalid info in the config file. Please delete it.')
            sleep(10)
            exit()

def write_time_to_config_file():
    if skipWriteToConfig != True:
        """Writes the current time to the config file and tells the user that the program is done"""
        configFile_Write = open(configFileName, "w")
        configFile_Write.write("lastRunTime=" + str(ceil(time())))
        configFile_Write.close()
        sleep(0.5)
        if debug == True: #debug check
            print ('')
            print ('Wrote lastRunTime=' + str(ceil(time())) + ' to config file.')
            sleep(5)

    
def askUrl():
    write_time_to_config_file()
    """
    Asks which subreddit you want to pull from and fixes the formatting of the http request.
    Then it get a .json page from the url and downloads valid images.
    """
    if fixedUrl != 'empty':
        finalUrl = fixedUrl
    else:
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
    
    if debug == True: #debug check
        print ('')
        print ('The final url to get .json from is ' + finalUrl)
        sleep(5)

    response = urllib.request.urlopen(finalUrl)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    
    if debug == True: #debug check
        print ('')
        print ('The data from ' + finalUrl + 'is returning this data:')
        sleep(2)
        print ('')
        print (data)
        sleep(5)
    
    i=0
    while i < 25:
        img = data['data']['children'][i]['data']
        i += 1
        fileType = img['url'].lower()[-3:]
        domain = img['url'].lower().split("/")[2]
        allowedType = fileType == 'png' or fileType == 'jpg'
        
        if debug == True: #debug check
            print ('')
            print ('This loop runs if i < 25. I is currently ' + str(i))
            sleep(1)
            print ('')
            print ('The current value of "img" is:')
            sleep(0.5)
            print ('')
            print (img)
            print ('')
            sleep(2)
            print ('Is this a self-post? ' + str(img['is_self']))
            print ('The go-to url of this post is: ' + img['url'])
            print ('The domain is ' + domain)
            print ('What are the 3 last letters of the url? (filetype if valid image) .' + fileType)
            print ('Is the filetype allowed? ' + str(allowedType))
            sleep(10)
            
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

SinceLastRun() #actually runs the script.



    #the following code is from reddit user u/Jonno_FTW. It is heavily edited above.
    #It now runs on python 3.3 and suits my needs: (without this I would have had a really hard time!)
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
