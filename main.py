#!/usr/bin/python3 
#Created in Python 3.3.0
#Written by Marc2540

#from time import time, sleep            #time.time() gets time since the epoch
#                                        #time.sleep() will pause for 'x' seconds
#from math import ceil                   #math.ceil() rounds out time() float to an int
import urllib.request                   #urllib.request lets me pull things from websites
from shutil import copyfileobj          #shutil lets me download the results from urlopen
import json                             #the json library lets me decode .json
from datetime import date               #datetime lets me get current date
import argparse                         #argparse lets me parse command-line arguments
from string import ascii_letters, digits #gives me a list of allowed characters for name sanitization
from unicodedata import normalize       #used swapping accented characters with unaccented ones before sanitization
import os                               #used for creating directories

parser = argparse.ArgumentParser(description='Downloads pictures from a specified subreddit.')
#group1 = parser.add_argument_group(title='Optional arguments: Run frequency options')
#parser.add_argument('-d', '--debug', help='Debug flag', action='store_true')
#parser.add_argument('-q', '--quiet', help='Makes the script not print anything.', action='store_false')
#group1.add_argument('-fc', '--freq_enable', help='Enables frequency check (and config file).', action='store_true')
#group1.add_argument('-fd', '--freq_duration', type=int, help='Specifies run frequency in seconds.', default=604800)
#group1.add_argument('-cfg', help='Specify config filename.', default='config.txt')
parser.add_argument('-la', '--loop_amount', type=int, help='Number of loops through .json file.', default=25)
parser.add_argument('-u', '--url', help='Uses specified url instead of asking for input. (either subreddit or imgur album)')

flags = vars(parser.parse_args())

#debug = flags['debug']
#verbose = flags['quiet']
#config_filename = flags['cfg']
#check_run_frequency = flags['freq_enable']
#frequency_duration = flags['freq_duration']
number_of_loops = flags['loop_amount']
fixed_url = flags['url']

#user specifications:
user_User_agent = 'Imgur-Reddit-Pic-Downloader v? by u/Marc2540'
user_allowed_filetype = ['png', 'jpg', 'gif']
user_allowed_domains = ['i.imgur.com', 'imgur.com', 'i.minus.com']
user_imgur_ClientID = '112ba8a808315df'


class UrlFixing:
    """Translates the user input to a useable reddit url"""
    
    def pull_or_modify(user_input):
        chosen_modifier = ''
        
        if user_input == 'frontpage':
            chosen_modifier = '.json'
        elif user_input in ['new', 'rising', 'controversial']:
            chosen_modifier = '{}/.json'.format(user_input)
        elif user_input in ['hour', 'day', 'week', 'month', 'all']:
            chosen_modifier = 'top/.json?sort=top&t={}'.format(user_input)
        return chosen_modifier
        
    def fix_subreddit_url(user_input):
        subreddit_url = ''
        if user_input.startswith('/') and user_input.endswith('/'):
            subreddit_url = 'http://reddit.com' + user_input            
        elif user_input.startswith('/'):
            subreddit_url = 'http://reddit.com' + user_input + '/'
        elif user_input.startswith('r/') and user_input.endswith('/'):
            subreddit_url = 'http://reddit.com/' + user_input
        elif user_input.startswith('r/') and not user_input.endswith('/'):
            subreddit_url = 'http://reddit.com/' + user_input + '/'
        return subreddit_url
        
    def pull_data(url, headers):
        request = urllib.request.Request(url, None, headers)
        response = urllib.request.urlopen(request)
        content = response.read()
        data = json.loads(content.decode("utf8"))
        return data


class RedditData:
    """Get info from reddit .json response."""
    def __init__(self, response):
        self.data = response['data']['children']
        
    def get_filetype(self, number):
        file_type = self.data[number]['data']['url'][-3:]
        return file_type
    
    def get_domain(self, number):
        domain = self.data[number]['data']['url'].split('/')[2]
        return domain
        
    def get_full_url(self, number):
        full_image_url = self.data[number]['data']['url']
        return full_image_url
        
    def check_if_imgur_album(self, number):
        temp_url_split = self.data[number]['data']['url'].split('/')
        return True if temp_url_split[-3] + '/' + temp_url_split[-2] == 'imgur.com/a' else False
    
    def self_post(self, number):
        is_self = self.data[number]['data']['is_self']
        return is_self
        
    def link_title(self, number):
        image_title = filename_sanitization(self.data[number]['data']['title'])
        return image_title
    
    def get_imgur_api_url(self, number):
        full_album_url = self.data[number]['data']['url']
        imgur_api_url = 'https://api.imgur.com/3/album/{}.json'.format(full_album_url.split('/')[-1])
        return imgur_api_url


class ImgurData:
    """Get info from imgur api .json response."""
    def __init__(self, response):
        self.title = filename_sanitization(response['data']['title'])
        self.valid_title = 'Unnamed Album' if self.title == 'None' else self.title
        self.description = filename_sanitization(response['data']['description'])
        self.uploader = filename_sanitization(response['data']['account_url'])
        self.album_link = response['data']['link']
        self.images_count = response['data']['images_count']
        self.image_info = response['data']['images']
    
    def get_folder(self, folder):
        imgur_folder = '{0}\\{1}'.format(folder, self.valid_title)
        os.makedirs(imgur_folder, exist_ok=True)
        return imgur_folder
        
    def get_image_link(self, number):
        image_link = self.image_info[number]['link']
        return image_link


def main():
    url_defining = UrlFixing
    ask_for_subreddit = None
    ask_for_modifiers = None
    ask_for_modifiers_specific = None
    
    if fixed_url:
        chosen_url = fixed_url
    else:
        while not ask_for_subreddit:
            ask_for_subreddit = input('Which subreddit do you want to pull from? (e.g. r/pics) ').lower()
            subreddit_url = url_defining.fix_subreddit_url(ask_for_subreddit)
            if not len(subreddit_url.split('/')) == 6:
                ask_for_subreddit = None
    
        while not ask_for_modifiers:
            # Notice - you can type the final modifier directly
            ask_for_modifiers = input('Do you want to pull from the frontpage, or modify the pull-request? (frontpage/modify) ').lower()
            
            if ask_for_modifiers == 'modify':
                ask_for_modifiers_specific = input('What kind of posts do you want? (new/top/rising/controversial) ').lower()
                if ask_for_modifiers_specific in ['new', 'rising', 'controversial']:
                    ask_for_modifiers = ask_for_modifiers_specific
                elif ask_for_modifiers_specific == 'top':
                    ask_for_modifier_top = input('What kind of "top" modifier do you want to use? (hour/day/week/month/year/all) ').lower()
                    if ask_for_modifier_top in ['hour', 'day', 'week', 'month', 'all']:
                        ask_for_modifiers = ask_for_modifier_top
                        
            chosen_modifier = url_defining.pull_or_modify(ask_for_modifiers)
            if not chosen_modifier:
                ask_for_modifiers = None
        chosen_url = subreddit_url + chosen_modifier

    fetch_img(chosen_url)

def filename_sanitization(filename):
    if filename:
        valid_characters = str('-_.() {0}{1}'.format(ascii_letters, digits))
        clean_filename = str(normalize('NFKD', filename).encode('ASCII', 'ignore'))
        return ''.join(char for char in clean_filename if char in valid_characters)[1:]
    else:
        return 'None'
    
def fetch_img(chosen_url):
    url_defining = UrlFixing
    
    imgur_headers = {'Authorization' : 'Client-ID {}'.format(user_imgur_ClientID)}
    reddit_headers = {'User-Agent' : '{}'.format(user_User_agent)}
    reddit_response = url_defining.pull_data(chosen_url, reddit_headers)

    reddit_data = RedditData(reddit_response)
    
    folder = '{0}\\{1}'.format(os.getcwd(), date.today())
    os.makedirs(folder, exist_ok=True)
    
    i = 0
    try:
        while i < number_of_loops:
            allowed_type = True if reddit_data.get_filetype(i) in user_allowed_filetype else False
            allowed_domains = True if reddit_data.get_domain(i) in user_allowed_domains else False
            
            if reddit_data.self_post(i):
                print('Skipped: Self-post.')
            elif reddit_data.check_if_imgur_album(i):
                imgur_url = reddit_data.get_imgur_api_url(i)
                imgur_response = url_defining.pull_data(imgur_url, imgur_headers)
                imgur_data = ImgurData(imgur_response)
                
                with open('{0}\\info.txt'.format(imgur_data.get_folder(folder)), 'a') as f:
                    f.write('\nTitle: {0}\nUploader: {1}\nAlbum link: {2}\nNumber of images: {3}\nDescription: {4}'.format(imgur_data.valid_title,
                                                                                                                           imgur_data.uploader,
                                                                                                                           imgur_data.album_link,
                                                                                                                           imgur_data.images_count,
                                                                                                                           imgur_data.description))
                imgur_i = 0
                while imgur_i < imgur_data.images_count:
                    imgur_save_to = '{0}\\{1} - {2}'.format(imgur_data.get_folder(folder),imgur_i,
                                                            imgur_data.get_image_link(imgur_i).split('/')[-1])
                    with urllib.request.urlopen(imgur_data.get_image_link(imgur_i)) as in_stream, open(imgur_save_to, 'wb') as out_file:
                        copyfileobj(in_stream, out_file)
                        print('Imgur Album: Saved new image as {0}, in folder "{1}\\{2}"'.format(imgur_save_to.split('\\')[-1],
                                                                                                 imgur_save_to.split('\\')[-3],
                                                                                                 imgur_save_to.split('\\')[-2]))

                    imgur_i += 1
            elif not allowed_type:
                print('Skipped: Invalid filetype.')
            elif not allowed_domains:
                print('Skipped: Invalid domain.')
            else:
                save_to = '{0}\\{1}.{2}'.format(folder, reddit_data.link_title(i), reddit_data.get_filetype(i))
                with urllib.request.urlopen(reddit_data.get_full_url(i)) as in_stream, open(save_to, 'wb') as out_file:
                    copyfileobj(in_stream, out_file) 
                print('Saved new image as {0}, in folder "{1}"'.format(save_to.split('\\')[-1], save_to.split('\\')[-2]))
            i += 1
            sleep(2) # limit speed in accordance with the reddit api
    except IndexError:
        print('No data left in .json file.')
    except KeyboardInterrupt:
        exit()

main()
