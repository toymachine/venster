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
from venster import gdi

HORIZONTAL = 1
VERTICAL = 2
    
class Splitter(Window):
    _window_style_ = WS_CHILD | WS_VISIBLE
    _window_style_ex_ = 0
    _window_background_ = gdi.GetSysColorBrush(COLOR_BTNFACE)

    def __init__(self, *args, **kwargs):
        self.splitWidth = kwargs.get('splitWidth', 4)
        self.splitPos = kwargs.get('splitPos', 100)
        self.orientation = kwargs.get('orientation', VERTICAL)
        if kwargs.has_key('splitPos'): del kwargs['splitPos']
        if kwargs.has_key('splitWidth'): del kwargs['splitWidth']
        if kwargs.has_key('orientation'): del kwargs['orientation']

        #TODO wrap cursor type: (and then dispose)
        if self.orientation == VERTICAL:
            self.hcursor = LoadCursor(NULL, IDC_SIZEWE)
        elif self.orientation == HORIZONTAL:
            self.hcursor = LoadCursor(NULL, IDC_SIZENS)

        brushPat = (c_ushort * 8)()
        for i in range(8):
            brushPat[i] = (0x5555 << (i & 1))

        hbitmap = gdi.CreateBitmap(8, 8, 1, 1, byref(brushPat))
        if hbitmap:
            self.brush = gdi.CreatePatternBrush(hbitmap)
            gdi.DeleteObject(hbitmap)
        else:
            self.brush = gdi.CreateHatchBrush(gdi.HS_DIAGCROSS, 0)

        self.m_views = {}

        Window.__init__(self, *args, **kwargs)


    def dispose(self):
        del self.m_views
        
    def Add(self, index, ctrl):
        #make sure splitter window is at bottom
        self.SetWindowPos(HWND_BOTTOM, 0, 0, 0, 0,
                          SWP_NOACTIVATE|SWP_NOMOVE|SWP_NOREDRAW|SWP_NOSIZE)
        self.m_views[index] = ctrl
        
    def OnSize(self, event):
        self.Layout(*event.size)
        
    def Layout(self, cx, cy):
        if len(self.m_views) < 2: return
        
        wr = self.windowRect
        pt = POINT()        
        pt.x = wr.left
        pt.y = wr.top
        self.GetParent().ScreenToClient(pt)

        #move windows all together
        hdwp = BeginDeferWindowPos(2)
        x, y = int(pt.x), int(pt.y)
        ctrl = self.m_views[0]
        if self.orientation == VERTICAL:
            DeferWindowPos(hdwp, ctrl.handle, NULL, x, y, self.splitPos, cy,
                           SWP_NOACTIVATE | SWP_NOZORDER)
        elif self.orientation == HORIZONTAL:
            DeferWindowPos(hdwp, ctrl.handle, NULL, x, y, cx, self.splitPos,
                           SWP_NOACTIVATE | SWP_NOZORDER)
        ctrl = self.m_views[1]
        if self.orientation == VERTICAL:
            DeferWindowPos(hdwp, ctrl.handle, NULL, self.splitPos + self.splitWidth + x, y,
                           cx - self.splitPos - self.splitWidth, cy, SWP_NOACTIVATE | SWP_NOZORDER)
        elif self.orientation == HORIZONTAL:
            DeferWindowPos(hdwp, ctrl.handle, NULL, x, self.splitPos + self.splitWidth + y,
                           cx, cy - self.splitPos - self.splitWidth, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)
        

    def OnLeftButtonDown(self, event):
        x, y = GET_XY_LPARAM(event.lParam)
        if self.orientation == VERTICAL:
            self.dragOffset = x - self.splitPos
        elif self.orientation == HORIZONTAL:
            self.dragOffset = y - self.splitPos
            
        if self.IsOverSplitter(x, y):
            self.SetCapture()
            if self.orientation == VERTICAL:
                self.PatBlt(0, x, 0)
            elif self.orientation == HORIZONTAL:
                self.PatBlt(0, y, 0)

    def IsOverSplitter(self, x, y):
        if self.orientation == VERTICAL and \
               x >= self.splitPos and x <= self.splitPos + self.splitWidth:
            return 1
        elif self.orientation == HORIZONTAL and \
             y >= self.splitPos and y <= self.splitPos + self.splitWidth:
            return 1
        else:
            return 0

    def OnLeftButtonUp(self, event):
        if GetCapture() == self.handle:
            x, y = GET_XY_LPARAM(event.lParam)
            x, y = self.Clamp(x, y)
            ReleaseCapture()
            if self.orientation == VERTICAL:
                self.PatBlt(0, x, 0)
            elif self.orientation == HORIZONTAL:
                self.PatBlt(0, y, 0)
            rc = self.clientRect
            self.splitPos -= self.dragOffset
            self.Layout(rc.width, rc.height)

    def Clamp(self, x, y):
        if self.orientation == VERTICAL:
            if x - self.dragOffset < 10:
                x = 10 + self.dragOffset
            if x > self.clientRect.width - 10 - self.splitWidth + self.dragOffset:
                x = self.clientRect.width - 10 - self.splitWidth + self.dragOffset
        elif self.orientation == HORIZONTAL:
            if y - self.dragOffset < 10:
                y = 10 + self.dragOffset
            if y > self.clientRect.height - 10 - self.splitWidth + self.dragOffset:
                y = self.clientRect.height - 10 - self.splitWidth + self.dragOffset
            
        return x, y
    
    def OnMouseMove(self, event):
        if event.wParam & MK_LBUTTON and GetCapture() == self.handle:
            x, y = GET_XY_LPARAM(event.lParam)
            x, y = self.Clamp(x, y)
            if self.orientation == VERTICAL:
                self.PatBlt(self.splitPos, x, 1)
            elif self.orientation == HORIZONTAL:
                self.PatBlt(self.splitPos, y, 1)
            
    def PatBlt(self, oldPos, newPos, eraseOld):
        if oldPos == newPos: return
        
        hdc = self.GetDCEx(NULL, DCX_PARENTCLIP)
        hbr = gdi.SelectObject(hdc, self.brush)

        if eraseOld:
            if self.orientation == VERTICAL:
                gdi.PatBlt(hdc, oldPos - self.dragOffset, 0,
                           self.splitWidth, self.clientRect.height, gdi.PATINVERT)
            elif self.orientation == HORIZONTAL:
                gdi.PatBlt(hdc, 0, oldPos - self.dragOffset,
                           self.clientRect.width, self.splitWidth, gdi.PATINVERT)

        if self.orientation == VERTICAL:
            gdi.PatBlt(hdc, newPos - self.dragOffset, 0,
                       self.splitWidth, self.clientRect.height, gdi.PATINVERT)
        elif self.orientation == HORIZONTAL:
            gdi.PatBlt(hdc, 0, newPos - self.dragOffset,
                       self.clientRect.width, self.splitWidth, gdi.PATINVERT)
            
        gdi.SelectObject(hdc, hbr)
        self.ReleaseDC(hdc)

        self.splitPos = newPos
        

    def OnSetCursor(self, event):
        x, y = GET_XY_LPARAM(GetMessagePos())
        pt = POINT(x, y)
        self.ScreenToClient(pt)
        if self.IsOverSplitter(pt.x, pt.y):
            SetCursor(self.hcursor)

    def OnCaptureChanged(self, event):
        #TODO?
        pass
        
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_LBUTTONDOWN, OnLeftButtonDown),
                         MSG_HANDLER(WM_LBUTTONUP, OnLeftButtonUp),
                         MSG_HANDLER(WM_MOUSEMOVE, OnMouseMove),
                         MSG_HANDLER(WM_SETCURSOR, OnSetCursor),
                         MSG_HANDLER(WM_CAPTURECHANGED, OnCaptureChanged)])
        
    

