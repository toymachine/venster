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
from venster import atl
from venster import comctl
from venster import gdi

class NoteBook(comctl.TabControl):
    _window_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS
    _window_style_ex_ = 0
    _window_background_ = 0
    
    def __init__(self, *args, **kwargs):
        comctl.TabControl.__init__(self, *args, **kwargs)
        
        hfnt = gdi.GetStockObject(gdi.DEFAULT_GUI_FONT)
        SendMessage(self.handle, WM_SETFONT, hfnt, 0)
        #intercept msgs tabctrl sends to parent in order to detect current
        #tab changes:
        self.m_interceptor = self.Intercept(self.GetParent(), self._msg_map2_)
                                          
        #remove the default CS_HREDRAW and CS_VREDRAW class styles from
        #tab ctrl, these produce much flicker!
        #may produce some artifacts, anybody got a solution?
        clsStyle = self.GetClassLong(GCL_STYLE)
        clsStyle &= ~CS_HREDRAW
        clsStyle &= ~CS_VREDRAW
        self.SetClassLong(GCL_STYLE, clsStyle)

    def dispose(self):
        self.m_interceptor.dispose()
        del self.m_interceptor

    def _ResizeChild(self, child):
        if child:
            rc = self.GetClientRect()
            self.AdjustRect(0, rc)
            child.MoveWindow(rc.left, rc.top, rc.width, rc.height, TRUE)
            
    def GetChildAt(self, index):
        if index >= 0:
            item = self.GetItem(index, TCIF_PARAM)
            return instanceFromHandle(item.lParam)
        else:
            return None
        
    def AddTab(self, index, title, child):
        item = comctl.TCITEM()
        item.mask = TCIF_TEXT | TCIF_PARAM
        item.pszText = title
        item.lParam = handle(child)
        self.InsertItem(index, item)
        self._ResizeChild(child)
        self.SetCurrentTab(index)
        return index

    def SetCurrentTab(self, index):
        """sets the current tab to index"""
        if index == self.GetCurSel(): return
        self.OnSelChanging(None) #simulate
        self.SetCurSel(index) #does not cause sel changing and sel change events
        self.OnSelChange(None) #simulate

    def GetCurrentChild(self):
        return self.GetChildAt(self.GetCurSel())
    
    def OnSelChange(self, event):
        """new current tab"""
        child = self.GetCurrentChild()
        if child:
            self._ResizeChild(child)
            child.ShowWindow(SW_SHOW)

    def OnSelChanging(self, event):
        #current tab changing
        child = self.GetChildAt(self.GetCurSel())
        if child:
            child.ShowWindow(SW_HIDE)
        
    def OnSize(self, event):
        self.Invalidate() #slight flicker at tabs, but keeps artifacts from showing up
        #maybe only invalidate areas not covered by child
        child = self.GetChildAt(self.GetCurSel())
        self._ResizeChild(child)
        event.handled = 0

    def OnEraseBackground(self, event):
        event.handled = 0

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_ERASEBKGND, OnEraseBackground)])

    _msg_map2_ = MSG_MAP([NTF_HANDLER(comctl.TCN_SELCHANGE, OnSelChange),
                          NTF_HANDLER(comctl.TCN_SELCHANGING, OnSelChanging)])
                       
    
