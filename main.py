#!/usr/bin/python3 
#Created in Python 3.3.0
#Written by Marc2540
#Version 1.1.0

import urllib.request                   #urllib.request lets me pull things from websites
from shutil import copyfileobj          #shutil lets me download the results from urlopen
import json                             #the json library lets me decode .json
from datetime import date               #datetime lets me get current date
import argparse                         #argparse lets me parse command-line arguments
from string import ascii_letters, digits #gives me a list of allowed characters for name sanitization
from unicodedata import normalize       #used for swapping accented characters with unaccented ones before sanitization
import os                               #used for creating directories

parser = argparse.ArgumentParser(description='Downloads pictures from a specified subreddit or imgur album')
parser.add_argument('-q', '--quiet', help='Disables status messages.', action='store_false')
parser.add_argument('-u', '--url', help='Accepts subreddit or imgur album url.')

flags = vars(parser.parse_args())
verbose_bool = flags['quiet']
fixed_url = flags['url']

#user specifications:
user_User_agent = 'Imgur-Reddit-Pic-Downloader v1.1.0 by u/Marc2540'
user_allowed_filetype = ['png', 'jpg', 'gif']
user_allowed_domains = ['i.imgur.com', 'imgur.com', 'i.minus.com']
user_imgur_ClientID = '112ba8a808315df'
user_number_of_loops = 25


class UrlFixing:
    """Translates the user input to a useable reddit url and pulls data."""
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
        if headers:
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            content = response.read()
            data = json.loads(content.decode("utf8"))
        else:
            response = urllib.request.urlopen(url)
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

    def check_if_deviantart(self, number):
        temp_url_split = self.data[number]['data']['url'].split('/')
        try:
            return True if temp_url_split[2][-15:] + '/' + temp_url_split[3] == '.deviantart.com/art' else False
        except IndexError:
            return False
    
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
    
    def get_image_height(self, number):
        image_height = self.image_info[number]['height']
        return image_height
    
    def get_image_width(self, number):
        image_width = self.image_info[number]['width']
        return image_width


def verbose_func(*args):
    """This function holds all the print messages."""
    if verbose_bool:
        if args[0] == 'seperation_line':
            print('-'*30)
        elif args[0] == 'self_post':
            print('Reddit: Skipped - Self-post.')
        elif args[0] == 'filetype':
            print('Reddit: Skipped - Invalid filetype.')
        elif args[0] == 'domain':
            print('Reddit: Skipped - Invalid domain.')
        elif args[0] == 'index_error':
            print('Possible error: No data left in .json file.')
        elif args[0] == 'image save':
            save_to = args[1]
            print('Reddit: Saved new image as "{0}", in folder "{1}"'.format(save_to.split('\\')[-1], save_to.split('\\')[-2]))
        elif args[0] == 'imgur_image_save':
            save_to = args[1]
            print('Imgur Album: Saved new image as {0}, in folder "{1}\\{2}"'.format(save_to.split('\\')[-1],
                                                                                     save_to.split('\\')[-3],
                                                                                     save_to.split('\\')[-2]))
        elif args[0] == 'imgur_album_resolution':
            width = args[1]
            height = args[2]
            print('Imgur Album: Skipped image. Resolution was {0}x{1}'.format(width, height))
        elif args[0] == 'imgur_album_skip':
            print('Reddit: Skipped imgur album.')
        elif args[0] == 'deviant save':
            save_to = args[1]
            print('Deviantart: Saved new image as "{0}", in folder "{1}"'.format(save_to.split('\\')[-1], save_to.split('\\')[-2]))

def filename_sanitization(filename):
    """Removes invalid characters in the arguments passed to it. Used for folder- and filenames."""
    if filename:
        valid_characters = str('-_.() {0}{1}'.format(ascii_letters, digits))
        clean_filename = str(normalize('NFKD', filename).encode('ASCII', 'ignore'))
        return ''.join(char for char in clean_filename if char in valid_characters)[1:]
    else:
        return 'None'
    
def fetch_image(chosen_url, imgur_album_skip, imgur_res_min_h, imgur_res_min_w):
    """
    Downloads images and saves them to a folder.
    Runs fetch_imgur_album if url is an Imgur album
    Runs fetch_deviantart if the image is hosted on DeviantArt
    """
    url_defining = UrlFixing
    
    reddit_headers = {'User-Agent' : '{}'.format(user_User_agent)}
    reddit_response = url_defining.pull_data(chosen_url, reddit_headers)
    reddit_data = RedditData(reddit_response)
    
    folder = '{0}\\{1}'.format(os.getcwd(), date.today())
    os.makedirs(folder, exist_ok=True)
    
    verbose_func('seperation_line')
    i = 0
    try:
        while i < user_number_of_loops:
            allowed_type = True if reddit_data.get_filetype(i) in user_allowed_filetype else False
            allowed_domains = True if reddit_data.get_domain(i) in user_allowed_domains else False

            if reddit_data.self_post(i):
                verbose_func('self_post')
            elif reddit_data.check_if_imgur_album(i):
                if not imgur_album_skip:
                    imgur_url = reddit_data.get_imgur_api_url(i)
                    fetch_imgur_album(imgur_url, imgur_res_min_h, imgur_res_min_w)
                else:
                    verbose_func('imgur_album_skip')
            elif reddit_data.check_if_deviantart(i):
                print(reddit_data.get_full_url(i))
                fetch_deviantart(reddit_data.get_full_url(i), folder, i)
            elif not allowed_type:
                verbose_func('filetype')
            elif not allowed_domains:
                verbose_func('domain')
            else:
                save_to = '{0}\\{1} - {2}.{3}'.format(folder, i, reddit_data.link_title(i)[:40], reddit_data.get_filetype(i))
                with urllib.request.urlopen(reddit_data.get_full_url(i)) as in_stream, open(save_to, 'wb') as out_file:
                    copyfileobj(in_stream, out_file)
                verbose_func('image save', save_to)
            i += 1
    except IndexError:
        verbose_func('index_error')
    except KeyboardInterrupt:
        exit()

def fetch_imgur_album(imgur_url, min_h, min_w):
    """Handles saving of imgur albums with the imgur api."""
    url_defining = UrlFixing
    
    imgur_headers = {'Authorization' : 'Client-ID {}'.format(user_imgur_ClientID)}
    folder = '{0}\\{1}'.format(os.getcwd(), date.today())
    
    if not imgur_url[:29] == 'https://api.imgur.com/3/album':
        imgur_api_url = 'https://api.imgur.com/3/album/{}.json'.format(imgur_url.split('/')[-1])
        imgur_url = imgur_api_url
    
    imgur_response = url_defining.pull_data(imgur_url, imgur_headers)
    imgur_data = ImgurData(imgur_response)
    verbose_func('seperation_line')
    
    with open('{0}\\info.txt'.format(imgur_data.get_folder(folder)), 'a') as f:
        f.write('\nTitle: {0}\nUploader: {1}\nAlbum link: {2}\nNumber of images: {3}\nDescription: {4}'.format(imgur_data.valid_title,
                                                                                                               imgur_data.uploader,
                                                                                                               imgur_data.album_link,
                                                                                                               imgur_data.images_count,
                                                                                                               imgur_data.description))
    imgur_i = 0
    while imgur_i < imgur_data.images_count:
        if min_h <= imgur_data.get_image_height(imgur_i) and min_w <= imgur_data.get_image_width(imgur_i):
            imgur_save_to = '{0}\\{1} - {2}'.format(imgur_data.get_folder(folder),imgur_i,
                                                    imgur_data.get_image_link(imgur_i).split('/')[-1])
            with urllib.request.urlopen(imgur_data.get_image_link(imgur_i)) as in_stream, open(imgur_save_to, 'wb') as out_file:
                copyfileobj(in_stream, out_file)
            verbose_func('imgur_image_save', imgur_save_to)
        else:
            verbose_func('imgur_album_resolution', imgur_data.get_image_width(imgur_i), imgur_data.get_image_height(imgur_i))
        imgur_i += 1
    verbose_func('seperation_line')

def fetch_deviantart(deviant_url, folder, number):
    """Handles saving of images hosted on DeviantArt"""
    url_defining = UrlFixing

    deviant_api_url = 'http://backend.deviantart.com/oembed?url={0}'.format(deviant_url)
    deviant_response = url_defining.pull_data(deviant_api_url, None)

    try:
        deviant_final_url = deviant_response['url']
        deviant_filetype = deviant_final_url[-3:]
        deviant_title = deviant_response['title']
    except KeyError:
        deviant_final_url = deviant_response['fullsize_url']
        deviant_filetype = deviant_final_url[-3:]
        deviant_title = deviant_response['title']

    save_to = '{0}\\{1} - {2}.{3}'.format(folder, number, deviant_title[:40], deviant_filetype)
    with urllib.request.urlopen(deviant_final_url) as in_stream, open(save_to, 'wb') as out_file:
        copyfileobj(in_stream, out_file)
    verbose_func('deviant save', save_to)

def main():
    """Takes care of prompting the user for all needed info, then runs fetch_image"""
    url_defining = UrlFixing
    ask_for_subreddit = None
    ask_for_modifiers = None
    ask_for_modifiers_specific = None
    ask_for_imgur_options = None
    valid_input = False
    imgur_album_skip = False
    imgur_res_min_h = 0
    imgur_res_min_w = 0
    imgur_chosen_url = None

    if fixed_url:
        if fixed_url.split('/')[2] == 'reddit.com':
            chosen_url = fixed_url
        elif fixed_url.split('/')[2] == 'imgur.com' or fixed_url.split('/')[2] == 'api.imgur.com':
            imgur_chosen_url = fixed_url
        else:
            print('Invalid url input.')
            exit()
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

    if verbose_bool:
        while not ask_for_imgur_options:
            if imgur_chosen_url:
                ask_for_imgur_options = 'down'
            else:
                ask_for_imgur_options = input('If you hit imgur albums, do you want to skip them or download them? (skip/download) ')

            if ask_for_imgur_options == 'skip':
                imgur_album_skip = True
                valid_input = True
            elif ask_for_imgur_options in ['download', 'down']:
                imgur_album_skip = False
                imgur_res = input('Do you want to pull all the imgur album images, or add a criteria? (all/criteria) ')
                if imgur_res == 'all':
                    valid_input = True
                elif imgur_res in ['cri', 'criteria', 'res']:
                    try:
                        imgur_res_min_h = int(input('What is the minimum height of pictures that you want to download? '))
                        imgur_res_min_w = int(input('What is the minimum width of pictures that you want to download? '))
                        valid_input = True
                    except ValueError:
                        print('Not a number')

            if not valid_input:
                ask_for_imgur_options = None

    if imgur_chosen_url:
        fetch_imgur_album(imgur_chosen_url, imgur_res_min_h, imgur_res_min_w)
    else:
        fetch_image(chosen_url, imgur_album_skip, imgur_res_min_h, imgur_res_min_w)


main()