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
    
class Tree(TreeView):
    def __init__(self, *args, **kwargs):
        TreeView.__init__(self, *args, **kwargs)
        self.m_interceptor = self.Intercept(self.GetParent(), self._msg_map_)

    def dispose(self):
        self.m_interceptor.dispose()
        del self.m_interceptor
        
    def SetItemText(self, item, txt):
        itemEx = TVITEMEX()
        itemEx.mask  = TVIF_TEXT
        itemEx.hItem = item
        itemEx.pszText = txt
        return self.SendMessage(TVM_SETITEM, 0, byref(itemEx))

    def GetItemData(self, hItem):
        itemEx = TVITEMEX()
        itemEx.hItem = hItem
        itemEx.mask = TVIF_PARAM
        self.GetItem(itemEx)
        return itemEx.lParam
