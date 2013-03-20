Imgur + Reddit picture downloader
===========================

**This program takes a reddit.com or imgur album url and loops through it to download .jpg, .png and .gif pictures.**  

### What it does:  
1. Asks for subreddit to pull images from.
2. Asks if you want to pull from the frontpage, or modify the request (i.e. get top-alltime links).
3. Asks what to do if it hits Imgur albums. (skip/only download files with a resolution larger than 'x')
2. Loops through the data and downloads all .jpg, .png and .gif images hosted on imgur.com and minus.com
3. All images are saved in a folder named YYYY-MM-DD in the current working directory.  

### Optional parameters:  
If you specify a url on startup it'll skip asking for subreddit and modifiers. Accepts both subreddit and imgur album urls.
```
python main.py -u URL
```
  
Disables status messages.
```
python main.py -q or --quiet
```

### To do:  
* ~~Add deviantArt support~~
* Update standalone build to include v1.1 changes.
