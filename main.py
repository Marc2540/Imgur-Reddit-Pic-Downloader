#!/usr/bin/python3 
#Created in Python 3.3.0
#Written by Marc2540
#Version 0.9.9

from time import time, sleep            #time.time() gets time since the epoch
                                        #time.sleep() will pause for 'x' seconds
from math import ceil                   #math.ceil() rounds out time() float to an int
import urllib.request                   #urllib.request lets me pull things from websites
from shutil import copyfileobj          #shutil lets me download the results from urlopen
import json                             #the json library lets me decode .json
from datetime import date               #datetime lets me get current date
import argparse                         #argparse lets me parse command-line arguments
from string import ascii_letters, digits #gives me a list of allowed characters for name sanitization
from unicodedata import normalize       #used swapping accented characters with unaccented ones before sanitization
import os                               #used for creating directories

parser = argparse.ArgumentParser(description='Downloads pictures from a specified subreddit.')
group1 = parser.add_argument_group(title='Optional arguments: Run frequency options')
parser.add_argument('-d', '--debug', help='Debug flag', action='store_true')
parser.add_argument('-q', '--quiet', help='Makes the script not print anything.', action='store_false')
group1.add_argument('-fc', '--freq_enable', help='Enables frequency check (and config file).', action='store_true')
group1.add_argument('-fd', '--freq_duration', type=int, help='Specifies run frequency in seconds.', default=604800)
group1.add_argument('-cfg', help='Specify config file name.', default='config.txt')
parser.add_argument('-la', '--loop_amount', type=int, help='Number of loops through .json file.', default=25)
parser.add_argument('-u', '--url', help='Uses specified url instead of asking for input. (either subreddit or imgur album)')

flags = vars(parser.parse_args())

debug = flags['debug']
verbose = flags['quiet']
config_file_name = flags['cfg']
check_run_frequency = flags['freq_enable']
frequency_duration = flags['freq_duration']
number_of_loops = flags['loop_amount']
fixed_url = flags['url']

#user specifications:
user_User_agent = 'Imgur-Reddit-Pic-Downloader v0.9.9 by u/Marc2540'
user_allowed_file_type = ['png', 'jpg', 'gif']
user_allowed_domains = ['i.imgur.com', 'imgur.com', 'i.minus.com']
user_imgur_ClientID = '112ba8a808315df'

#pre-defining
last_run_time = 0
subreddit_url = None
debug_modifier = None
p = None
imgur_p = None
data = None
file_type = None
final_url = None
imgur_number_of_images = None
imgur_url = None
imgur_i = None

def since_last_run():
    """
    Finds out how much time has passed since last run and, if one week (default) has passed, runs the program.
    If one week hasn't passed, it asks if you want to continue anyway.
    """
    if time() >= int(last_run_time[14:]) + frequency_duration:
        ask_url()
    elif not verbose:
        ask_url()
    else:
        print('According to config.txt, it hasn\'t been {} seconds since last run'.format(frequency_duration))
        go_ahead_anyway = input('Want to continue anyway? (Y/N) ')
        if go_ahead_anyway.upper() == 'Y':
            ask_url()
        elif go_ahead_anyway.upper() == 'N':
            print('Aborted.')
            sleep(1)
            exit()
        else:
            print('I didn\'t understand you, try again.')
            since_last_run()

def write_time_to_config_file():
    """Writes the current time to the config file"""
    if check_run_frequency:
        with open(config_file_name,'w') as f:
            f.write('last_run_time=' + str(ceil(time())))
        del f
        debug_func('last_run_time write')

def ask_url():
    """
    Asks which subreddit you want to pull from and fixes the formatting of the http request.
    Then it runs modify_url()
    """
    write_time_to_config_file()
    global subreddit_url
    global final_url
    
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
    """
    Takes the valid subreddit from ask_url() and modifies it.
    Runs fetch_img() afterwards.
    """
    global final_url
    global debug_modifier
    
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

def filename_sanitization(filename):
    valid_characters = str('-_.() {0}{1}'.format(ascii_letters, digits))
    clean_filename = str(normalize('NFKD', filename).encode('ASCII', 'ignore'))
    return ''.join(char for char in clean_filename if char in valid_characters)[1:]

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
            print('Image is not on the allowed filetype list. Skipped.')
        elif arg == 'allowed_domains':
            print('Image isn\'t hosted on an allowed domain, skipping to avoid 404 errors.')
        elif arg == 'image name':
            print('Saved new image as {0}, in folder "{1}"'.format(p.split('\\')[-1], p.split('\\')[-2]))
        elif arg == 'imgur image name':
            print('Imgur Album: Saved new image as {0}, in folder "{1}\\{2}"'.format(imgur_p.split('\\')[-1], imgur_p.split('\\')[-3], imgur_p.split('\\')[-2]))
        elif arg == 'imgur album':
            print('Link is an imgur album. And contains {} images'.format(imgur_number_of_images))
        elif arg == 'imgur album info.txt':
            print('Album information has been written to info.txt in the album folder')

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
        elif arg == 'cmd flags':
            #debugging command-line flags
            print('\nIs debugging on? {}'.format(debug))
            print('\nIs verbose on? {}'.format(verbose))
            print('\nWhat is the name of the config file? {}'.format(config_file_name))
            print('\nDo we check the run frequency and enable config file? {}'.format(check_run_frequency))
            print('\nFrequency between runs is {}.'.format(frequency_duration))
            print('\nThe fixed url is {}.'.format(fixed_url))
            print('\nWe are looping through the .json file {} times.'.format(number_of_loops))
            sleep(5)
        elif arg == 'imgur album url':
            print('\nThe imgur album link is {}'.format(imgur_url))
            sleep(2)
        elif arg == 'imgur fetching images':
            print('This imgur album has {0} images, we are downloading image number {1}'.format(imgur_number_of_images, imgur_i))
            

def fetch_img():
    """Pulls .json information and downloads valid images."""
    global p
    global data
    global i
    global number_of_loops
    global domain
    global img
    global allowed_type
    global file_type
    global imgur_p
    global imgur_number_of_images
    global imgur_url
    global imgur_i
    debug_func('pre fetching images')
    
    request = urllib.request.Request(final_url, None, headers={'User-Agent' : '{}'.format(user_User_agent)})
    response = urllib.request.urlopen(request)
    content = response.read()
    data = json.loads(content.decode("utf8"))
    
    folder = '{0}\\{1}'.format(os.getcwd(), date.today())
    os.makedirs(folder, exist_ok=True)
    
    i=0
    while i < number_of_loops:
        try:
            img = data['data']['children'][i]['data']
            
            file_type = img['url'].lower()[-3:]
            domain = img['url'].lower().split("/")[2]
            allowed_type = True if file_type in user_allowed_file_type else False
            allowed_domains = True if domain in user_allowed_domains else False
            
            if i < 3:
                debug_func('fetching images')
            
            if img['is_self']:
                verbose_func('is_self')
            elif img['url'].split('/')[-3] + '/' + img['url'].split('/')[-2] == 'imgur.com/a':
                #imgur album downloading
                imgur_url = 'https://api.imgur.com/3/album/{}.json'.format(img['url'].split('/')[-1])
                debug_func('imgur album url')
                
                imgur_request = urllib.request.Request(imgur_url, None, headers={'Authorization' : 'Client-ID {}'.format(user_imgur_ClientID)})
                imgur_response = urllib.request.urlopen(imgur_request)
                imgur_content = imgur_response.read()
                imgur_data = json.loads(imgur_content.decode("utf8"))
                
                imgur_i = 0
                imgur_number_of_images = imgur_data['data']['images_count']
                
                imgur_album_title = filename_sanitization(imgur_data['data']['title']) if imgur_data['data']['title'] else 'Unnamed Album'
                imgur_folder = '{0}\\{1}'.format(folder, imgur_album_title)
                imgur_description = filename_sanitization(imgur_data['data']['description']) if imgur_data['data']['description'] else 'No desciption'
                imgur_uploader = filename_sanitization(imgur_data['data']['account_url']) if imgur_data['data']['account_url'] else 'Anonymous uploader'
                imgur_album_link = imgur_data['data']['link']
                
                os.makedirs(imgur_folder, exist_ok=True)
                with open('{0}\\info.txt'.format(imgur_folder), 'a') as f:
                    f.write('\nTitle: {0}\nUploader: {1}\nAlbum link: {2}\nNumber of images: {3}\nDescription: {4}'.format(imgur_album_title, imgur_uploader, imgur_album_link, imgur_number_of_images, imgur_description))
                verbose_func('imgur album info.txt')
                del f
                
                verbose_func('imgur album')
                while imgur_i < imgur_number_of_images:
                    imgur_image_link = imgur_data['data']['images'][imgur_i]['link']
                    os.makedirs(imgur_folder, exist_ok=True)
                    
                    imgur_p = '{0}\\{1} - {2}'.format(imgur_folder, imgur_i, imgur_image_link.split('/')[-1])
                    debug_func('imgur fetching images')
                    imgur_i +=1
                    
                    with urllib.request.urlopen(imgur_image_link) as in_stream, open(imgur_p, 'wb') as out_file:
                        copyfileobj(in_stream, out_file)
                        verbose_func('imgur image name')
                        
            elif not allowed_type:
                verbose_func('allowed_type')
            elif not allowed_domains:
                verbose_func('allowed_domains')
            else:
                valid_title = filename_sanitization(img['title'][0:35])
                p = '{0}\\{1}.{2}'.format(folder, valid_title, file_type)
                with urllib.request.urlopen(img['url']) as in_stream, open(p, 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
                    verbose_func('image name')
            i += 1
            sleep(2) #limit speed of requests. - limit in accordance with the reddit api
        except IndexError:
            print('No data left in .json file.')
            break
        except KeyboardInterrupt:
            exit()

if debug:
    verbose = True
    debug_func('cmd flags')
if not check_run_frequency:
    ask_url()
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
        with open(config_file_name, 'w') as f:
            f.write('last_run_time=0')
    del f
    #reads last_run_time from config file.
    with open(config_file_name,'r') as f:
        for last_run_time in f:
            if "last_run_time=" in last_run_time:
                debug_func('last_run_time read')
    del f
    since_last_run()
