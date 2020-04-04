#!/usr/bin/env python3

# Imports
import praw
import pandas as pd
import datetime as dt
import wget
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
import duplicates as dupes

# Gets Reddit API Creds
import configparser
config = configparser.ConfigParser()
config.read('apiCreds.config')


# Global Variables
reddit = praw.Reddit(client_id=config.get("REDDITAPI","client_id"),
					 client_secret=config.get("REDDITAPI","client_secret"),
					 user_agent=config.get("REDDITAPI","user_agent"),
					 username=config.get("REDDITAPI","username"),
					 password=config.get("REDDITAPI","password"))
subredditName = ''
redditorName = ''
decidedName = ''
linkList = []
error404 = 'received 404 HTTP response'
errorRedirect = 'Redirect to /subreddits/search'
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
headers = {'User-Agent': user_agent}
formatTypes = ['jpg','png','jpeg','gif']
albumTypes = ['a','album','gallery','show']
rootDownloadPath = '/Users/trusty/Pictures/'


# Functions
def checkUserExists(grabbedName):
	global redditorName
	grabbedName = grabbedName.strip()
	u = reddit.redditor(grabbedName)
	uCheck = ''

	try:
		u = u.id
	except Exception as e:
		uCheck = str(e)

	if u != '' and uCheck != error404 and uCheck != errorRedirect:
		redditorName = grabbedName.strip()
		print('Redditor name set to: '+redditorName)
	else:
		print('Couldn\'t find user '+grabbedName)


def checkSubredditExists(grabbedName):
	global subredditName
	grabbedName = grabbedName.strip()
	r = reddit.subreddit(grabbedName)
	rCheck = ''
	
	try:
		r = r.id
	except Exception as e:
		rCheck = str(e)

	if r != '' and rCheck != error404 and rCheck != errorRedirect:
		subredditName = grabbedName
		print('Subreddit name set to: '+subredditName)
	else:
		print('Couldn\'t find subreddit '+grabbedName)


def AskHowManyImages():
	global downloadLimit
	print(f'Set your download limit: \neg: 100 or month, year, hour')
	downloadLimit = input().strip()


def getUserInput():
	global subredditName, redditorName, userInput, decidedName
	print('''
+++ Reddit scraper +++
Takes reddit URL or name and arguments: User /u or Subreddit /r
Enter:
		''')

	userInput = str(input()).lower().strip()
	listUserInput = userInput.split('/')

	if 'r' in listUserInput:
		indexr = listUserInput.index('r') +1
		checkSubredditExists(listUserInput[indexr])
		decidedName = subredditName
		AskHowManyImages()
		print('\nChecking subreddit '+subredditName)
		subreddit(decidedName)
	elif 'user' in listUserInput:
		indexr = listUserInput.index('user') +1
		checkUserExists(listUserInput[indexr])
		decidedName = redditorName
		redditor(decidedName)
		print('\nChecking redditor '+redditorName)

	# Checking if specified user or subreddit with /u /r
	elif len(listUserInput) == 2:
		if listUserInput[-1] == 'u':
			checkUserExists(listUserInput[0])
			decidedName = redditorName
			redditor(decidedName)
			print('\nChecking redditor '+redditorName)
		elif listUserInput[-1] == 'r':
			checkSubredditExists(listUserInput[0])
			decidedName = subredditName
			AskHowManyImages()
			print('\nChecking subreddit '+subredditName)
			subreddit(decidedName)
		else:
			print('''Incorrect argument specified.
User ....... = /u
Subreddit .. = /r''')
			getUserInput()
	elif len(listUserInput) == 1:
		checkUserExists(listUserInput[0])
		checkSubredditExists(listUserInput[0])

		if redditorName == '' and subredditName == '':
			print('\nSorry, that is neither a user or subreddit.\nTry again.')
			getUserInput()
		elif redditorName == subredditName:
			print('Is this a user or subreddit?\n\n1 = User\n2 = Subreddit')
			try:
				redditType = int(input())
				if redditType == 1:
					decidedName = redditorName
					redditor(decidedName)
					print('\nChecking SubReddit '+redditorName)
				elif redditType == 2:
					decidedName = subredditName
					AskHowManyImages()
					print('\nChecking subreddit '+subredditName)
					subreddit(decidedName)
			except ValueError:
				print('Enter 1 or 2')
		elif redditorName != '' and subredditName == '':
			decidedName = redditorName
			redditor(decidedName)
			print('\nChecking SubReddit '+redditorName)
		elif redditorName == '' and subredditName != '':
			decidedName = subredditName
			AskHowManyImages()
			print('\nChecking subreddit '+subredditName)
			subreddit(decidedName)
		else:
			print('Big Error: Couldn\'t find '+userInput)
	else:
		print('Not a reddit link. Or something went wrong with \n'+userInput)


def gallery(postLink):
	response = requests.get(postLink, headers=headers)
	if response.status_code == 200:
		print(postLink+'\nFinding pictures in album!')
		if 'imgur' in postLink.split('.'):
			album = requests.get(postLink)
			soup = BeautifulSoup(album.content, 'html.parser')
			postImageContainers = soup.findAll('div',attrs={'class':'post-image-container'})
			for i in postImageContainers:
				imgur = 'https://i.imgur.com/'
				jpg = '.jpg'
				builtLink = str(imgur+str(i.get('id'))+jpg)
				linkList.append(builtLink)
				print('Adding >> '+builtLink)
		elif 'vidble' in postLink.split('.'):
			album = requests.get(postLink)
			soup = BeautifulSoup(album.content, 'html.parser')
			postImageContainers = soup.findAll('img', src=True)
			for i in postImageContainers:
				rSrc = i.get('src')
				explodeSrcSlash = rSrc.split('/')
				explodeSrcDot = rSrc.split('.')
				imageID = explodeSrcSlash[-1]
				imageID = imageID[:10]
				vidble = 'https://www.vidble.com/'
				builtLink = vidble+imageID+'.'+explodeSrcDot[-1]
				ignore = ['https://www.vidble.com/vidble_log.png']
				if builtLink not in ignore:
					linkList.append(builtLink)
					print('Adding >> '+builtLink)
				else:
					print('Ignoring because logo...')
	else:
		print('Whoops! Looks like that link is dead \n'+postLink)


def ifImgur(postLink):
	postLinkr = postLink
	postLink = postLink.split('/')
	imageLink = ''

	if 'imgur.com' in postLink:
		if postLink[3] in albumTypes:
			print('Found an album!')
			gallery(postLinkr)
		else:
			imageLink = 'https://i.imgur.com/'+postLink[-1]+'.jpg'
			print('Adding >> '+imageLink)
			linkList.append(imageLink)
	elif 'i.imgur.com' in postLink:
		if postLinkr[-4:] == "gifv":
			imageLink = postLinkr[:-4]+'mp4'
			print('Adding >> '+imageLink)
			linkList.append(imageLink)
		else:
			imageLink = postLinkr
			print('Adding >> '+imageLink)
			linkList.append(imageLink)
	elif 'i.redd.it' in postLink:
		imageLink = postLinkr
		print('Adding >> '+imageLink)
		linkList.append(imageLink)
	elif 'www.vidble.com' in postLink:
		if (postLink[-1])[-3:] not in formatTypes:
			print('Found an album!')
			gallery(postLinkr)
		else:
			imageLink = postLinkr
			print('Adding >> '+imageLink)
			linkList.append(imageLink)
	else:
		print('Not a picture >> '+postLinkr)


def redditor(name):
	for submission in reddit.redditor(name).submissions.new(limit=None):
		ifImgur(submission.url)


def subreddit(name):
	subreddit = reddit.subreddit(name)
	print(f'download limit set to: {downloadLimit}')


	if downloadLimit.isdigit():
		for submission in subreddit.top(limit=int(downloadLimit)):
			ifImgur(submission.url)
	else:
		if downloadLimit == 'all':
			setDownloadLimit = 'all'
		elif downloadLimit == 'year':
			setDownloadLimit = 'year'
		elif downloadLimit == 'month':
			setDownloadLimit = 'month'
		elif downloadLimit == 'week':
			setDownloadLimit = 'week'
		elif downloadLimit == 'day':
			setDownloadLimit = 'day'
		elif downloadLimit == 'hour':
			setDownloadLimit = 'hour'

		for submission in subreddit.top(setDownloadLimit):
			ifImgur(submission.url)


def downloadImages(imageList):

	downloadPath = Path(str(rootDownloadPath+decidedName))
	storedDuplicateListPath = os.path.join(downloadPath,'DuplicateList.txt')
	storedDuplicatesList = []

	if os.path.exists(storedDuplicateListPath):
		print('Found list of known duplicates')
		storedDuplicatesFile = open(storedDuplicateListPath, 'r')
		for eachDupe in storedDuplicatesFile:
			eachDupe.split('/')
			oldDupe = eachDupe[-1]
			storedDuplicatesList.append(eachDupe)
		imagesToRemoveList = [newLink for oldFile in storedDuplicatesList for newLink in imageList if oldFile in newLink]
		imageList = dupes.Difference(imageList,imagesToRemoveList)

	print('Did not find list of duplicate files')
	if len(imageList) > 0:
		print('\nCreating download list...')
		print('\nFound '+str(len(imageList))+' files.')
		downloadPath.mkdir(exist_ok=True)
		os.chdir(downloadPath)
		print('\n\nMaking directory '+str(downloadPath)+'\n')
		# Remove Duplicates
		imageList = list(dict.fromkeys(imageList))
		# Create/Appened Download List
		downloadList = open(f'{decidedName}_DownloadList.txt','a')
		count = 0
		downloaded = []
		startTime = time.time()
		for pic in imageList:
			count +=1
			fileName = pic.split('/')
			fullFilePath = os.path.join(downloadPath,str(fileName[-1]))
			downloadList.write(f'{pic}\n')
			if os.path.exists(fullFilePath) == False:
				print('\nDownloading '+str(count)+' of '+str(len(imageList))+' - '+pic)
				file = wget.download(pic, str(downloadPath))
				downloaded.append(fullFilePath)
			else:
				print('\nAlready Exists, Skipping file '+str(count)+' of '+str(len(imageList))+' - '+pic)
		downloadList.close()
		endTime = time.time()
		timeTaken = '%.2f' % (endTime - startTime)
		downloadSize = 0
		for file in downloaded:
			downloadSize += os.path.getsize(file)
		print('\n\nFinshed!')
		print('\nDownloaded '+str(len(downloaded))+' files ('+str(downloadSize/1000000)+'MB) in '+timeTaken+' seconds')
		print('\n'+str(len(imageList)-len(downloaded))+' files were skipped because they exist.')
		print('\nSaved to: \n'+str(downloadPath))
		dupes.analyse(decidedName)
	else:
		print('No pictures to download.')
	

try:
	getUserInput()
	downloadImages(linkList)
	print('\n\n\n')
except KeyboardInterrupt:
	print('\n\nExiting...\n')
