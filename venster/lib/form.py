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

class Form(Window):
    """A class representing an applications main window. This class
    supports accelerators, automatic closing of the application with
    simple window management
    For status bar support make sure you have a statusBar property in
    your derived Form and provide _class_form_status_msgs_ to enable
    help msgs on the statusbar.
    A single child view is supported and it must be available in the
    derived class as 'view' property.
    """
    
    _class_ws_style = WS_OVERLAPPEDWINDOW | WS_VISIBLE | WS_OVERLAPPED
    _class_ws_ex_style_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | \
                          WS_EX_WINDOWEDGE | WS_EX_APPWINDOW

    _class_background_ = 0
    _class_accels_ = []
    _haccel_ = 0

    _class_form_exit_ = EXIT_ONDESTROY
    _class_form_count_ = 0
    _class_form_status_msgs_ = {} #maps command_id's to status bar msgs

    _form_menu_ = [(MF_POPUP, "&File",
                    [(MF_SEPARATOR,),
                     (MF_STRING, "&Exit", ID_EXIT)])]

    _form_title_ = ""
    
    def __init__(self, *args, **kwargs):
        menu = kwargs.get('menu', None) or self.EvalMenu(None, self._form_menu_)
        if menu: kwargs['menu'] = menu
        kwargs['title'] = kwargs.get('title', '') or self._form_title_
        Window.__init__(self, *args, **kwargs)
        #install accelerator support
        self.CreateAccels()
        GetMessageLoop().AddFilter(self.PreTranslateMessage)
        Form._class_form_count_ += 1
        self.m_controls = Controls()
        

    controls = property(lambda self: self.m_controls)
    
    def dispose(self):
        self.controls.dispose()
        #TODO weak ref on filter
        GetMessageLoop().RemoveFilter(self.PreTranslateMessage)
        #TODO dispose Accel Table weak refs?
        
    def CreateAccels(self):
        """Create accelerator table from _class_accels_"""
        if self._class_accels_ and not Form._haccel_:
            accels = (ACCEL * len(self._class_accels_))()
            for i in range(len(self._class_accels_)):
                accels[i].fVirt = self._class_accels_[i][0]
                accels[i].key   = self._class_accels_[i][1]
                accels[i].cmd   = self._class_accels_[i][2]
            Form._haccel_ = CreateAcceleratorTable(byref(accels), len(self._class_accels_))


    def EvalMenu(self, parent, item):
        #the menus and popupmenus created by this method are non managed (
        #this is because the real handle will be owned by the form window
        #and the menu's will be destroyed when the window itself is destroyed
        if item is None:
            return None
        if parent is None:
            menu = Menu(managed = False)
            for subItem in item:
                self.EvalMenu(menu, subItem)
            return menu
        elif item[0] == MF_POPUP:
            popupMenu = PopupMenu(managed = False)
            for subItem in item[2]:
                self.EvalMenu(popupMenu, subItem)
            parent.AppendMenu(MF_POPUP, popupMenu, item[1])
        elif item[0] == MF_STRING:
            parent.AppendMenu(MF_STRING, item[2], item[1])
        elif item[0] == MF_SEPARATOR:
            parent.AppendMenu(MF_SEPARATOR, 0, 0)
            
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
            txt = self._class_form_status_msgs_.get(LOWORD(event.wParam), "")
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
        cmdUiUpdateMap = self._msg_map_._msg_map_.get("CMD_UI_UPDATE_MAP", {})
        menu = instanceFromHandle(event.wParam)
        if not menu: return #not a wtl menu
        minfo = MENUITEMINFO()
        minfo.cbSize = sizeof(MENUITEMINFO)
        minfo.fMask = MIIM_ID | MIIM_TYPE
        for i in range(len(menu)):
            minfo.fMask = MIIM_ID | MIIM_TYPE
            GetMenuItemInfo(menu.handle, i, 1, byref(minfo))
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
                    SetMenuItemInfo(menu.handle, i, 1, byref(minfo))

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
        Form._class_form_count_ -= 1
        if self._class_form_exit_ == EXIT_ONDESTROY:
            PostQuitMessage(0)
        elif self._class_form_exit_ == EXIT_ONLASTDESTROY and \
             self._class_form_count_ == 0:
            PostQuitMessage(0)

    def OnSize(self, event):
        self.DoLayout(*event.size)

    def OnExit(self, event):
        self.SendMessage(WM_CLOSE)

    ##override and set event.handled = 1 to prevent
    ##form from closing
    def OnClose(self, event):
        self.dispose()
        event.handled = 0
    
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_DESTROY, OnDestroy),
                         MSG_HANDLER(WM_CLOSE, OnClose),
                         MSG_HANDLER(WM_MENUSELECT, OnMenuSelect),
                         MSG_HANDLER(WM_INITMENUPOPUP, OnInitMenuPopup),
                         CMD_ID_HANDLER(ID_EXIT, OnExit),
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

