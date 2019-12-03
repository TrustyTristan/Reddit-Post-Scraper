# Reddit Image Scraper

## Idea

Scrapes specified, subreddit or user for posts linked to images.

# Use

Paste in URL, subreddit name or users name. Download.

# Setup

You will need a Reddit API account
https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps
...That's about it really.


## To Do:
- Subreddit filtering
	- Subreddits can be big...
	- Limits, now asks for a download limit
	- Maybe other things to filter by to only get good stuff
- Remove duplicate pictures based on picture - Done!
	- Hashing should not run on pictures that have already been hashed
- Work around for images requiring authentication
- Understand why you can have while true for the functions
	- Because when you do it doesn't stores old data
- Check if been downloaded before.
	- Created a log of download links, should this include date, or date downloaded...?
 	- Only check posts since that post date.
 - Look at whatever pickle is, probably better for the lists writing