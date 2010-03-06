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
from venster import comdlg

from venster.lib import notebook
from venster.lib import form
from venster.lib import splitter
from venster.lib import tree
from venster.lib import list
from venster.lib import browser

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

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
        hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, item)
        for i in range(100):
            item.mask = 0
            item.text = "A child %d" % i
            item.image = 3
            item.selectedImage = 4            
            hChild = self.InsertItem(hRoot, comctl.TVI_LAST, item)
        self.SetRedraw(1)


    def OnItemExpanding(self, event):
        print "item expanding"

    ntf_handler(comctl.TVN_ITEMEXPANDING)(OnItemExpanding)

    def OnSelectionChanged(self, event):
        print "on sel changed"
        nmtv = event.structure(comctl.NMTREEVIEW)
        print nmtv.ptDrag

    ntf_handler(comctl.TVN_SELCHANGED)(OnSelectionChanged)
                         

class Form(form.Form):
    _window_icon_ = Icon("COW.ICO")
    _window_icon_sm_ = _window_icon_
    _window_title_ = "Supervaca al Rescate!"

    _form_accels_ = [(FCONTROL|FVIRTKEY, ord("O"), form.ID_OPEN),
                      (FCONTROL|FVIRTKEY, ord("N"), form.ID_NEW)]
    
    _form_exit_ = form.EXIT_ONLASTDESTROY

    _form_status_msgs_ = {form.ID_NEW: "Creates a new window.",
                          form.ID_OPEN: "Frobnicates a new Widget!"}

    _form_menu_ = [(MF_POPUP, "&File", 
                    [(MF_STRING, "&New\tCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR, ),
                     (MF_STRING, "&Open\tCtrl+O", form.ID_OPEN),
                     (MF_STRING, "&Save...\tCtrl+S", form.ID_SAVE),
                     (MF_STRING, "&Save As...", form.ID_SAVEAS),
                     (MF_SEPARATOR, ),
                     (MF_POPUP, "Sub", 
                      [(MF_STRING, "sub1", 0),
                       (MF_STRING, "sub2", 0)]),
                     (MF_SEPARATOR, ),
                     (MF_STRING, "&Exit", form.ID_EXIT)
                     ]),
                   (MF_POPUP, "&Edit", 
                    [(MF_STRING, "&Undo\bCtrl-Z", form.ID_UNDO),
                     (MF_STRING, "&Redo", form.ID_REDO)])
                   ]

    def OnCreate(self, event):
        noteBook = notebook.NoteBook(parent = self, orExStyle = WS_EX_CLIENTEDGE)
        
        aBrowser = browser.Browser("http://www.python.org", parent = noteBook,
                                   orExStyle = WS_EX_CLIENTEDGE)
        
        aList = list.List(parent = noteBook, orExStyle = WS_EX_CLIENTEDGE)
        
        aList.InsertColumns([("blaat", 100), ("col2", 150)])
        aList.SetRedraw(0)
        for i in range(100):
            aList.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])
        aList.SetRedraw(1)
    
        
        noteBook.AddTab(0, "blaat1", aBrowser)
        noteBook.AddTab(1, "blaat2", aList)

        aTree = Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE)

        aSplitter = splitter.Splitter(parent = self, splitPos = 150)
        aSplitter.Add(0, aTree)
        aSplitter.Add(1, noteBook)

        self.controls.Add(aList)
        self.controls.Add(aBrowser)
        self.controls.Add(noteBook)
        self.controls.Add(form.CTRL_STATUSBAR, comctl.StatusBar(parent = self))
        self.controls.Add(form.CTRL_VIEW, aSplitter)
        
    def OnNew(self, event):
        form = Form()
        form.ShowWindow()

    cmd_handler(form.ID_NEW)(OnNew)
    
    def OnOpen(self, event):
        ofn = comdlg.OpenFileDialog()
        ofn.filter = "Blaat Document (*.bla)|*.bla|All files (*.*)|*.*"
        #TODO: flags dont' work!
        ofn.Flags = comdlg.OFN_FILEMUSTEXIST|comdlg.OFN_PATHMUSTEXIST
        print ofn.DoModal(parent = self)

    cmd_handler(form.ID_OPEN)(OnOpen)
   

mainForm = Form()
mainForm.ShowWindow()
Run()
