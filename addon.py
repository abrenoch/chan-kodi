#!/usr/bin/env python
import sys, urllib, urllib2, xbmcgui, xbmcaddon, simplejson as json
from xbmcapi import XBMCSourcePlugin

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__cwd__ = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__icon__ = __addon__.getAddonInfo('icon')
json_filename = __profile__+'data.json'

plugin = XBMCSourcePlugin()

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
		die('There was an error retrieving data from the server')
	else:
		conn.close()
		return response

def populateHomeDirectory():
	array = serverRequest('','boards')['boards']
	listitem = xbmcgui.ListItem('> Bookmarks', iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
	plugin.addDirectoryItem(url='%s/bmarks' % (plugin.root), listitem=listitem, isFolder=True)	
	for obj in array:
		if(obj['ws_board'] == 0 and plugin.getSetting('incl_nsfw') == 'false') :
			pass
		else :
			commands = []
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
		die('Invalid page number selected')
	else:	
		for obj in currentPage:
			commands = []
			try:
				label = obj['sub']
			except:
				label = obj['com']
			else:
				pass
			try:
				thumb = 'https://1.t.4cdn.org/%s/%ss.jpg' % (board,obj['tim'])
			except :
				thumb = None
				listitem = xbmcgui.ListItem(label)
			else:
				listitem = xbmcgui.ListItem(label,iconImage=thumb,thumbnailImage=thumb)
			commands.append(( 'Bookmark thread', 'XBMC.RunScript(special://home/addons/plugin.image.chan/resources/lib/bmark_thread.py, add, %s, %s, %s, %s)' % (json_filename, board, obj['no'], thumb), ))
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='%s/%s/thread/%s' % (plugin.root, board, obj['no']), listitem=listitem, isFolder=True)
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

def populateBookmarkDirectory():
	try:
		json_data = open(json_filename)
		data = json.load(json_data)	
		json_data.close()
		bmarks = data['bmthreads']
	except:
		die('No bookmarks found')
	else:
		if len(bmarks) == 0:
			xbmcgui.Dialog().ok(__addonname__, 'No bookmarks found')
			xbmc.executebuiltin('XBMC.Container.Update('+plugin.root+')')
			die()
		for bmark in bmarks:
			commands = []
			commands.append(( 'Remove bookmark', 'XBMC.RunScript(special://home/addons/plugin.image.chan/resources/lib/bmark_thread.py, remove, %s, %s)' % (json_filename, bmark['number']), ))
			listitem = xbmcgui.ListItem(bmark['name'],iconImage=bmark['thumb'])
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='%s/%s/chkthread/%s' % (plugin.root, bmark['board'], bmark['number']), listitem=listitem, isFolder=True)
		plugin.endOfDirectory()

def die(alert=False):
	if alert:
		xbmcgui.Dialog().ok(__addonname__, alert)
	raise SystemExit(0)	

if plugin.path:
	split = plugin.path.split('/')
	if(split[0] == 'bmarks') :
		populateBookmarkDirectory()	
	elif(split[1] == 'thread') :
		populatePostDirectory(split[0],split[2])
	elif(split[1] == 'chkthread') :
		try:
			populatePostDirectory(split[0],split[2])
		except:
			xbmcgui.Dialog().ok(__addonname__, 'Thread has expired and will be removed from bookmarks')
			xbmc.executebuiltin('XBMC.RunScript(special://home/addons/plugin.image.chan/resources/lib/bmark_thread.py, remove, %s, %s)' % (json_filename, split[2]))	
	else :
		if(split[1] == 'jump') :
			result = xbmcgui.Dialog().numeric(0, 'Choose a Page')
			populateBoardDirectory(split[0],result)
		else :
			populateBoardDirectory(split[0],split[1])
else:
	populateHomeDirectory()