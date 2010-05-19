import httplib
import urllib2
import xml.dom.minidom

import win32con
import wx

import screengrab

settings = {
            'copyUrlToClipboard': '0',
            'userId': '',
            'enableToastNotifications': '1',
            'imageFormat': 'PNG',
            'imageQuality': 'Very High',
            'screenshotSaveDirectory': '',
            'hotKey1Modifier': 'Shift',
            'hotKey1KeyCode': 'F10',
            'hotKey2Modifier': 'Shift',
            'hotKey2KeyCode': 'F11'
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

UPDATE_CHECK_URL = 'http://dl.getdropbox.com/u/521887/dropbox_screen_grabber/latest'

def loadSettings():
    config = wx.Config('dropbox_screen_grabber')
    
    settings['copyUrlToClipboard'] = config.Read('copy_url_to_clipboard', '0')
    settings['userId'] = config.Read('user_id', '')
    settings['enableToastNotifications'] = config.Read('enable_toast_notifications', '1')
    settings['imageFormat'] = config.Read('image_format', 'PNG')
    settings['imageQuality'] = config.Read('image_quality', 'Very High')
    
    settings['screenshotSaveDirectory'] = config.Read('screenshot_save_directory', '')
    
    settings['hotKey1Modifier'] = config.Read('hot_key1_modifier', 'Shift')
    settings['hotKey1KeyCode'] = config.Read('hot_key1_key_code', 'F10')
    settings['hotKey2Modifier'] = config.Read('hot_key2_modifier', 'Shift')
    settings['hotKey2KeyCode'] = config.Read('hot_key2_key_code', 'F11')
  
def saveSettings(settings):
    config = wx.Config('dropbox_screen_grabber')
    
    config.Write('copy_url_to_clipboard', '1' if settings['copyUrlToClipboard'] else '0')
    config.Write('user_id', str(settings['userId']))
    config.Write('enable_toast_notifications', '1' if settings['enableToastNotifications'] == True else '0')
    config.Write('image_format', str(settings['imageFormat']))
    config.Write('image_quality', str(settings['imageQuality']))
    
    saveDirectory = settings['screenshotSaveDirectory']
    saveDirectory = saveDirectory[len(screengrab.publicFolderPath) + 1:] if saveDirectory.find(screengrab.publicFolderPath) != -1 and len(saveDirectory) > len(screengrab.publicFolderPath) else None
    config.Write('screenshot_save_directory', saveDirectory if saveDirectory != None else '') # only path relative to Dropbox public directory is allowed
    
    config.Write('hot_key1_modifier', str(settings['hotKey1Modifier']))
    config.Write('hot_key1_key_code', str(settings['hotKey1KeyCode']))
    config.Write('hot_key2_modifier', str(settings['hotKey2Modifier']))
    config.Write('hot_key2_key_code', str(settings['hotKey2KeyCode']))
    
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