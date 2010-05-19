# -*- coding: utf-8 -*-
#
# Name: Dropbox Screen Grabber
# Description: Simple application for capturing screenshots of the whole desktop or
# the currently active window and saving it to the Dropbox public folder.
# Author: Tomaž Muraus (http://www.tomaz-muraus.info)
# Version: 1.4
# License: GPL

# Requirements:
# - Windows (tested on Windows XP, Vista and 7)
# - Microsoft Visual C++ 2008 runtime (http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en)
# - Python >= 2.6 (< 3.0)
# - wxPython (http://www.wxpython.org/)
# - Python for Windows extensions - pywin32 (http://sourceforge.net/projects/pywin32/)
# - Python Imaging Library - PIL (http://www.pythonware.com/products/pil/)
#
# Known problems:
# - If you are using multi-monitor setup you can only capture screenshot of the primary desktop
#
# Thanks to:
# - Steve H. for making PythonScriptToDisplayConfig script which reads the Dropbox configuration data (http://wiki.getdropbox.com/DropboxAddons/PythonScriptToDisplayConfig)
# - Dropbox team for making the best syncing tool

__version__ = "1.5"

import os
import sys

import wx
import wx.lib.agw.toasterbox as TB
import wx.lib.agw.supertooltip as STT

from wx import xrc

try:
	import screengrab
except IOError:
	# Dropbox database not found, show the error and exit the application
	application = wx.App()
	wx.MessageBox("No Dropbox installation detected", "ERROR", wx.ICON_ERROR)
	application.MainLoop()
	sys.exit(1)
import settings

# Application name and other IDs constants
APP_NAME = 'Dropbox Screen Grabber'

ID_HOT_KEY_FULL = 1
ID_HOT_KEY_ACTIVE = 2

ID_TAKE_SCREEN_FULL = 1
ID_TAKE_SCREEN_ACTIVE = 2
ID_SETTINGS = 3
ID_ABOUT = 4
ID_UPDATE_CHECK = 5
ID_EXIT = 6

class DropboxScreenGrabberFrame(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, parent, id, title, size = (1, 1))
		
		# Load the user settings
		settings.loadSettings()
		
		# Register the system-wide hot-keys and create the taskbar icon
		self.registerHotKeys()
		self.taskBarIcon = TaskBarIcon('res/icons/application.ico')
		
		# Bind the taskbar icon menu events
		self.taskBarIcon.Bind(wx.EVT_MENU, self.handleMenuAndHotKeyEvents, id = ID_SETTINGS)
		self.taskBarIcon.Bind(wx.EVT_MENU, self.handleMenuAndHotKeyEvents, id = ID_ABOUT)
		self.taskBarIcon.Bind(wx.EVT_MENU, self.handleMenuAndHotKeyEvents, id = ID_UPDATE_CHECK)
		self.taskBarIcon.Bind(wx.EVT_MENU, self.handleMenuAndHotKeyEvents, id = ID_EXIT)
		
		self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
		
	def registerHotKeys(self):
		self.RegisterHotKey(ID_HOT_KEY_FULL, settings.modifiers[settings.settings['hotKey1Modifier']], settings.keyCodes[settings.settings['hotKey1KeyCode']])  # Shift + F10
		self.RegisterHotKey(ID_HOT_KEY_ACTIVE, settings.modifiers[settings.settings['hotKey2Modifier']], settings.keyCodes[settings.settings['hotKey2KeyCode']])  # Shift + F11
		
		# Bind the hot-key events
		self.Bind(wx.EVT_HOTKEY, self.handleMenuAndHotKeyEvents, id = ID_TAKE_SCREEN_FULL)
		self.Bind(wx.EVT_HOTKEY, self.handleMenuAndHotKeyEvents, id = ID_TAKE_SCREEN_ACTIVE)
		
	def unregisterHotKeys(self):
		self.UnregisterHotKey(ID_HOT_KEY_FULL)
		self.UnregisterHotKey(ID_HOT_KEY_ACTIVE)
		
	def showNotification(self, filePath):
		notification = NotificationBox(self, ('Screenshot has been successfully saved as %s' % (filePath)))
		notification.Play()
		
	def handleMenuAndHotKeyEvents(self, event):
		# Handles the menu and hot-key events
		eventId = event.GetId()
		
		if eventId == ID_TAKE_SCREEN_FULL:
			fileName = screengrab.grab_screenshot('true', 'true' if settings.settings['copyUrlToClipboard'] == '1' else 'false', settings.settings['userId'])
			
			if (settings.settings['enableToastNotifications']  == '1'):
				self.showNotification(os.path.join(screengrab.publicFolderPath, fileName))
		elif eventId == ID_TAKE_SCREEN_ACTIVE:
			fileName = screengrab.grab_screenshot('false', 'true' if settings.settings['copyUrlToClipboard'] == '1' else 'false', settings.settings['userId'])
			
			if (settings.settings['enableToastNotifications'] == '1'):
			   self.showNotification(os.path.join(screengrab.publicFolderPath, fileName))
		elif eventId == ID_UPDATE_CHECK:
			
			try:
				(version, releaseDate, downloadUrl) = settings.get_latest_version()
			except:
				# fetching xml or xml parsing failed (possible HTTPError or ExpatError exception)
				wx.MessageBox("Checking for updates failed, please try again later", "Update check", wx.ICON_ERROR) 
				return

			if version > __version__:
				 wx.MessageBox("New version is available (v%s), you can download it from %s" % (version, downloadUrl), "Update check", wx.ICON_INFORMATION)
			else:
				wx.MessageBox("You are using the latest version", "Update check", wx.ICON_INFORMATION)
		elif eventId == ID_ABOUT:
			description = '''%s is a simple application for capturing screenshots of the whole desktop or
the currently active window and saving it to the Dropbox public folder.

If you specify your user ID in the settings, application can also automatically copy your
public file URL to the clipboard after taking the screenshot.

Available hot-keys:

%s + %s - capture a screenshot of the whole desktop
%s + %s - capture a screenshot of the currently active window''' % (APP_NAME, settings.settings['hotKey1Modifier'], settings.settings['hotKey1KeyCode'], settings.settings['hotKey2Modifier'], settings.settings['hotKey2KeyCode'])

			info = wx.AboutDialogInfo()
			
			info.SetIcon(wx.Icon('res/bitmaps/application.png', wx.BITMAP_TYPE_PNG))
			info.SetName(APP_NAME)
			info.SetVersion(__version__)
			info.SetDescription(description)
			info.AddDeveloper('Tomaz Muraus - http://www.tomaz-muraus.info')
			wx.AboutBox(info)
		elif eventId == ID_SETTINGS:
			settingsDialog = SettingsDialog(self)
			settingsDialog.dialog.CenterOnScreen()
			
			if settingsDialog.dialog.ShowModal() == wx.ID_OK:
				# Save the settings
				userId = settingsDialog.userIdField.GetValue()
				copyUrlToClipboard = settingsDialog.copyUrlToClipboardCheckBox.GetValue() if userId != '' else False
				
				settings.saveSettings({'copyUrlToClipboard': copyUrlToClipboard, 'userId': settingsDialog.userIdField.GetValue(), \
				'enableToastNotifications': settingsDialog.notificationCheckbox.GetValue(), 'shortenURLs': settingsDialog.shortenUrlsCheckbox.GetValue(), \
				'imageFormat': settingsDialog.imageFormat.GetValue(), \
				'imageQuality': settingsDialog.imageQuality.GetValue(), 'screenshotSaveDirectory': settingsDialog.screenshotSaveLocation.GetValue(), \
				'hotKey1Modifier': settingsDialog.hotKey1Modifier.GetValue(), \
				'hotKey1KeyCode': settingsDialog.hotKey1KeyCode.GetValue(), 'hotKey2Modifier': settingsDialog.hotKey2Modifier.GetValue(), \
				'hotKey2KeyCode': settingsDialog.hotKey2KeyCode.GetValue()})
				settings.loadSettings()
				
				# Re-register the hot-keys
				self.unregisterHotKeys()
				self.registerHotKeys()
				
			settingsDialog.dialog.Destroy()
		elif eventId == ID_EXIT:
			self.Close(True)
		
	def OnCloseWindow(self, event):
		# Unregister the hot-keys (should be done automatically, but just in case...), remove the taskbar icon and destroy the main window
		self.unregisterHotKeys()
		self.taskBarIcon.RemoveIcon()
		self.taskBarIcon.Destroy()
		self.Reparent(None)
		self.Destroy()
		
		# Sometimes resources aren't released so only solution is to forcefully kill the process (yes, it's a bad idea, but the only one I can come up with atm...)
		os.system("taskkill /PID %s /f" % os.getpid())

class SettingsDialog():
	def __init__(self, parent):
		self.resource = xrc.XmlResource("res/xml/settings.xrc")
		self.dialog = self.resource.LoadDialog(parent, "SettingsDialog")
		
		# Get control references
		self.copyUrlToClipboardCheckBox = xrc.XRCCTRL(self.dialog, 'ID_COPY_URL_TO_CLIPBOARD')
		self.userIdField = xrc.XRCCTRL(self.dialog, 'ID_USERID')
		self.notificationCheckbox = xrc.XRCCTRL(self.dialog, 'ID_ENOTIFICATIONS')
		self.shortenUrlsCheckbox = xrc.XRCCTRL(self.dialog, 'ID_SHORTEN_URL')
		self.imageFormat = xrc.XRCCTRL(self.dialog, 'ID_IMAGE_FORMAT')
		self.imageQuality = xrc.XRCCTRL(self.dialog, 'ID_IMAGE_QUALITY')
		
		self.screenshotSaveLocation = xrc.XRCCTRL(self.dialog, 'ID_SAVE_DIRECTORY')
		
		self.hotKey1Modifier = xrc.XRCCTRL(self.dialog, 'ID_HOTKEY1_KEY1')
		self.hotKey1KeyCode = xrc.XRCCTRL(self.dialog, 'ID_HOTKEY1_KEY2')
		
		self.hotKey2Modifier = xrc.XRCCTRL(self.dialog, 'ID_HOTKEY2_KEY1')
		self.hotKey2KeyCode = xrc.XRCCTRL(self.dialog, 'ID_HOTKEY2_KEY2')
		
		# Dialog events
		self.dialog.Bind(wx.EVT_COMBOBOX, self.onItemSelect)
		self.dialog.Bind(wx.EVT_CHECKBOX, self.onStateChange)
		self.dialog.Bind(wx.EVT_BUTTON, self.onButtonClick, id = xrc.XRCID('ID_CHANGE_DIRECTORY'))
		
		# Fill the fields
		self.populateDialog()
		
	def populateDialog(self):
		settings.loadSettings()
		
		self.copyUrlToClipboardCheckBox.SetValue(True if settings.settings['copyUrlToClipboard'] == '1' else False)
		
		if settings.settings['copyUrlToClipboard'] == '1':
			self.userIdField.Enable(True)
		else:
			self.userIdField.Enable(False)
		
		self.userIdField.SetValue(settings.settings['userId'])
		self.notificationCheckbox.SetValue(True if settings.settings['enableToastNotifications'] == '1' else False)
		self.shortenUrlsCheckbox.SetValue(True if settings.settings['shortenURLs'] == '1' else False)
		self.imageFormat.SetStringSelection(settings.settings['imageFormat'])
		
		if settings.settings['imageFormat'] == 'JPEG':
			self.imageQuality.Enable(True)
		else:
			self.imageQuality.Enable(False)
			
		self.imageQuality.SetStringSelection(settings.settings['imageQuality'])
		
		self.screenshotSaveLocation.SetValue(os.path.join(screengrab.publicFolderPath, settings.settings['screenshotSaveDirectory']))
		
		self.hotKey1Modifier.SetStringSelection(settings.settings['hotKey1Modifier'])
		self.hotKey1KeyCode.SetStringSelection(settings.settings['hotKey1KeyCode'])
		self.hotKey2Modifier.SetStringSelection(settings.settings['hotKey2Modifier'])
		self.hotKey2KeyCode.SetStringSelection(settings.settings['hotKey2KeyCode'])
		
	def chooseSaveLocationDirectory(self):
		dialog = wx.DirDialog(None, "Please choose the directory where the screenshots will be saved (relative to Dropbox public directory):", style = 1, defaultPath = self.screenshotSaveLocation.GetValue())
		
		if dialog.ShowModal() == wx.ID_OK:
			selectedDirectory = dialog.GetPath();
		else:
			selectedDirectory = None
			
		dialog.Destroy()
		return selectedDirectory

	def onStateChange(self, event):
		if event.GetEventObject() == self.copyUrlToClipboardCheckBox:
			self.userIdField.Enable(True if self.copyUrlToClipboardCheckBox.IsChecked() else False)
			self.shortenUrlsCheckbox.Enable(True if self.copyUrlToClipboardCheckBox.IsChecked() else False)
		
	def onItemSelect(self, event):
		# Same hot-key can't be used for both actions
		if self.hotKey1Modifier.GetValue() == self.hotKey2Modifier.GetValue() and self.hotKey1KeyCode.GetValue() == self.hotKey2KeyCode.GetValue():
			wx.MessageBox("Both actions can't have same hot-keys", "ERROR")
			
			# Re-populate the dialog with the saved data
			self.populateDialog()
 
		if event.GetEventObject() == self.imageFormat:
			self.imageQuality.Enable(True if self.imageFormat.GetValue() == 'JPEG' else False)
			
	def onButtonClick(self, event):
		directory = self.chooseSaveLocationDirectory()
		
		if directory != None:
			if directory.count(screengrab.publicFolderPath) == 1:
				self.screenshotSaveLocation.SetValue(directory)
			else:
				 wx.MessageBox("This directory must be located inside the Dropbox Public directory", "ERROR", wx.ICON_INFORMATION)
		
	def OnClose(self, event):
		self.Destroy()
		
class TaskBarIcon(wx.TaskBarIcon):
	def __init__(self, icon):
		wx.TaskBarIcon.__init__(self)
		
		self.icon = wx.Icon(icon, wx.BITMAP_TYPE_ICO)
		self.SetIcon(self.icon, '')

	def CreatePopupMenu(self):
		# Create the taskbar icon popup menu
		menu = wx.Menu()
		
		item = wx.MenuItem(menu, ID_SETTINGS, "&Settings")
		item.SetBitmap(wx.Bitmap("res/bitmaps/settings.png"))
		menu.AppendItem(item)
		
		item = wx.MenuItem(menu, ID_ABOUT, "&About")
		item.SetBitmap(wx.Bitmap("res/bitmaps/about.png"))
		menu.AppendItem(item)
		
		item = wx.MenuItem(menu, ID_UPDATE_CHECK, "&Update check")
		item.SetBitmap(wx.Bitmap("res/bitmaps/update_check.png"))
		menu.AppendItem(item)
		
		item = wx.MenuItem(menu, ID_EXIT, "&Exit")
		item.SetBitmap(wx.Bitmap("res/bitmaps/exit.png"))
		menu.AppendItem(item)

		return menu
		
class NotificationBox(TB.ToasterBox):
	def __init__(self, parent, text, pauseTime = 2800, size = (280, 80), tbstyle = TB.TB_SIMPLE, windowstyle = TB.DEFAULT_TB_STYLE, closingstyle = TB.TB_ONCLICK):
		TB.ToasterBox.__init__(self, parent, tbstyle, windowstyle, closingstyle)
		
		xx, yy, displayWidth, displayHeight = wx.ClientDisplayRect()
		
		self.SetPopupText(text)
		self.SetPopupSize(size)
		self.SetPopupPauseTime(pauseTime)
		self.SetPopupPosition((displayWidth - size[0], displayHeight - size[1]))

class DropboxScreenGrabber(wx.App):
	def OnInit(self):
		self.name = APP_NAME;
		self.instance = wx.SingleInstanceChecker(self.name)
		
		if self.instance.IsAnotherRunning():
			wx.MessageBox("Another instance of the program is already running", "ERROR")
			
			return False
		
		DropboxScreenGrabberFrame(None, -1, APP_NAME)

		return True

if __name__ == '__main__':
	application = DropboxScreenGrabber(0)
	application.MainLoop()