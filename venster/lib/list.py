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

class List(ListView):
    def __init__(self, *args, **kwargs):
        ListView.__init__(self, *args, **kwargs)
        #reroute all notifications to self
        self.m_interceptor = self.Intercept(self.GetParent(), self._msg_map_)

    def dispose(self):
        self.m_interceptor.dispose()
        del self.m_interceptor
        
    def InsertColumns(self, colDef):
        """inserts columns into list view, based on colDef
        colDef is a list of tuples (title, width)"""
        col = LVCOLUMN()
        i = 0
        for title, width in colDef:
            col.clear()
            col.text = title
            col.width = width
            self.InsertColumn(i, col)
            i += 1

    def SetColumns(self, colDef):
        col = LVCOLUMN()
        i = 0
        for title, width in colDef:
            col.clear()
            col.text = title
            col.width = width
            self.SetColumn(i, col)
            i += 1

    def InsertRow(self, i, row):
        """inserts a row at index i, row is a list of strings"""
        item = LVITEM()
        item.iItem = i
        item.iSubItem = 0
        item.text = row[0]
        self.InsertItem(item)
        
        for iSubItem in range(len(row) - 1):
            item.iSubItem = iSubItem + 1
            item.text = row[iSubItem + 1]
            self.SetItem(item)

    def SetRow(self, i, row):
        """sets the row at index i, row is a list of strings"""
        item = LVITEM()
        item.iItem = i
        for iSubItem in range(len(row)):
            item.iSubItem = iSubItem
            item.text = row[iSubItem]
            self.SetItem(item)
        
    def SelectAll(self):
        self.SetRedraw(0)
        self.SetItemState(-1, LVIS_SELECTED, LVIS_SELECTED)
        self.SetRedraw(1)

    def InvertSelection(self):
        self.SetRedraw(0)
        
        for i in range(self.GetItemCount()):
            if self.GetItemState(i, LVIS_SELECTED):
                self.SetItemState(i, 0, LVIS_SELECTED)
            else:
                self.SetItemState(i, LVIS_SELECTED, LVIS_SELECTED)

        self.SetRedraw(1)


    

