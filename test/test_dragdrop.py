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

## THIS SAMPLE IS NOT WORKING!!

from venster.windows import *
from venster.wtl import *

from venster import atl
from venster import comctl
from venster import gdi
from venster import comdlg

from venster.lib import notebook
from venster.lib import form
from venster.lib import splitter
from venster.lib import tree
from venster.lib import list

from venster.lib.ole import *

from comtypes import COMObject

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)


class Factory(object):
    def LockServer(self, arg, arg2):
        pass

class MyDataObject(SimpleDataObjectImpl):
    _clipboard_format_ = 'test_dragdrop'
    
class DropSourceImpl(COMObject):
    _com_interfaces_ = [IDropSource]
    _factory = Factory()

    ###############
    ## IDropSource:
    def GiveFeedback(self, this, dwEffect):
        #print "giveFeedback", dwEffect
        return DRAGDROP_S_USEDEFAULTCURSORS

    def QueryContinueDrag(self, this, fEscapePressed, grfKeyState):
        #print "qcd", fEscapePressed, grfKeyState
        if fEscapePressed:
            return DRAGDROP_S_CANCEL
        elif not (grfKeyState & MK_LBUTTON):
            return DRAGDROP_S_DROP
        else:
            return S_OK

        
class Tree(tree.Tree, COMObject):
    _com_interfaces_ = [IDropTarget]

    _factory = Factory()
    
    def __init__(self, *args, **kwargs):
        tree.Tree.__init__(self, *args, **kwargs)
        COMObject.__init__(self)
        
        RegisterDragDrop(self.handle, byref(self._com_pointers_[0][1]))
        
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
        hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, item)
        for i in range(100):
            item.mask = 0
            item.text = "A child %d" % i
            item.image = 3
            item.selectedImage = 4            
            hChild = self.InsertItem(hRoot, comctl.TVI_LAST, item)
        self.SetRedraw(1)

    def dispose(self):
        RevokeDragDrop(self.handle)

class List(list.List, COMObject):
    _com_interfaces_ = [IDropTarget]
    _factory = Factory()
    
    def __init__(self, *args, **kwargs):
        list.List.__init__(self, *args, **kwargs)
        COMObject.__init__(self)

        RegisterDragDrop(self.handle, byref(self._com_pointers_[0][1]))

        self.InsertColumns([("blaat", 100), ("col2", 150)])
        self.SetRedraw(0)
        for i in range(100):
            self.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])
        self.SetRedraw(1)

    def dispose(self):
        RevokeDragDrop(self.handle)

    def OnBeginDrag(self, event):
        print "obd"
        dataObject = MyDataObject(lambda: "blaat")
        dropSource = DropSourceImpl()
        dwEffect = DWORD()

        print id(dataObject)
        print id(dropSource)
        print dwEffect

        DoDragDrop(byref(dataObject._com_pointers_[0][1]),
                   byref(dropSource._com_pointers_[0][1]),
                   DROPEFFECT_COPY | DROPEFFECT_MOVE, byref(dwEffect))

        print dataObject._refcnt
        print dropSource._refcnt

    
    ntf_handler(comctl.LVN_BEGINDRAG)(OnBeginDrag)

    ###############
    ## IDropTarget:
    def DragEnter(self, this, pDataObject, grfKeyState, pt, pdwEffect):
        print pDataObject.AddRef()
        print "DragEnter", self, this, pt, pdwEffect
        if grfKeyState & MK_CONTROL:
            pdwEffect.contents = DWORD(DROPEFFECT_COPY)
        else:
            pdwEffect.contents = DWORD(DROPEFFECT_MOVE)

        return S_OK

    def DragOver(self, this, grfKeyState, pt, pdwEffect):
        print "DragOver", self, this, pt, pdwEffect
        if grfKeyState & MK_CONTROL:
            pdwEffect.contents = DWORD(DROPEFFECT_COPY)
        else:
            pdwEffect.contents = DWORD(DROPEFFECT_MOVE)
        return S_OK
        
    def DragLeave(self, this):
        print "DragLeave"
        return S_OK


    def Drop(self, this, pDataObject, grfKeyState, pt, pdwEffect):
        print pDataObject.AddRef()
        print "Drop"
        return S_OK

class Form(form.Form):
    _window_icon_sm_ = _window_icon_ = Icon("COW.ICO")

    _window_title_ = "Drag and Drop Sample"

    _form_menu_ = [(MF_POPUP, "&File",
                    [(MF_STRING, "&New\bCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR,),
                     (MF_STRING, "&Exit", form.ID_EXIT)])]
    
    def OnCreate(self, event):
        aList = List(parent = self, orExStyle = WS_EX_CLIENTEDGE)
        aTree = Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE)
        
        aSplitter = splitter.Splitter(parent = self, splitPos = 150)
        aSplitter.Add(0, aTree)
        aSplitter.Add(1, aList)

        self.controls.Add(form.CTRL_VIEW, aSplitter)
        self.controls.Add(aTree)
        self.controls.Add(aList)

    def OnNew(self, event):
        newForm = Form()
        newForm.ShowWindow()

    cmd_handler(form.ID_NEW)(OnNew)


mainForm = Form()
mainForm.ShowWindow()
Run()

#data object can also be used to support clipboard operations:    
## dataObject = MyDataObject(lambda: "blaat")
## dataObject.SetClipboard()
## assert dataObject.DataAvailable
## print dataObject.GetClipboard()


