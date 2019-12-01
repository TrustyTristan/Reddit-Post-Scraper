# Reddit Image Scraper

## Idea

Scrapes specified, subreddit or user for posts linked to images.

# Use

Paste in URL, subreddit name or users name. Download.

# Setup

You will need a Reddit API account
https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps
..That's about it really.


## To Do:
- Subreddit filtering
	- Subreddits can be big...
	- Limits, currently just grabs top 25
	- Maybe other things to filter by to only get good stuff
- Remove duplicate pictures based on picture
	- This should save a log, so if you try to download again, you don't download known duplicates.
- Work around for images requiring authentication
- Understand why you can have while true for the functions
	- Because when you do it doesn't stores old data