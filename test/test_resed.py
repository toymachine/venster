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
from venster.debug import *
from venster.gdi import *

from venster import comctl
from venster.lib import form


comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

class Canvas(Window):
    _window_style_ = WS_CHILD | WS_VISIBLE
    _window_background_ = GetStockObject(WHITE_BRUSH)
    
    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        self.dragging = False
        self.lastDragEnd = None
        self.selectedControls = []
        
##     def WndProc(self, hWnd, nMsg, wParam, lParam):
##         print "canvas: ", msgFormatter.format(nMsg, wParam, lParam)
##         return Window.WndProc(self, hWnd, nMsg, wParam, lParam)

    def OnLeftButtonDown(self, event):
        child = self.ChildWindowFromPoint(event.clientPosition)
        if child != self:
            if self.selectedControls and self.selectedControls[0] == child:
                self.selectedControls = []
            else:
                self.selectedControls = [child]
            self.Invalidate()
            
        self.dragStart = event.clientPosition
        self.lastDragEnd = None
        self.dragging = True
        self.SetCapture()

    msg_handler(WM_LBUTTONDOWN)(OnLeftButtonDown)
    
    def DragEnd(self):
        if self.lastDragEnd:
            hdc = self.GetDCEx(NULL, DCX_PARENTCLIP)
            self.DrawRect(hdc)
            self.ReleaseDC(hdc)
           
        ReleaseCapture()
        self.dragging = False
        self.lastDragEnd = None

    def DrawRect(self, hdc):
        #figure out where start and end points are
        startX = min(self.dragStart.x, self.lastDragEnd.x)
        startY = min(self.dragStart.y, self.lastDragEnd.y)
        endX = max(self.dragStart.x, self.lastDragEnd.x)
        endY = max(self.dragStart.y, self.lastDragEnd.y)
        #draw the rubberband
        DrawFocusRect(hdc, byref(RECT(startX, startY, endX, endY)))
        
    def OnLeftButtonUp(self, event):
        self.DragEnd()

    msg_handler(WM_LBUTTONUP)(OnLeftButtonUp)

    def OnMouseMove(self, event):
        if not self.dragging: return
        #keep the rubberband within the canvas
        cpos = event.clientPosition
        crect = self.clientRect
        if cpos.x > crect.right: cpos = POINT(crect.right, cpos.y)
        if cpos.y > crect.bottom: cpos = POINT(cpos.x, crect.bottom)
        if cpos.x < crect.left: cpos = POINT(crect.left, cpos.y)
        if cpos.y < crect.top: cpos = POINT(cpos.x, crect.top)
        #undraw the last rubberband and draw the new one
        hdc = self.GetDCEx(NULL, DCX_PARENTCLIP)
        if self.lastDragEnd: self.DrawRect(hdc)
        self.lastDragEnd = cpos
        self.DrawRect(hdc)
        self.ReleaseDC(hdc)

    msg_handler(WM_MOUSEMOVE)(OnMouseMove)
    
    def OnCancelMode(self, event):
        self.DragEnd()

    msg_handler(WM_CANCELMODE)(OnCancelMode)

    hatchPen = Pen.CreateEx(dwPenStyle = PS_GEOMETRIC | PS_SOLID, dwWidth = 5,
                            lbStyle = BS_HATCHED, lbColor = 0x00000000,
                            lbHatch = HS_FDIAGONAL)

    rectBrush = SolidBrush(0x00000000)

    def GetDragRects(self, rc):
        """returns a list of rectangles representing the little
        drag rectangles at the corners of a selected item"""
        return [RECT(rc.left - 2, rc.top - 2, rc.left + 4, rc.top + 4),
                RECT(rc.right - 3, rc.top - 2, rc.right + 3, rc.top + 4),
                RECT(rc.right - 3, rc.bottom -2, rc.right +3, rc.bottom + 4),
                RECT(rc.left -2, rc.bottom - 2, rc.left + 4, rc.bottom + 4)]
        
    def DrawSelectRect(self, hdc, rc):
        """draws a marker around a selected item"""
        oldPen = SelectObject(hdc, self.hatchPen.handle)
        MoveToEx(hdc, rc.left, rc.top, 0)
        LineTo(hdc, rc.right, rc.top)
        LineTo(hdc, rc.right, rc.bottom)
        LineTo(hdc, rc.left, rc.bottom)
        LineTo(hdc, rc.left, rc.top)
        SelectObject(hdc, oldPen)
        for dragRc in self.GetDragRects(rc):
            FillRect(hdc, byref(dragRc), self.rectBrush.handle)
        
    def OnPaint(self, event):
        ps = PAINTSTRUCT()
        hdc = self.BeginPaint(ps)
        for ctrl in self.selectedControls:
            selfWr = self.windowRect
            ctrlWr = ctrl.windowRect
            selRect = RECT(ctrlWr.left - selfWr.left - 3,
                           ctrlWr.top - selfWr.top - 3,
                           ctrlWr.right - selfWr.left + 2,
                           ctrlWr.bottom - selfWr.top + 2)            
            self.DrawSelectRect(hdc, selRect)
        self.EndPaint(ps)

    msg_handler(WM_PAINT)(OnPaint)

    defaultCursor = LoadCursor(NULL, IDC_ARROW)
    
    cursors = [LoadCursor(NULL, IDC_SIZENWSE),
               LoadCursor(NULL, IDC_SIZENESW),
               LoadCursor(NULL, IDC_SIZENWSE),
               LoadCursor(NULL, IDC_SIZENESW)]
    
    def OnSetCursor(self, event):
        pt = event.position #in screen coords
        try:
            for child in self.selectedControls:
                for i, rect in enumerate(self.GetDragRects(child.windowRect)):
                    if rect.ContainsPoint(pt):
                        SetCursor(self.cursors[i])
                        raise "done"
        except:
            pass
        else:
            SetCursor(self.defaultCursor)

    msg_handler(WM_SETCURSOR)(OnSetCursor)

msgFormatter = MsgFormatter()

class intercept(object):
    def __init__(self, target, source):
        self.newProc = WNDPROC(self.WndProc)
        self.oldProc = source.SubClass(self.newProc)
        self.target = target
        self.source = source
        for childWindow in source.EnumChildWindows():
            intercept(target, childWindow)
        
    def WndProc(self, hWnd, nMsg, wParam, lParam):
##        print "control: ", msgFormatter.format(nMsg, wParam, lParam)
        callTarget = False
        if nMsg in [WM_MOUSEMOVE,
                    WM_LBUTTONDOWN, WM_LBUTTONUP, WM_LBUTTONDBLCLK,
                    WM_RBUTTONDOWN, WM_RBUTTONUP, WM_RBUTTONDBLCLK,
                    WM_MBUTTONDOWN, WM_MBUTTONUP, WM_MBUTTONDBLCLK,]:
            pt = GET_POINT_LPARAM(lParam)
            self.source.ClientToScreen(pt)
            self.target.ScreenToClient(pt)
            lParam = MAKELPARAM(pt.x, pt.y)
            callTarget = True
        elif nMsg == WM_SETCURSOR:
            callTarget = True
            
        if callTarget:
            handled, result = self.target.WndProc(hWnd, nMsg, wParam, lParam)
            return result
        else:
            return CallWindowProc(self.oldProc, hWnd, nMsg, wParam, lParam)
        
class Form(form.Form):
    _form_accels_ = [(FCONTROL|FVIRTKEY, ord("N"), form.ID_NEW),
                      (FCONTROL|FVIRTKEY, ord("O"), form.ID_OPEN),]
    
    _form_menu_ = [(MF_POPUP, "&File", 
                    [(MF_STRING, "&New\tCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR, ),
                     (MF_STRING, "&Exit", form.ID_EXIT)
                     ]),
                   ]

    _window_title_ = "Venster Resource Editor"
    
    def __init__(self):
        form.Form.__init__(self)      

    def OnCreate(self, event):
        canvas = Canvas(parent = self)
        self.controls.Add(form.CTRL_VIEW, canvas)
        self.controls.Add(form.CTRL_STATUSBAR, comctl.StatusBar(parent = self))

    canvas = property(lambda self: self.controls[form.CTRL_VIEW])
    
    def OnNew(self, event):
##         self.button = comctl.Button("Click Me!", parent = self.canvas,
##                                     rcPos = RECT(100, 100, 250, 325))
        
##         intercept(self.canvas, self.button)

        self.combo = comctl.ComboBox(parent = self.canvas,
                                     rcPos = RECT(275, 100, 500, 125))

        intercept(self.canvas, self.combo)
        
    cmd_handler(form.ID_NEW)(OnNew)
   
if __name__ == '__main__':
    mainForm = Form()
    mainForm.ShowWindow()

    application = Application()
    application.Run()
