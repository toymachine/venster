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
from venster.lib import form

from venster import gdi
from venster import comctl

from venster.lib import splitter
from venster.lib import tree

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

class Tree(tree.Tree):
    def __init__(self, *args, **kwargs):
        tree.Tree.__init__(self, *args, **kwargs)

        item = comctl.TVITEMEX()
        item.text = "A root"
        item.children = 1
        hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, item)
        
        item.mask = 0
        item.text = "A child"
        hChild = self.InsertItem(hRoot, comctl.TVI_LAST, item)


    @ntf_handler(comctl.TVN_ITEMEXPANDING)
    def OnItemExpanding(self, event):
        print "item expanding"

    @ntf_handler(comctl.TVN_SELCHANGED)
    def OnSelectionChanged(self, event):
        print "on sel changed"

class CrossWindow(Window):
    _window_style_ = WS_VISIBLE | WS_CHILD
    _window_style_ex_ = 0
    _window_background_ = gdi.GetStockObject(WHITE_BRUSH)
    #make windows automatically invalidate window on resize, forces repaint of client area:
    _window_class_style_ = CS_HREDRAW | CS_VREDRAW 

    #@msg_handler(WM_PAINT) #python 2.4 style decorator
    def OnPaint(self, event):
        ps = PAINTSTRUCT()
        hdc = self.BeginPaint(ps)
        rc = self.GetClientRect()

        gdi.LineTo(hdc, rc.width, rc.height)
        gdi.MoveToEx(hdc, rc.width, 0, None)
        gdi.LineTo(hdc, 0, rc.height)
        
        self.EndPaint(ps)

    msg_handler(WM_PAINT)(OnPaint) #python 2.3 style decorator
    

class MyForm(form.Form):
    _window_title_ = "Decorator Test (requires python 2.4)"
    _window_icon_ = _window_icon_sm_ = Icon("blinky.ico")

    _form_menu_ = [(MF_POPUP, "&File",
                    [(MF_STRING, "&New\bCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR,),
                     (MF_STRING, "&Exit", form.ID_EXIT)])]

    _form_accels_ = [(FCONTROL|FVIRTKEY, ord("N"), form.ID_NEW)]

    def OnCreate(self, event):
        aCrossWindow = CrossWindow(parent = self, orExStyle = WS_EX_CLIENTEDGE)
        aTree = Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE)

        aSplitter = splitter.Splitter(parent = self, splitPos = 150)
        aSplitter.Add(0, aTree)
        aSplitter.Add(1, aCrossWindow)

        self.controls.Add(form.CTRL_VIEW, aSplitter)
    
    @cmd_handler(form.ID_NEW)
    def OnNew(self, event):
        newForm = MyForm()

if __name__ == '__main__':
    mainForm = MyForm()        
    application = Application()
    application.Run()
