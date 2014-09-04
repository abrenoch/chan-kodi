#!/usr/bin/env python
import sys, xbmcgui, json
try:
	json_data = open(sys.argv[2])
	data = json.load(json_data)	
	json_data.close()
except:
	data = {};
else:
	pass
if sys.argv[1] == 'remove':
	for thread in data['bmthreads']:
		if thread['number'] == sys.argv[3]:
			data['bmthreads'].remove(thread)
			xbmc.executebuiltin('Notification(Chan Browser, Thread bookmark removed, 5000, '+sys.argv[4]+')')
			xbmc.executebuiltin('XBMC.Container.Refresh()')
	with open(sys.argv[2], 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()
else:
	defaultTitle = sys.argv[4]+' - /'+sys.argv[3]+'/'
	result = xbmcgui.Dialog().input('Thread Name',defaultTitle)	
	with open(sys.argv[2], 'w') as outfile:
		new_thread = {'board':sys.argv[3],'number':sys.argv[4],'name':result,'thumb':sys.argv[5]}
		try:
			bmthreads = data['bmthreads']
		except:
			bmthreads = []
		else:
			pass
		cont = True
		for thread in bmthreads:
			if thread['number'] == sys.argv[4]:
				cont = False
		if cont:
			bmthreads.append(new_thread)
			data['bmthreads'] = bmthreads
			xbmc.executebuiltin('Notification(Chan Browser, Thread bookmarked successfully, 5000, '+sys.argv[6]+')')
		else:
			xbmc.executebuiltin('Notification(Chan Browser, Thread already bookmarked, 5000, '+sys.argv[6]+')')
		json.dump(data, outfile)
		outfile.close()
