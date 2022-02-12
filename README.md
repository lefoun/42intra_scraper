# 42intra_scraper


Scrap the 42 Intranet's elearning videos in a single click.

### Why you would want to use it ?

1. Adjust speed at your convenience. (The intra doesn't allow this)
2. Working in a remote location where internet is hit or miss ? Download what you need and you'll have it in your computer.
3. Have a friend that is freeze and can't access the intra's resources ? You can download the videos, compress them and send them via drive. 


### How to use it:

```
git clone git@github.com:Dovalich/42intra_scraper.git
```
```
pip3 install -r requirements.txt
```
```
python3 intra_scraper.py
```

And then all you have to do is follow the instructions that the program gives you, that is:

1. enter your 42 intranet username
2. enter your 42 intranet password
3. enter the elearning link you want to scrap for example https://elearning.intra.42.fr/tags/38/notions

Here's a short Tutorial gif:

![tutorial_gif](https://github.com/Dovalich/42intra_scraper/blob/main/assets/intra_scraper_tuto.gif)

## How does it work ?

It's fairly simple.

1. The program makes a post request to the intranet using your logins (via the requests module).

2. Once logged-in, it recursively searches for any links that are in the middle of the page (the ones that contain videos)

3. Once it finds a video link it downloads it based on the video quality you chose (SD or HD)

(there are some steps that I ommited in the explanation like getting the authenticity token using a get request or creating a directory for each section but they are not relevant... Oops I justed explained them)

### Note 

As you can see in the code I don't store your user name and password. In fact I only use them once to login. But be careful when using these types of scripts. You should always read the source code before giving away sensitive information.


If you have feedback on the code please let me know! 👨‍🎓

And feel free to use it however you want.
