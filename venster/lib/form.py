## 	   Copyright (c) 2003 Henk Punt

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
from venster import comctl
from venster import gdi

import menu

#determines form destroy policy:
EXIT_NONE = 0
EXIT_ONDESTROY = 1 #exit app on destroy of form
EXIT_ONLASTDESTROY = 2 #exit app on destroy of last form

#some useful default command id's:
ID_NEW = 5001
ID_OPEN = 5002
ID_EXIT = 5003
ID_SAVE = 5004
ID_SAVEAS = 5005
ID_CLOSE = 5006

ID_UNDO = 5101
ID_REDO = 5102
ID_COPY = 5103
ID_PASTE = 5104
ID_CUT = 5105

ID_SELECTALL = 5106
ID_CLEAR = 5107

ID_HELP_CONTENTS = 5201
ID_ABOUT = 5202

CTRL_VIEW = "form_CtrlView"
CTRL_STATUSBAR = "form_CtrlStatusBar"
CTRL_COOLBAR = "form_CtrlCoolbar"

class Controls(dict):
    def Add(self, *args):
        if len(args) == 1:
            self[args[0]] = args[0]
        elif len(args) == 2:
            self[args[0]] = args[1]
        else:
            raise "invalid number of arguments"
            
    def dispose(self):
        for ctrl in self.values():
            ctrl.dispose()
        self.clear()

    def __getattr__(self, key):
        if self.has_key(key):
            return self[key]
        else:
            return dict.__getattr__(key)
        
class Form(Window):
    """A class representing an applications main window. This class
    supports accelerators, automatic closing of the application with
    simple window management
    For status bar support make sure you have a statusBar property in
    your derived Form and provide _form_status_msgs_ to enable
    help msgs on the statusbar.
    A single child view is supported and it must be available in the
    derived class as 'view' property.
    """
    
    _window_style_ex_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | \
                        WS_EX_WINDOWEDGE | WS_EX_APPWINDOW

    _window_background_ = gdi.GetStockObject(WHITE_BRUSH)
    _form_accels_ = []

    _form_exit_ = EXIT_ONDESTROY
    _form_count_ = 0
    _form_status_msgs_ = {} #maps command_id's to status bar msgs

    _form_menu_ = [(MF_POPUP, "&File",
                    [(MF_SEPARATOR,),
                     (MF_STRING, "&Exit", ID_EXIT)])]

    def __init__(self, *args, **kwargs):
        self.m_controls = Controls()
        aMenu = kwargs.get('menu', None) or (self._form_menu_ and menu.EvalMenu(self._form_menu_))
        if aMenu: kwargs['menu'] = aMenu
        #install accelerator support
        self.CreateAccels()
        GetMessageLoop().AddFilter(self.PreTranslateMessage)
        Form._form_count_ += 1
        Window.__init__(self, *args, **kwargs)

    controls = property(lambda self: self.m_controls)
    
    def dispose(self):
        self.controls.dispose()
        #TODO weak ref on filter
        GetMessageLoop().RemoveFilter(self.PreTranslateMessage)
        #TODO dispose Accel Table weak refs?

    _haccel_ = 0
        
    def CreateAccels(self):
        """Create accelerator table from _form_accels_"""
        if self._form_accels_ and not Form._haccel_:
            accels = (ACCEL * len(self._form_accels_))()
            for i in range(len(self._form_accels_)):
                accels[i].fVirt = self._form_accels_[i][0]
                accels[i].key   = self._form_accels_[i][1]
                accels[i].cmd   = self._form_accels_[i][2]
            Form._haccel_ = CreateAcceleratorTable(byref(accels), len(self._form_accels_))


    def PreTranslateMessage(self, msg):
        if Form._haccel_ and self.handle == GetForegroundWindow():
            return TranslateAccelerator(self.handle, Form._haccel_, byref(msg))
        else:
            return 0

    def OnMenuSelect(self, event):
        """displays short help msg for menu command on statusbar"""
        statusBar = self.controls.get(CTRL_STATUSBAR, None)
        if not statusBar: return
        wFlags = HIWORD(event.wParam)
        if wFlags == 0xffff and event.lParam == 0:
            statusBar.Simple(0)
        else:
            txt = self._form_status_msgs_.get(LOWORD(event.wParam), "")
            statusBar.Simple(1)
            statusBar.SetText(txt)

    class CmdUIUpdateEvent(object):
        def __init__(self):
            self.m_enabled = 0

        def Enable(self, fEnable):
            self.m_enabled = fEnable

        enabled = property(lambda self: self.m_enabled)
        
    def OnInitMenuPopup(self, event):
        """querys cmd ui update map to see if menu items must be enabled/disabled"""
        if HIWORD(event.lParam) == 1: return #it's the window menu
        cmdUiUpdateMap = self._msg_map_._msg_map_.get("CMD_UI_UPDATE_MAP", {})
        hMenu = event.wParam
        minfo = MENUITEMINFO()
        minfo.cbSize = sizeof(MENUITEMINFO)
        minfo.fMask = MIIM_ID | MIIM_TYPE
        for i in range(GetMenuItemCount(hMenu)):
            minfo.fMask = MIIM_ID | MIIM_TYPE
            GetMenuItemInfo(hMenu, i, 1, byref(minfo))
            if minfo.fType == MFT_STRING:
                handler = cmdUiUpdateMap.get(minfo.wID, None)
                if handler:
                    cmdUiUpdateEvent = self.CmdUIUpdateEvent()
                    handler(self, cmdUiUpdateEvent)
                    minfo.fMask = MIIM_STATE
                    if cmdUiUpdateEvent.enabled:
                        minfo.fState = MFS_ENABLED
                    else:
                        minfo.fState = MFS_DISABLED
                    SetMenuItemInfo(hMenu, i, 1, byref(minfo))

    def DoLayout(self, cx, cy):
        """Lays out the form. A form consists of an optional toolbar, view and statusbar"""
        deferWindowPos = []

        coolBar = self.controls.get(CTRL_COOLBAR, None)
        if coolBar:
            coolBarHeight = coolBar.windowRect.height
            deferWindowPos.append((coolBar,
                                   0, 0,
                                   cx, coolBarHeight))
        else:
            coolBarHeight = 0

        statusBar = self.controls.get(CTRL_STATUSBAR, None)
        if statusBar:
            statusBarHeight = statusBar.windowRect.height
            deferWindowPos.append((statusBar,
                                   0, cy - statusBarHeight,
                                   cx, statusBarHeight))
        else:
            statusBarHeight = 0

        view = self.controls.get(CTRL_VIEW, None)
        if view:
            deferWindowPos.append((view,
                                   0, coolBarHeight,
                                   cx, cy - statusBarHeight - coolBarHeight))


        hdwp = BeginDeferWindowPos(len(deferWindowPos))
        for ctrl, x, y, dx, dy in deferWindowPos:
            DeferWindowPos(hdwp, ctrl.handle, NULL, x, y,
                           dx, dy, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)

        if coolBar: coolBar.Invalidate()
        
    def OnDestroy(self, event):
        self.dispose()
        Form._form_count_ -= 1
        if self._form_exit_ == EXIT_ONDESTROY:
            PostQuitMessage(0)            
        elif self._form_exit_ == EXIT_ONLASTDESTROY and \
             self._form_count_ == 0:
            PostQuitMessage(0)

    def OnSize(self, event):
        self.DoLayout(*event.size)

    def OnCreate(self, event):
        pass
        
    def OnExitCmd(self, event):
        self.SendMessage(WM_CLOSE)

    def OnCloseCmd(self, event):
        self.SendMessage(WM_CLOSE)

    ##override and set event.handled = True to prevent
    ##form from closing
    def OnClose(self, event):
        event.handled = False #event will buble and invoke window destroy eventually
    
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_DESTROY, OnDestroy),
                         MSG_HANDLER(WM_CREATE, OnCreate),
                         MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_CLOSE, OnClose),
                         MSG_HANDLER(WM_MENUSELECT, OnMenuSelect),
                         MSG_HANDLER(WM_INITMENUPOPUP, OnInitMenuPopup),
                         CMD_ID_HANDLER(ID_EXIT, OnExitCmd),
                         CMD_ID_HANDLER(ID_CLOSE, OnCloseCmd),
                         NTF_HANDLER(comctl.RBN_HEIGHTCHANGE,
                                     lambda self, event: self.DoLayout(*self.clientRect.size)),
                         ])
        


class CMD_UI_UPDATE(object):
    """This msp map handler is used to update cmd ui elements"""
    def __init__(self, id, handler):
        self.id, self.handler = id, handler

    def __install__(self, msgMap):
        cmdMap = msgMap._msg_map_.setdefault("CMD_UI_UPDATE_MAP", {})
        cmdMap[self.id] = self
             
    def __call__(self, receiver, event):
        self.handler(receiver, event)

