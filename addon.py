#!/usr/bin/env python
import sys, urllib, urllib2, cookielib, xbmcgui, xbmcaddon, simplejson as json

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__cwd__ = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__icon__ = __addon__.getAddonInfo('icon')

from xbmcapi import XBMCSourcePlugin

cookie_filename = __profile__+'chan.cookie'
cookieJar = cookielib.LWPCookieJar(cookie_filename)

if os.access(cookie_filename, os.F_OK):
	cookieJar.load(ignore_discard=True)

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.11) Gecko/20101012 Firefox/3.6.11'),]
plugin = XBMCSourcePlugin()

def home():
	user = serverRequest('pwg.session.getStatus')
	if (user['status'] == 'webmaster') or (user['status'] == 'admin') or (user['status'] == 'administrator') :
		opts['Synchronize Server'] = 'sync'
	for key in opts.iteritems():
		listitem = xbmcgui.ListItem(key[0])
		plugin.addDirectoryItem(url='%s/%s' % (plugin.root, key[1]), listitem=listitem, isFolder=True)
	plugin.endOfDirectory()	

def serverRequest(board = '', method = '', thread = False, extraData = []):
	url = 'http://a.4cdn.org/'
	if(board != ''):
		url += '%s/' % (board)
	if(thread):
		url += 'thread/'		
	if(method != ''):
		url += '%s.json' % (method)
	req = urllib2.Request(url)
	try:
		conn = urllib2.urlopen(req)
		response = json.loads(conn.read())
	except:
		conn.close()
		# xbmcgui.Dialog().ok(__addonname__, 'There was an error retrieving data from the server')
		die('There was an error retrieving data from the server')
	else:
		conn.close()
		return response

def populateHomeDirectory():
	array = serverRequest('','boards')['boards']
	for obj in array:
		if(obj['ws_board'] == 0 and plugin.getSetting('incl_nsfw') == 'false') :
			pass
		else :
			commands = []

			# commands.append(( 'Jump to page', 'RunScript('+__cwd__+'/page_jump.py,'+plugin.root+','+obj['board']+')', ))
			commands.append(( 'Jump to page', 'XBMC.Container.Update(%s/%s/jump)' % (plugin.root, obj['board']), ))

			listitem = xbmcgui.ListItem('/'+obj['board']+'/ - '+obj['title'], iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='%s/%s/1' % (plugin.root, obj['board']), listitem=listitem, isFolder=True)
	plugin.endOfDirectory()

def populateBoardDirectory(board,page):
	pages = serverRequest(board,'catalog')
	try:
		currentPage = pages[int(page) - 1]['threads']
	except :
		# xbmcgui.Dialog().ok(__addonname__, 'Invalid page selection')
		die('Invalid page selection')
	else:	
		for obj in currentPage:
			try:
				label = obj['sub']
			except:
				label = obj['com']
			else:
				pass
			try:
				thumb = 'https://1.t.4cdn.org/%s/%ss.jpg' % (board,obj['tim'])
			except :
				listitem = xbmcgui.ListItem(label)
			else:
				listitem = xbmcgui.ListItem(label,iconImage=thumb,thumbnailImage=thumb)
			plugin.addDirectoryItem(url='%s/%s/thread/%s' % (plugin.root, board,obj['no']), listitem=listitem, isFolder=True)
		if(len(pages) != int(page)) :
			nextPageNum = int(page) + 1
			listitem = xbmcgui.ListItem('> Next Page (%s)' % (nextPageNum), iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
			plugin.addDirectoryItem(url='%s/%s/%s' % (plugin.root, board, nextPageNum), listitem=listitem, isFolder=True)		
		plugin.endOfDirectory()

def populatePostDirectory(board,thread):
	posts = serverRequest(board,thread,True)['posts']
	for post in posts:
		try:
			filename = post['filename']
			thumb = 'https://1.t.4cdn.org/%s/%ss.jpg' % (board,post['tim'])
			image = 'https://i.4cdn.org/%s/%s%s' % (board,post['tim'],post['ext'])
		except:
			pass
		else:
			listitem = xbmcgui.ListItem(filename,iconImage=thumb)
			plugin.addDirectoryItem(url=image, listitem=listitem)
	plugin.endOfDirectory()

def die(alert=False):
	if alert:
		xbmcgui.Dialog().ok(__addonname__, alert)
	raise SystemExit(0)	

if plugin.path:
	split = plugin.path.split('/')
	if(split[1] == 'thread') :
		populatePostDirectory(split[0],split[2])
	else :
		if(split[1] == 'jump') :
			result = xbmcgui.Dialog().numeric(0, 'Choose a Page')
			populateBoardDirectory(split[0],result)
		else :
			populateBoardDirectory(split[0],split[1])
else:
	populateHomeDirectory()

