#!/usr/bin/python 
#Created in Python 3.3.0
#Created by Marc2540
#Version 0.9.2

from time import time, sleep
from math import ceil
import urllib.request
from shutil import copyfileobj
import json
import urllib.error

#time.time() gets time since the epoch.
#time.sleep() will pause for 'x' seconds.
#math.ceil() rounds out time() float to an int.
#urllib.request lets me pull things from websites.
#shutil lets me download the results from urlopen.
#the json library lets me decode .json.
#lets me handle HTTP errors.



#settings
debug = False
frequency_check = 604800 #change if you want to change run frequency (in seconds) default = 604800 (1 week) 
fixed_url = 'empty' #will use this url and wont ask for subreddit. NO ERROR CHECKING. Default is 'empty'
skip_frequency_check = False #default = False
skip_write_to_config = False #default = False
run_without_config_file = False #Script wont make, read, nor write to config.txt   default = False
config_file_name = 'config.txt' #default = 'config.txt'
number_of_loops = 25 #change number of cycles through the .json file. default = 25
verbose = True #want it to be silent? default = True

#pre-defining
last_run_time = 0
subreddit_url = 'empty'
final_url = 'empty'
debug_modifier = 'none'


if debug:
    verbose = True
if run_without_config_file:
    skip_frequency_check = True
    skip_write_to_config = True
else:
    if len(config_file_name) < 2 or len(config_file_name) > 100:
        config_file_name = 'config.txt'
        if verbose:
            print ('Invalid config file name, reverted to "config.txt".')
    #checks if config.txt exists. Creates it if it doesn't exist.
    try:
        with open(config_file_name) as f:
            pass
    except:
        if verbose:
            print ('Config file doesn\'t exist. Creating it.')
        f = open(config_file_name,'w')
        f.write('last_run_time=0')
        f.close()
    del f

    #reads last_run_time from config file.
    config_file_read = open(config_file_name, "r")
    for last_run_time in config_file_read:
        if "last_run_time=" in last_run_time:
            if debug: #debug check
                print ('\nLast runtime was ' + last_run_time[14:])
                sleep(5)
    config_file_read.close()


def since_last_run():
    """
    Finds out how much time has passed since last run and,
    if one week has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if time() >= (int(last_run_time[14:]) + frequency_check):
        ask_url()
    elif not verbose:
        ask_url()
    else:
        print ('According to config.txt, it hasn\'t been ' + str(frequency_check) + ' seconds since last run')
        go_ahead_anyway = input ('Want to continue anyway? (Y/N) ')
        if go_ahead_anyway.upper() == 'Y':
            ask_url()
        elif go_ahead_anyway.upper() == 'N':
            print ('Aborted.')
            sleep(2)
            exit()
        else:
            print ('I didn\'t understand you, try again.')
            since_last_run()

def write_time_to_config_file():
    if not skip_write_to_config:
        """
        Writes the current time to the config file
        """
        config_file_write = open(config_file_name, "w")
        config_file_write.write("last_run_time=" + str(ceil(time())))
        config_file_write.close()
        if debug: #debug check
            print ('\nWrote last_run_time=' + str(ceil(time())) + ' to config file.')
            sleep(5)

    
def ask_url():
    write_time_to_config_file()
    global subreddit_url
    """
    Asks which subreddit you want to pull from and fixes the formatting of the http request.
    Then it runs modify_url()
    """
    if fixed_url != 'empty':
        final_url = fixed_url
        fetch_img()
    else:
        ask_for_subreddit = input('Which subreddit do you want to pull from? (e.g. r/pics) ')
        if str(ask_for_subreddit) == '':
            if verbose:
                print ('Please try again.')
            ask_url()
        elif ask_for_subreddit.startswith('/') and ask_for_subreddit.endswith('/'):
            subreddit_url = 'http://reddit.com' + ask_for_subreddit + '.json'
            modify_url()
        elif ask_for_subreddit.startswith('/'):
            subreddit_url = 'http://reddit.com' + ask_for_subreddit + '/.json'
            modify_url()
        elif ask_for_subreddit.startswith('r/') and ask_for_subreddit.endswith('/'):
            subreddit_url = 'http://reddit.com/' + ask_for_subreddit + '.json'
            modify_url()
        elif ask_for_subreddit.startswith('r/') and not ask_for_subreddit.endswith('/'):
            subreddit_url = 'http://reddit.com/' + ask_for_subreddit + '/.json'
            modify_url()
        else:
            if verbose:
                print ('I didn\'t understand you. Are you sure you\'re writing it correctly? (e.g r/pics, /r/pics or /r/pics/)')
            ask_url()


def modify_url():
    global final_url
    """
    Takes the valid subreddit from ask_url() and modifies it.
    Runs fetch_img() afterwards.
    """
    ask_for_modifiers = input ('Do you want to pull from the frontpage, or modify the pull-request? (frontpage/modify) ')
    if str(ask_for_modifiers) == 'frontpage':
        final_url = subreddit_url
        debug_modifier = 'frontpage'
        fetch_img()
    elif str(ask_for_modifiers) != 'modify':
        if verbose:
            print ('Please try again.')
        ask_url()
    else:
        chosen_modifier = input ('What kind of posts do you want? (new/top/rising/controversial) ')
        if chosen_modifier == 'rising':
            final_url = subreddit_url[:-5] + 'rising/.json'
            debug_modifier = 'rising'
            fetch_img()
        elif chosen_modifier == 'con' or chosen_modifier == 'controversial':
            final_url = subreddit_url[:-5] + 'controversial/.json'
            debug_modifier = 'controversial'
            fetch_img()
        elif chosen_modifier == 'new':
            final_url = subreddit_url[:-5] + 'new/.json'
            debug_modifier = 'new'
            fetch_img()
        elif chosen_modifier == 'top':
            modifier_type = input ('What kind of "top" modifier do you want to use? (hour/day/week/month/year/alltime) ')
            if modifier_type == 'hour':
                final_url = subreddit_url[:-5] + 'top/.json?sort=top&t=hour'
                debug_modifier = 'top - hour'
                fetch_img()
            if modifier_type == 'day':
                final_url = subreddit_url[:-5] + 'top/.json?sort=top&t=day'
                debug_modifier = 'top - day'
                fetch_img()
            if modifier_type == 'week':
                final_url = subreddit_url[:-5] + 'top/.json?sort=top&t=week'
                debug_modifier = 'top - week'
                fetch_img()
            if modifier_type == 'month':
                final_url = subreddit_url[:-5] + 'top/.json?sort=top&t=month'
                debug_modifier = 'top - month'
                fetch_img()
            if modifier_type == 'alltime':
                final_url = subreddit_url[:-5] + 'top/.json?sort=top&t=all'
                debug_modifier = 'top - alltime'
                fetch_img()
            else:
                print ('Please try again.')
                modify_url()
        else:
            print ('Please try again.')
            modify_url()


def debug_pre_fetch():
    """
    Debugging values before fetching subreddit data.
    Placed here because I call fetch_img() inside if statements and
    dont want to repeat the 'if debug == true' statement 1000 times.
    """
    #debugging for ask_url()
    print ('\nThe subreddit url to get .json from is ' + subreddit_url)
    #debugging for modify_url()
    print ('\nThe chosen modifier is ' + str(debug_modifier))
    print ('\nThe final url to get .json from is ' + str(final_url))
    sleep(5)



def fetch_img():
    if debug:
        debug_pre_fetch()
    
    request = urllib.request.Request(final_url, None, headers={'User-Agent':'Imgur-Reddit-Pic-Downloader v0.9.2 by u/Marc2540'})
    response = urllib.request.urlopen(request)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    
    if debug: #debug check
        print ('\nThe data from ' + final_url + ' is returning this data: \n')
        sleep(1)
        print (data)
        sleep(5)
    
    i=0
    while i < number_of_loops:
        try:
            img = data['data']['children'][i]['data']
            i += 1
            file_type = img['url'].lower()[-3:]
            domain = img['url'].lower().split("/")[2]
            allowed_type = file_type == 'png' or file_type == 'jpg' or file_type == 'gif'
            allowed_domains = domain == 'i.imgur.com' or domain == 'i.minus.com'
            if debug: #debug check
                print ('\nThis loop runs if i < ' + str(number_of_loops) + '. I is currently ' + str(i))
                sleep(1)
                print ('\nThe current value of "img" is: \n')
                sleep(0.5)
                print (img)
                sleep(2)
                print ('\nIs this a self-post? ' + str(img['is_self']))
                print ('The go-to url of this post is: ' + img['url'])
                print ('The domain is ' + domain)
                print ('What are the 3 last letters of the url? (file_type if valid image) .' + file_type)
                print ('Is the file_type allowed? ' + str(allowed_type))
                sleep(5)
            
            if img['is_self']:
                if verbose:
                    print ('Image is a self-post. Skipped')
            elif not allowed_type:
                if verbose:
                    print ('Image isn\'t is either an album, or not on the allowed filtype list. Skipped.')
            elif not allowed_domains:
                if verbose:
                    print ('Image isn\'t hosted on an allowed domain, skipping to avoid 404 errors.')
            else:
                p = img['url'].split("/")[-1]
                with urllib.request.urlopen(img['url']) as in_stream, open(p, 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
                    if verbose:
                        print ('Saved new image as ' + p)
            sleep(2) #limit speed of requests. - limit to a max of 30/sec in accordance with the reddit api
        except IndexError:
            print ('No data left in .json file.')
            break
        except KeyboardInterrupt:
            print ('Aborted')
            break
        

#actually runs the main part of the script.
if skip_frequency_check:
    ask_url()
else: since_last_run()
