import httplib
import urllib2
import xml.dom.minidom

import win32con
import wx

import screengrab

UPDATE_CHECK_URL = 'http://dl.getdropbox.com/u/521887/dropbox_screen_grabber/latest'

settings = {
			'user_id': '',
			'copy_url_to_clipboard': '0',
			'shorten_urls': '0',
			'enable_toast_notifications': '1',
			
			'image_format': 'PNG',
			'image_quality': 'Very High',
			'filename_prefix': 'screengrab',
			'screenshot_save_directory': '',
			
			'hot_key1_modifier': 'Shift',
			'hot_key1_key_code': 'F10',
			'hot_key2_modifier': 'Shift',
			'hot_key2_key_code': 'F11',
			
			'resize_image': '0',
			'resize_value': '95%',
			'auto_grab': '0',
			'auto_grab_type': 'Full screen',
			'auto_grab_interval': '60 minutes',
			}

modifiers = {
			 'Ctrl': win32con.MOD_CONTROL,
			 'Alt': win32con.MOD_ALT,
			 'Shift': win32con.MOD_SHIFT
			}
keyCodes = {
			'F10': win32con.VK_F10,
			'F11': win32con.VK_F11,
			'F12': win32con.VK_F12
			}

def loadSettings():
	config = wx.Config('dropbox_screen_grabber')
	
	for key, value in settings.iteritems():
		settings[key] = config.Read(key, value)

def saveSettings(settingsNew):
	config = wx.Config('dropbox_screen_grabber')
	
	for key, value in settings.iteritems():
		value = settingsNew[key]
		
		if type(value) == bool:
			value = '1' if value else '0'
			
		config.Write(key, str(value))
	
	# Only path relative to Dropbox public directory is allowed
	saveDirectory = settingsNew['screenshot_save_directory']
	saveDirectory = saveDirectory[len(screengrab.publicFolderPath) + 1:] if saveDirectory.find(screengrab.publicFolderPath) != -1 and len(saveDirectory) > len(screengrab.publicFolderPath) else None
	
	if not saveDirectory:
		config.Write('screenshot_save_directory', '')
		
def getAutoGrabIntervalValueInMs(interval):
	"""
	Parses the input string and returns the auto-grab interval in
	milliseconds.
	"""
	interval =  int(interval[:interval.find(' ')])
	interval = (interval * 60 * 1000)
	
	return interval
	
def get_latest_version():
	request = urllib2.Request(UPDATE_CHECK_URL)
	request.add_header('User-Agent', 'Python Client - Dropbox Screen Grabber')
	opener = urllib2.build_opener()

	response = opener.open(request).read()
		
	data = xml.dom.minidom.parseString(response)
	
	version = releaseDate = downloadUrl = None
	for node in data.childNodes:
		for node2 in node.childNodes:
			if node2.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
				for node3 in node2.childNodes:
					if node3.nodeType == xml.dom.minidom.Node.TEXT_NODE:
						if node2.tagName == 'version':
							version = node3.data
						elif node2.tagName == 'release-date':
							releaseDate = node3.data
						elif node2.tagName == 'url-download':
							downloadUrl = node3.data

	return (version, releaseDate, downloadUrl)