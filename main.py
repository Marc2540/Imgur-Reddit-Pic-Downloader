#!/usr/bin/python3 
#Created in Python 3.3.0
#Created by Marc2540
#Version 0.9.5

from time import time, sleep
from math import ceil
import urllib.request
from shutil import copyfileobj
import json
import urllib.error
from datetime import date

#time.time() gets time since the epoch.
#time.sleep() will pause for 'x' seconds.
#math.ceil() rounds out time() float to an int.
#urllib.request lets me pull things from websites.
#shutil lets me download the results from urlopen.
#the json library lets me decode .json.
#lets me handle HTTP errors.


#settings - Todo: Move to config file and/or commandline flags
debug = False
frequency_check = 604800 #change if you want to change run frequency (in seconds) default = 604800 (1 week) 
fixed_url = None #will use this url and wont ask for subreddit. Default is None
skip_frequency_check = False #default = False
skip_write_to_config = False #default = False
run_without_config_file = False #Script wont make, read, nor write to config.txt   default = False
config_file_name = 'config.txt' #default = 'config.txt'
number_of_loops = 25 #change number of cycles through the .json file. default = 25
verbose = True #want it to be silent? default = True

#pre-defining
last_run_time = 0
subreddit_url = None
final_url = None
debug_modifier = None
p = None
data = None
file_type = None

def since_last_run():
    """
    Finds out how much time has passed since last run and, if one week (default) has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if time() >= (int(last_run_time[14:]) + frequency_check):
        ask_url()
    elif not verbose:
        ask_url()
    else:
        print('According to config.txt, it hasn\'t been {} seconds since last run'.format(frequency_check))
        go_ahead_anyway = input('Want to continue anyway? (Y/N) ')
        if go_ahead_anyway.upper() == 'Y':
            ask_url()
        elif go_ahead_anyway.upper() == 'N':
            print('Aborted.')
            sleep(2)
            exit()
        else:
            print('I didn\'t understand you, try again.')
            since_last_run()

def write_time_to_config_file():
    if not skip_write_to_config:
        """
        Writes the current time to the config file
        """
        with open(config_file_name,'w') as f:
            f.write('last_run_time=' + str(ceil(time())))
        del f
        debug_func('last_run_time write')

    
def ask_url():
    write_time_to_config_file()
    global subreddit_url
    """
    Asks which subreddit you want to pull from and fixes the formatting of the http request.
    Then it runs modify_url()
    """
    if fixed_url:
        final_url = fixed_url
        fetch_img()
    else:
        ask_for_subreddit = input('Which subreddit do you want to pull from? (e.g. r/pics) ')
        ask_for_subreddit_lower = ask_for_subreddit.lower()
        if not ask_for_subreddit:
            verbose_func('try again')
            ask_url()
        elif ask_for_subreddit_lower.startswith('/') and ask_for_subreddit_lower.endswith('/'):
            subreddit_url = 'http://reddit.com' + ask_for_subreddit_lower + '.json'
            modify_url()
        elif ask_for_subreddit_lower.startswith('/'):
            subreddit_url = 'http://reddit.com' + ask_for_subreddit_lower + '/.json'
            modify_url()
        elif ask_for_subreddit_lower.startswith('r/') and ask_for_subreddit_lower.endswith('/'):
            subreddit_url = 'http://reddit.com/' + ask_for_subreddit_lower + '.json'
            modify_url()
        elif ask_for_subreddit_lower.startswith('r/') and not ask_for_subreddit_lower.endswith('/'):
            subreddit_url = 'http://reddit.com/' + ask_for_subreddit_lower + '/.json'
            modify_url()
        else:
            verbose_func('ask_for_subreddit writing')
            ask_url()


def modify_url():
    global final_url
    global debug_modifier
    """
    Takes the valid subreddit from ask_url() and modifies it.
    Runs fetch_img() afterwards.
    """
    if not len(subreddit_url.split('/'))==6:
        print('Your subreddit input was strange.')
        ask_url()
    else:
        ask_for_modifiers = input('Do you want to pull from the frontpage, or modify the pull-request? (frontpage/modify) ')
        if str(ask_for_modifiers) == 'frontpage':
            final_url = subreddit_url
            debug_modifier = 'frontpage'
            fetch_img()
        elif str(ask_for_modifiers) != 'modify':
            verbose_func('try again')
            ask_url()
        else:
            chosen_modifier = input('What kind of posts do you want? (new/top/rising/controversial) ')
            if chosen_modifier.lower() in ['new', 'top', 'rising', 'controversial']:
                if chosen_modifier.lower() == 'top':
                    modifier_type = input ('What kind of "top" modifier do you want to use? (hour/day/week/month/year/all) ')
                    if modifier_type.lower() in ['hour', 'day', 'week', 'month', 'all']:
                        final_url = subreddit_url[:-5] + 'top/.json?sort=top&t={}'.format(modifier_type)
                        debug_modifier = 'top - {}'.format(modifier_type)
                    else:
                        verbose_func('try again')
                        modify_url()
                else:
                    final_url = subreddit_url[:-5] + '{}/.json'.format(chosen_modifier)
                    debug_modifier = chosen_modifier.lower()
                fetch_img()
            else:
                verbose_func('try again')
                modify_url()
                
def verbose_func(arg):
    """ Collection of messages that will only print if verbose is True """ 
    if verbose:
        if arg == 'try again':
            print('Please try again.')
        elif arg == 'ask_for_subreddit writing':
            print('I didn\'t understand you. Are you sure you\'re writing it correctly? (e.g r/pics, /r/pics or /r/pics/)')
        elif arg == 'is_self':
            print('Image is a self-post. Skipped.')
        elif arg == 'allowed_type':
            print('Image is either an album, or not on the allowed filtype list. Skipped.')
        elif arg == 'allowed_domains':
            print('Image isn\'t hosted on an allowed domain, skipping to avoid 404 errors.')
        elif arg == 'image_name':
            print('Saved new image as {}'.format(p))

            
def debug_func(arg):
    """ Collection of debug messages that will only print if debug is True """
    if debug:
        if arg == 'last_run_time read':
            print ('\nLast runtime was {}'.format(last_run_time[14:]))
            sleep(2)
        elif arg == 'last_run_time write':
            #debugging for write_time_to_config_file()
            print('\nWrote last_run_time={} to config file.'.format(ceil(time())))
            sleep(2)
        elif arg == 'pre fetching images':
            #debugging for ask_url()
            print('\nThe subreddit url to get .json from is {}'.format(subreddit_url))
            #debugging for modify_url()
            print('\nThe chosen modifier is: {}'.format(debug_modifier))
            print('\nThe final url to get .json from is {}'.format(final_url))
            sleep(5)
        elif arg == 'data_return':
            #debugging for fetch_img()
            print('\nThe data from {} is returning this data: \n'.format(final_url))
            sleep(0.5)
            print(data)
            sleep(5)
        elif arg == 'fetching images':
            #debugging 'while loop' in fetch_img()
            print('\nThis loop runs if i < {0}. I is currently {1}'.format(number_of_loops, i))
            sleep(1)
            print('\nThe current value of "img" is: \n')
            sleep(0.5)
            print(img)
            sleep(2)
            print('\nIs this a self-post? {}'.format(img['is_self']))
            print('The go-to url of this post is: {}'.format(img['url']))
            print('The domain is {}'.format(domain))
            print('What are the 3 last letters of the url? (file_type if valid image) .{}'.format(file_type))
            print('Is the file_type allowed? {}'.format(allowed_type))
            sleep(5)



def fetch_img():
    global p
    global data
    global i
    global number_of_loops
    global domain
    global img
    global allowed_type
    global file_type
    debug_func('pre fetching images')
    
    request = urllib.request.Request(final_url, None, headers={'User-Agent' : 'Imgur-Reddit-Pic-Downloader v0.9.5 by u/Marc2540'})
    response = urllib.request.urlopen(request)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    
    debug_func('data_return')
    
    i=0
    while i < number_of_loops:
        try:
            img = data['data']['children'][i]['data']
            i += 1
            file_type = img['url'].lower()[-3:]
            domain = img['url'].lower().split("/")[2]
            allowed_type = True if file_type in ['png', 'jpg', 'jpeg', 'gif'] else False
            allowed_domains = True if domain in ['i.imgur.com', 'imgur.com', 'i.minus.com'] else False
            
            debug_func('fetching images')
            
            if img['is_self']:
                verbose_func('is_self')
            """
            #This is VERY much Work in Progress
            elif img['url'].split('/')[-2] == 'a':
                print('Image is an imgur album.')
                imgur_url = 'https://api.imgur.com/3/gallery/album/' + img['url'].split('/')[-1]
                print (imgur_url)
                imgur_request = urllib.request.Request(imgur_url, None, headers={'Authorization' : 'Client-ID 112ba8a808315df'})
                imgur_response = urllib.request.urlopen(imgur_request)
                imgur_content = imgur_response.read()
                imgur_data = json.loads(imgur_content.decode("utf8"))
                
                print (imgur_data)
                break
                sleep(100)
            """
            elif not allowed_type:
                verbose_func('allowed_type')
            elif not allowed_domains:
                verbose_func('allowed_domains')
            else:
                p = '{0} - {1}.{2}'.format(date.today(), img['title'][0:35], file_type)
                with urllib.request.urlopen(img['url']) as in_stream, open(p, 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
                    verbose_func('image_name')
            sleep(2) #limit speed of requests. - limit in accordance with the reddit api
        except IndexError:
            print('No data left in .json file.')
            break
        except KeyboardInterrupt:
            print('Aborted')
            break



if debug:
    verbose = True
if run_without_config_file:
    skip_frequency_check = True
    skip_write_to_config = True
else:
    if len(config_file_name) < 2 or len(config_file_name) > 100:
        config_file_name = 'config.txt'
        print ('Invalid config file name, reverted to "config.txt".')
    #checks if config.txt exists. Creates it if it doesn't exist.
    try:
        with open(config_file_name) as f:
            pass
    except:
        print ('Config file doesn\'t exist. Creating it.')
        with open(config_file_name,'w') as f:
            f.write('last_run_time=0')
    del f

    #reads last_run_time from config file.
    with open(config_file_name,'r') as f:
        for last_run_time in f:
            if "last_run_time=" in last_run_time:
                debug_func('last_run_time read')
    del f



#actually runs the main part of the script.
if skip_frequency_check:
    ask_url()
else: since_last_run()
