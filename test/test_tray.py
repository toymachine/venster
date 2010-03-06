## 	   Copyright (c) 2003 - 2004 Henk Punt

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

## This is an example on createing an application that minimizes to the system
## tray when closed.
## This program installs a tray icon with associated context menu.
## The program can be exitted trough the system tray menu.
## doubleclicking the tray icon will toggle between full view and tray minimized view

from venster.windows import *
from venster.wtl import *

from venster import comctl
from venster import gdi
from venster import shell

from venster.lib import form
from venster.lib import list
from venster.lib import tray
from venster.lib import menu

FILE_MENU = (MF_POPUP, "&File", 
                    [(MF_STRING, "&Close", form.ID_CLOSE),
                     (MF_SEPARATOR, ),
                     (MF_STRING, "&Exit", form.ID_EXIT)
                     ])

class Form(form.Form):
    _window_title_ = "Tray test"
    _window_icon_sm_ = _window_icon_ = Icon("cow.ico")
    _window_width_ = 700
    _window_height_ = 480
    
    _form_menu_ = [FILE_MENU]

    def OnDestroy(self, event):
        form.Form.OnDestroy(self, event)
        
    def OnClose(self, event):
        event.handled = True #prevent default handler from closing window
        self.ShowWindow(SW_HIDE) #instead hide it

    def OnExitCmd(self, event):
        exit()
        
        

class TrayIcon(tray.TrayIcon):
    _window_icon_ = Form._window_icon_
    _window_title_ = Form._window_title_
    _window_class_ = "ApplicationTrayWindow"

    _tray_icon_menu_open_ = [(MF_STRING, "*Open Application", form.ID_OPEN),
                             (MF_SEPARATOR,),
                             (MF_STRING, "Exit", form.ID_EXIT)]

    _tray_icon_menu_close_ = [(MF_STRING, "*Close Application", form.ID_CLOSE),
                              (MF_SEPARATOR,),
                              (MF_STRING, "Exit", form.ID_EXIT)]

    _tray_icon_menu_ = _tray_icon_menu_close_

    def __init__(self, mainForm):
        tray.TrayIcon.__init__(self)
        self.mainForm = mainForm
        
    def IsOpen(self):
        return self.mainForm.IsWindowVisible() and not self.mainForm.IsIconic()

    def Hide(self):
        self.mainForm.ShowWindow(SW_HIDE)
        
    def ShowNormal(self):
        self.mainForm.ShowWindow(SW_SHOWNORMAL)
        self.mainForm.SetForegroundWindow()
        
    def OnLeftButtonDoubleClick(self, event):
        if self.IsOpen():
            self.Hide()
        else:
            self.ShowNormal()

    def OnExitCmd(self, event):
        exit()
        
    def OnOpenCmd(self, event):
        self.ShowNormal()

    def OnCloseCmd(self, event):
        self.Hide()
        
    def TrackPopupMenu(self):
        if self.IsOpen():
            self._tray_icon_menu_ = self._tray_icon_menu_close_
        else:
            self._tray_icon_menu_ = self._tray_icon_menu_open_
        tray.TrayIcon.TrackPopupMenu(self)

mainForm = None
trayIcon = None
application = None

def exit():
    global mainForm
    global trayIcon
    mainForm.DestroyWindow()
    trayIcon.DestroyWindow()
    application.Quit()
    mainForm = None
    trayIcon = None
    
def run():
    global mainForm
    global trayIcon
    global application
    mainForm = Form()
    trayIcon = TrayIcon(mainForm)
    application = Application()
    application.Run()

if __name__ == '__main__':
    run()
