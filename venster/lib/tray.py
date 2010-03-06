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


from venster.windows import *
from venster.wtl import *
from venster.shell import *

from venster.lib import form
from venster.lib import menu

WM_USER_TASKBAR = WM_USER + 1
#this message is send when explorer restarts after a crash:
WM_TASKBAR_CREATED = RegisterWindowMessage("TaskbarCreated") 

class TrayIcon(Window):
    _window_style_ = WS_OVERLAPPEDWINDOW #removed the WS_VISIBLE flag, this creates a hidden window

    _tray_icon_menu_ = [(MF_STRING, "*Open", form.ID_OPEN),
                        (MF_SEPARATOR,),
                        (MF_STRING, "Exit", form.ID_EXIT)]

    _tray_tip_ = None

    def __init__(self, uID = 0):
        self.uID = uID
        Window.__init__(self)
        
    def OnCreate(self, event):
        self.AddTrayIcon()

    msg_handler(WM_CREATE)(OnCreate)

    def OnDestroy(self, event):
        self.RemoveTrayIcon()
        
    msg_handler(WM_DESTROY)(OnDestroy)
        
    def AddTrayIcon(self):
        ntfIconData = NOTIFYICONDATA()
        ntfIconData.cbSize = sizeof(NOTIFYICONDATA) #todo versioning

        ntfIconData.hWnd = self.handle
        ntfIconData.uID = self.uID
        ntfIconData.uFlags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        ntfIconData.hIcon = handle(self._window_icon_)
        ntfIconData.uCallbackMessage = WM_USER_TASKBAR
        ntfIconData.szTip = self._tray_tip_ or self._window_title_
        Shell_NotifyIcon(NIM_ADD, byref(ntfIconData))

        ntfIconData.uVersion = NOTIFYICON_VERSION #todo check that shell >= 5.0 is present
        Shell_NotifyIcon(NIM_SETVERSION, byref(ntfIconData))

    def RemoveTrayIcon(self):
        ntfIconData = NOTIFYICONDATA()
        ntfIconData.cbSize = sizeof(NOTIFYICONDATA) #todo versioning
        ntfIconData.hWnd = self.handle
        ntfIconData.uID = self.uID
        Shell_NotifyIcon(NIM_DELETE, byref(ntfIconData))
    
    def WndProc(self, hWnd, nMsg, wParam, lParam):
        #the shell icon will send notification messages to the hidden window
        #the message is the one given by the uCallbackMessage field when the icon was
        #added to the tray.
        #the lParam contains the original msg (WM_MOUSEMOVE etc). we intercept
        #it here, and turn it into a normal msg and use normal wtl processing to handle the msg
        if nMsg == WM_USER_TASKBAR:
            nMsg = lParam
            lParam = 0
            wParam = 0
            return Window.WndProc(self, hWnd, nMsg, wParam, lParam)
        else:
            return Window.WndProc(self, hWnd, nMsg, wParam, lParam)

    def OnTaskbarCreated(self, event):
        #after an Explorer crash, this event will be received
        #when explorer restarts. Then we re-add the tray icon...
        self.AddTrayIcon()
        
    msg_handler(WM_TASKBAR_CREATED)(OnTaskbarCreated)
    
    def TrackPopupMenu(self):
        #To display a context menu for a notification icon, the 
        #current window must be the foreground window before the 
        #application calls TrackPopupMenu or TrackPopupMenuEx. Otherwise, 
        #the menu will not disappear when the user clicks outside of the 
        #menu or the window that created the menu (if it is visible). 
        self.SetForegroundWindow()
        trayMenu = menu.EvalPopupMenu(self._tray_icon_menu_, managed = True)
        trayMenu.Track(self)
        #See MS KB article Q135788
        self.PostMessage(WM_NULL)

    def OnContextMenu(self, event):
        self.TrackPopupMenu()

    msg_handler(WM_CONTEXTMENU)(OnContextMenu)

    def OnRightButtonUp(self, event):
        self.TrackPopupMenu()
        
    msg_handler(WM_RBUTTONUP)(OnRightButtonUp)
                              
    def OnExitCmd(self, event):
        self.DestroyWindow()
        PostQuitMessage(0)

    cmd_handler(form.ID_EXIT)(OnExitCmd)

    def OnLeftButtonDoubleClick(self, event):
        pass
        
    msg_handler(WM_LBUTTONDBLCLK)(OnLeftButtonDoubleClick)

    def OnOpenCmd(self, event):
        pass
        
    cmd_handler(form.ID_OPEN)(OnOpenCmd)

    def OnCloseCmd(self, event):
        pass
        
    cmd_handler(form.ID_CLOSE)(OnCloseCmd)
