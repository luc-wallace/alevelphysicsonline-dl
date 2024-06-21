# alevelphysicsonline-dl

A video downloader for alevelphysicsonline-dl.
It downloads the website videos off vimeo.com

# How it works

This program automatically passes the site's authentication flows using a username and password.

It indexes video subpages by scraping links from the index page.

Each link is fetched and Vimeo master URLs are separated from the page.

Using the master URL, the program downloads video and audio packets one by one and combines them into one media stream using ffmpeg.

The program then categories each video and writes it to a directory structured by video topic.

# How to use

Download [ffmpeg](https://ffmpeg.org/download.html) and [Python 3.10 or higher](https://www.python.org/downloads/)

Download the dependencies:

```
pip install -r requirements.txt
```

Run the main file:

```
py main.py
```
