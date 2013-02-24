#!/usr/bin/python 
#Created in Python 3.3.0
#Created by Marc2540
#Version 0.9.1

from time import time, sleep
from math import ceil
from urllib.request import urlopen
from shutil import copyfileobj
import json
"""
time.time() gets time since the epoch.
time.sleep() will pause for 'x' seconds.
math.ceil() rounds out time() float to an int.
urllib.request lets me pull things from websites.
shutil lets me download the results from urlopen.
the json library lets me decode .json.
"""


#settings
debug = False
frequencyCheck = 604800 #change if you want to change run frequency (in seconds) default = 604800 (1 week) 
fixedUrl = 'empty' #will use this url and wont ask for subreddit. NO ERROR CHECKING. Default is 'empty'
skipFrequencyCheck = False #default = False
skipWriteToConfig = False #default = False
runWithoutConfigFile = False #Script wont make, read, nor write to config.txt   default = False
configFileName = 'config.txt' #default = 'config.txt'
numberOfLoops = 25 #change number of cycles through the .json file. default = 25
verbose = True #want it to be silent? default = True

#pre-defining
lastRunTime = 0
subredditUrl = 'empty'
finalUrl = 'empty'
debugModifier = 'none'


if debug:
    verbose = True
if runWithoutConfigFile:
    skipFrequencyCheck = True
    skipWriteToConfig = True
else:
    if len(configFileName) < 2 or len(configFileName) > 100:
        configFileName = 'config.txt'
        if verbose:
            print ('Invalid config file name, reverted to "config.txt".')
    #checks if config.txt exists. Creates it if it doesn't exist.
    try:
        with open(configFileName) as f:
            pass
    except:
        if verbose:
            print ('Config file doesn\'t exist. Creating it.')
        f = open(configFileName,'w')
        f.write('lastRunTime=0')
        f.close()
    del f

    #reads lastRunTime from config file.
    configFile_Read = open(configFileName, "r")
    for lastRunTime in configFile_Read:
        if "lastRunTime=" in lastRunTime:
            if debug: #debug check
                print ('\nLast runtime was ' + lastRunTime[12:])
                sleep(5)
    configFile_Read.close()


def sinceLastRun():
    """
    Finds out how much time has passed since last run and,
    if one week has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if time() >= (int(lastRunTime[12:]) + frequencyCheck):
        askUrl()
    elif verbose == False:
        askUrl()
    else:
        print ('According to config.txt, it hasn\'t been ' + str(frequencyCheck) + ' seconds since last run')
        goAheadAnyway = input ('Want to continue anyway? (Y/N) ')
        if goAheadAnyway.upper() == 'Y':
            askUrl()
        elif goAheadAnyway.upper() == 'N':
            print ('Aborted.')
            sleep(2)
            exit()
        else:
            print ('I didn\'t understand you, try again.')
            sinceLastRun()

def write_time_to_config_file():
    if skipWriteToConfig != True:
        """
        Writes the current time to the config file
        """
        configFile_Write = open(configFileName, "w")
        configFile_Write.write("lastRunTime=" + str(ceil(time())))
        configFile_Write.close()
        if debug: #debug check
            print ('\nWrote lastRunTime=' + str(ceil(time())) + ' to config file.')
            sleep(5)

    
def askUrl():
    write_time_to_config_file()
    global subredditUrl
    """
    Asks which subreddit you want to pull from and fixes the formatting of the http request.
    Then it runs modifyUrl()
    """
    if fixedUrl != 'empty':
        finalUrl = fixedUrl
        fetchImg()
    else:
        askForSubreddit = input('Which subreddit do you want to pull from? (e.g. r/pics) ')
        if str(askForSubreddit) == '':
            if verbose:
                print ('Please try again.')
            askUrl()
        elif askForSubreddit.startswith('/') and askForSubreddit.endswith('/'):
            subredditUrl = 'http://reddit.com' + askForSubreddit + '.json'
            modifyUrl()
        elif askForSubreddit.startswith('/'):
            subredditUrl = 'http://reddit.com' + askForSubreddit + '/.json'
            modifyUrl()
        elif askForSubreddit.startswith('r/') and askForSubreddit.endswith('/'):
            subredditUrl = 'http://reddit.com/' + askForSubreddit + '.json'
            modifyUrl()
        elif askForSubreddit.startswith('r/') and not askForSubreddit.endswith('/'):
            subredditUrl = 'http://reddit.com/' + askForSubreddit + '/.json'
            modifyUrl()
        else:
            if verbose:
                print ('I didn\'t understand you. Are you sure you\'re writing it correctly? (e.g r/pics, /r/pics or /r/pics/)')
            askUrl()


def modifyUrl():
    global finalUrl
    """
    Takes the valid subreddit from askUrl() and modifies it.
    Runs fetchImg() afterwards.
    """
    askForModifiers = input ('Do you want to pull from the frontpage, or modify the pull-request? (frontpage/modify) ')
    if str(askForModifiers) == 'frontpage':
        finalUrl = subredditUrl
        debugModifier = 'frontpage'
        fetchImg()
    elif str(askForModifiers) != 'modify':
        if verbose:
            print ('Please try again.')
        askUrl()
    else:
        chosenModifier = input ('What kind of posts do you want? (new/top/rising/controversial) ')
        if chosenModifier == 'rising':
            finalUrl = subredditUrl[:-5] + 'rising/.json'
            debugModifier = 'rising'
            fetchImg()
        elif chosenModifier == 'con' or chosenModifier == 'controversial':
            finalUrl = subredditUrl[:-5] + 'controversial/.json'
            debugModifier = 'controversial'
            fetchImg()
        elif chosenModifier == 'new':
            finalUrl = subredditUrl[:-5] + 'new/.json'
            debugModifier = 'new'
            fetchImg()
        elif chosenModifier == 'top':
            modifierType = input ('What kind of "top" modifier do you want to use? (hour/day/week/month/year/alltime) ')
            if modifierType == 'hour':
                finalUrl = subredditUrl[:-5] + 'top/.json?sort=top&t=hour'
                debugModifier = 'top - hour'
                fetchImg()
            if modifierType == 'day':
                finalUrl = subredditUrl[:-5] + 'top/.json?sort=top&t=day'
                debugModifier = 'top - day'
                fetchImg()
            if modifierType == 'week':
                finalUrl = subredditUrl[:-5] + 'top/.json?sort=top&t=week'
                debugModifier = 'top - week'
                fetchImg()
            if modifierType == 'month':
                finalUrl = subredditUrl[:-5] + 'top/.json?sort=top&t=month'
                debugModifier = 'top - month'
                fetchImg()
            if modifierType == 'alltime':
                finalUrl = subredditUrl[:-5] + 'top/.json?sort=top&t=all'
                debugModifier = 'top - alltime'
                fetchImg()
            else:
                print ('Please try again.')
                modifyUrl()
        else:
            print ('Please try again.')
            modifyUrl()


def debugPreFetch():
    """
    Debugging values before fetching subreddit data.
    Placed here because I call fetchImg() inside if statements and
    dont want to repeat the 'if debug == true' statement 1000 times.
    """
    #debugging for askUrl()
    print ('\nThe subreddit url to get .json from is ' + subredditUrl)
    #debugging for modifyUrl()
    print ('\nThe chosen modifier is ' + str(debugModifier))
    print ('\nThe final url to get .json from is ' + str(finalUrl))
    sleep(5)



def fetchImg():
    if debug:
        debugPreFetch()
    
    response = urlopen(finalUrl)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    
    if debug: #debug check
        print ('\nThe data from ' + finalUrl + ' is returning this data: \n')
        sleep(1)
        print (data)
        sleep(5)
    
    i=0
    while i < numberOfLoops:
        try:
            img = data['data']['children'][i]['data']
            i += 1
            fileType = img['url'].lower()[-3:]
            domain = img['url'].lower().split("/")[2]
            allowedType = fileType == 'png' or fileType == 'jpg'
            if debug: #debug check
                print ('\nThis loop runs if i < ' + str(numberOfLoops) + '. I is currently ' + str(i))
                sleep(1)
                print ('\nThe current value of "img" is: \n')
                sleep(0.5)
                print (img)
                sleep(2)
                print ('\nIs this a self-post? ' + str(img['is_self']))
                print ('The go-to url of this post is: ' + img['url'])
                print ('The domain is ' + domain)
                print ('What are the 3 last letters of the url? (filetype if valid image) .' + fileType)
                print ('Is the filetype allowed? ' + str(allowedType))
                sleep(5)
                
            if img['is_self']:
                if verbose:
                    print ('Image is a self-post. Skipped')
            elif allowedType == False:
                if verbose:
                    print ('Image isn\'t a png or jpg. Skipped')
            elif domain != 'i.imgur.com':
                if verbose:
                    print ('Image isn\'t hosted on an allowed domain, skipping to avoid 404 errors.')
            else:
                p = img['url'].split("/")[-1]
                with urlopen(img['url']) as in_stream, open(p, 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
                    if verbose:
                        print ('Saved new image as ' + p)
        except IndexError:
            print ('No data left in .json file.')
            break
        except KeyboardInterrupt:
            print ('Aborted')
            break
        

#actually runs the main part of the script.
if skipFrequencyCheck:
    askUrl()
else: sinceLastRun()
