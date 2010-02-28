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
from venster.comctl import *
from venster.lib import list
from venster.lib import form


from ctypes import *

blinkyIcon = Icon("blinky.ico")

columnDefs = [("blaat", 100), ("col2", 150)]

class MyList(list.List):
    def OnPaint(self, event):
        #print "lpaint", self.handle
        width = self.clientRect.width
        for i in range(len(columnDefs) - 1):
            #self.SetColumnWidth(i, width / len(columnDefs))
            self.SetColumnWidth(i, -2)
        self.SetColumnWidth(len(columnDefs) - 1, -2)

        event.handled = 0

    def OnWindowPosChanging(self, event):
        event.handled = 0

    def OnSize(self, event):
        
        #width = self.clientRect.width
        ShowScrollBar(self.handle, SB_HORZ, False)
        self.SetRedraw(0)
        for i in range(len(columnDefs) - 1):
            #self.SetColumnWidth(i, width / len(columnDefs))
            self.SetColumnWidth(i, -2)
        self.SetColumnWidth(len(columnDefs) - 1, -2)
        self.SetRedraw(1)
        
        event.handled = 0

    def OnColumnClick(self, event):
        nmlv = NMLISTVIEW.from_address(int(event.lParam))
        print "column clicked!", nmlv.iSubItem
        
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_PAINT, OnPaint),
                         MSG_HANDLER(WM_WINDOWPOSCHANGED, OnWindowPosChanging),
                         MSG_HANDLER(WM_SIZE, OnSize),
                         NTF_HANDLER(LVN_COLUMNCLICK, OnColumnClick)])
    
    
class MyForm(form.Form):
    _class_icon_ = blinkyIcon
    _class_icon_sm_ = blinkyIcon
    _class_background_ = 0

    _form_title_ = "Test auto column resize (NOT WORKING!)"
    
    def __init__(self):
        form.Form.__init__(self)      

        aList = MyList(parent = self, orExStyle = WS_EX_CLIENTEDGE)
        aList.InsertColumns(columnDefs)
        for i in range(100):
            aList.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])

        self.controls.Add(form.CTRL_VIEW, aList)

if __name__ == '__main__':
    mainForm = MyForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()
