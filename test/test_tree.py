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

from venster.lib import tree
from venster.lib import form

from ctypes import *

blinkyIcon = Icon("blinky.ico")

import sys
if sys.version_info[0:2] == (2, 2):
    pythonDll = cdll.python22
elif sys.version_info[0:2] == (2, 3):
    pythonDll = cdll.python23
    
def as_pointer(obj):
    "Increment the refcount of obj, and return a pointer to it"
    ptr = pythonDll.Py_BuildValue("O", id(obj))
    assert ptr == id(obj)
    return ptr

def from_pointer(ptr):
    "Convert a pointer to a Python object, and decrement the refcount of the ptr"
    l = [None]
    # PyList_SetItem consumes a refcount of its 3. argument
    pythonDll.PyList_SetItem(id(l), 0, ptr)
    return l[0]

class TestItem:
    def __del__(self):
        #print "del ti"
        pass

class Tree(tree.Tree):
    def __init__(self, *args, **kwargs):
        tree.Tree.__init__(self, *args, **kwargs)

        self.iml = comctl.ImageList(16, 16, ILC_COLOR32 | ILC_MASK, 0, 32)
        self.iml.AddIconsFromModule("shell32.dll", 16, 16, LR_LOADMAP3DCOLORS)
        self.iml.SetBkColor(gdi.CLR_NONE)
        self.SetImageList(self.iml)

        self.SetRedraw(0)
        item = comctl.TVITEMEX()
        item.text = "A root"
        item.image = 17
        item.selectedImage = 17
        item.children = 1        
        self.hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, item)
        for i in range(1):
            item = comctl.TVITEMEX()
            item.text = "A child %d" % i
            item.image = 3
            item.selectedImage = 4
            item.children = 0
            hChild = self.InsertItem(self.hRoot, comctl.TVI_LAST, item)
        self.SetRedraw(1)

    def OnItemExpanding(self, event):
        nmtv = comctl.NMTREEVIEW.from_address(int(event.lParam))
        if nmtv.action == comctl.TVE_EXPAND:            
            for i in range(100):
                ti = TestItem()
                item = comctl.TVITEMEX()
                item.text = "A child %d" % i
                item.image = 3
                item.selectedImage = 4
                item.children = 0
                item.param = as_pointer(ti)
                self.InsertItem(self.hRoot, comctl.TVI_LAST, item)
        elif nmtv.action == comctl.TVE_COLLAPSE:
            self.CollapseAndReset(nmtv.itemNew.hItem)

    def OnSelectionChanged(self, event):
        #print "on sel changed"
        nmtv = comctl.NMTREEVIEW.from_address(int(event.lParam))

    def OnDeleteItem(self, event):
        #print "del item"
        nmtv = comctl.NMTREEVIEW.from_address(int(event.lParam))
        i = nmtv.itemOld.lParam
        if i != 0:
            ti = from_pointer(i)
            #print ti
        
    _msg_map_ = MSG_MAP([NTF_HANDLER(comctl.TVN_ITEMEXPANDING, OnItemExpanding),
                         NTF_HANDLER(comctl.TVN_SELCHANGED, OnSelectionChanged),
                         NTF_HANDLER(comctl.TVN_DELETEITEM, OnDeleteItem)])

class MyForm(form.Form):
    _class_icon_ = blinkyIcon
    _class_icon_sm_ = blinkyIcon
    _form_title_ = "Tree Test (Puts references to Python instances in treenodes)"
    
    def __init__(self):
        form.Form.__init__(self)      
        self.controls.Add(form.CTRL_VIEW, Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE))

if __name__ == '__main__':
    mainForm = MyForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()
