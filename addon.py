#!/usr/bin/env python
import urllib, urllib.request, simplejson as json, traceback, os
import xbmcgui, xbmcaddon, xbmcvfs, xbmc
from xbmcapi import XBMCSourcePlugin

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__profile__ = xbmcvfs.translatePath( __addon__.getAddonInfo('profile') )
__cwd__ = xbmcvfs.translatePath( __addon__.getAddonInfo('path') )
__icon__ = __addon__.getAddonInfo('icon')
json_filename = __profile__+'data.json'

plugin = XBMCSourcePlugin()

def serverRequest(board = '', method = '', thread = False, extraData = []):
	url = 'https://a.4cdn.org/'
	if(board != ''):
		url += '%s/' % (board)
	if(thread):
		url += 'thread/'		
	if(method != ''):
		url += '%s.json' % (method)
	try:
		conn = urllib.request.urlopen(url)
		response = json.loads(conn.read())
	except:
		if(conn):
			conn.close()
		traceback.print_stack()
		die('There was an error retrieving data from the server: %s' % (url))
	else:
		return response

def populateHomeDirectory():
	array = serverRequest('','boards')['boards']
	listitem = xbmcgui.ListItem('> Bookmarks')
	listitem.setArt({ 'icon': 'DefaultFolder.png', 'thumbnail' : 'DefaultFolder.png' })
	plugin.addDirectoryItem(url='plugin://%s/bmarks' % (plugin.root), listitem=listitem, isFolder=True)	
	for obj in array:
		if(obj['ws_board'] == 0 and plugin.getSetting('incl_nsfw') == 'false') :
			pass
		else :
			commands = []
			commands.append(( 'Jump to page', 'XBMC.Container.Update(plugin://%s/%s/jump)' % (plugin.root, obj['board']), ))
			listitem = xbmcgui.ListItem('/'+obj['board']+'/ - '+obj['title'])
			listitem.setArt({ 'icon': 'DefaultFolder.png', 'thumbnail' : 'DefaultFolder.png' })
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='plugin://%s/%s/1' % (plugin.root, obj['board']), listitem=listitem, isFolder=True)
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
				listitem = xbmcgui.ListItem(label)
				listitem.setArt({ 'icon': thumb, 'thumbnail' : thumb })
			commands.append(( 'Bookmark thread', 'XBMC.RunScript(%s, add, %s, %s, %s, %s, %s)' % (os.path.join(__cwd__, 'resources', 'lib', 'bmark_thread.py'), json_filename, board, obj['no'], thumb, __icon__), ))
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='plugin://%s/%s/thread/%s' % (plugin.root, board, obj['no']), listitem=listitem, isFolder=True)
		if(len(pages) != int(page)) :
			nextPageNum = int(page) + 1
			listitem = xbmcgui.ListItem('> Next Page (%s)' % (nextPageNum))
			listitem.setArt({ 'icon': "DefaultFolder.png", 'thumbnail' : "DefaultFolder.png" })
			plugin.addDirectoryItem(url='plugin://%s/%s/%s' % (plugin.root, board, nextPageNum), listitem=listitem, isFolder=True)		
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
			listitem = xbmcgui.ListItem(filename)
			listitem.setArt({ 'icon': thumb })
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
			commands.append(( 'Remove bookmark', 'XBMC.RunScript(%s, remove, %s, %s, %s)' % (os.path.join(__cwd__, 'resources', 'lib', 'bmark_thread.py'), json_filename, bmark['number'],  __icon__), ))
			listitem = xbmcgui.ListItem(bmark['name'])
			listitem.setArt({ 'icon': bmark['thumb'] })
			listitem.addContextMenuItems(commands)
			plugin.addDirectoryItem(url='plugin://%s/%s/chkthread/%s' % (plugin.root, bmark['board'], bmark['number']), listitem=listitem, isFolder=True)
		plugin.endOfDirectory()

def die(alert=False):
	if alert:
		xbmcgui.Dialog().ok(__addonname__, alert)
	raise SystemExit(0)	

if plugin.path != 'plugin:///':
	split = plugin.path.split('/')
	# hacky way to remove plugin://
	split.pop(0)
	split.pop(0)
	split.pop(0)
	if(split[0] == 'bmarks') :
		populateBookmarkDirectory()	
	elif(split[1] == 'thread') :
		populatePostDirectory(split[0],split[2])
	elif(split[1] == 'chkthread') :
		try:
			populatePostDirectory(split[0],split[2])
		except:
			xbmcgui.Dialog().ok(__addonname__, 'Thread has expired and will be removed from bookmarks')
			xbmc.executebuiltin('XBMC.RunScript(%s, remove, %s, %s, %s)' % (os.path.join(__cwd__, 'resources', 'lib', 'bmark_thread.py'), json_filename, split[2],  __icon__))	
	else :
		if(split[1] == 'jump') :
			result = xbmcgui.Dialog().numeric(0, 'Choose a Page')
			populateBoardDirectory(split[0],result)
		else :
			populateBoardDirectory(split[0],split[1])
else:
	populateHomeDirectory()
