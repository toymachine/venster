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

from venster.lib import form
from venster.lib import splitter
from venster.lib import tree
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

        self.SetRedraw(False)

        item = comctl.TVITEMEX()
        item.text = "Bookmarks"
        item.image = 17
        item.selectedImage = 17
        item.children = 1
        hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, item)

        self.bookmarks = [('Python', 'http://www.python.org'),
                          ('Venster', 'http://venster.sourceforge.net')]
        
        for i, (text, url) in enumerate(self.bookmarks):
            item.mask = 0
            item.text = text
            item.image = 3
            item.selectedImage = 4
            item.param = i            
            hChild = self.InsertItem(hRoot, comctl.TVI_LAST, item)
            self.EnsureVisible(hChild)

        self.SetRedraw(True)


    def OnSelectionChanged(self, event):
        nmtv = comctl.NMTREEVIEW.from_address(int(event.lParam))
        i = nmtv.itemNew.lParam
        url = self.bookmarks[i][1]
        self.GetParent().Navigate(url)

    ntf_handler(comctl.TVN_SELCHANGED)(OnSelectionChanged)
                         

class Browser(browser.Browser):
    def StatusTextChange(self, this, txt):
        statusBar = self.parent.controls[form.CTRL_STATUSBAR]
        if txt:
            statusBar.Simple(1)
            statusBar.SetText(txt.encode("mbcs"))
        else:
            statusBar.Simple(0)

    def TitleChange(self, this, txt):
        form = self.parent
        try:
            form.SetText("%s - %s" % (form._window_title_, str(txt)))
        except:
            pass


class Form(form.Form):
    _window_icon_ = Icon("COW.ICO")
    _window_icon_sm_ = _window_icon_
    _window_title_ = "Supervaca al Rescate!"

    _form_accels_ = [(FCONTROL|FVIRTKEY, ord("N"), form.ID_NEW)]
    
    _form_exit_ = form.EXIT_ONLASTDESTROY

    _form_status_msgs_ = {form.ID_NEW: "Creates a new window."}

    _form_menu_ = [(MF_POPUP, "&File", 
                    [(MF_STRING, "&New\tCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR, ),
                     (MF_STRING, "&Exit", form.ID_EXIT)
                     ])]
    
    def OnCreate(self, event):
        aBrowser = Browser("http://www.python.org", parent = self, orExStyle = WS_EX_CLIENTEDGE)
        aTree = Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE)

        aSplitter = splitter.Splitter(parent = self, splitPos = 200)
        aSplitter.Add(0, aTree)
        aSplitter.Add(1, aBrowser)

        self.controls.Add("tree", aTree)
        self.controls.Add("browser", aBrowser)
        self.controls.Add(form.CTRL_STATUSBAR, comctl.StatusBar(parent = self))
        self.controls.Add(form.CTRL_VIEW, aSplitter)

    def Navigate(self, url):
        self.controls["browser"].Navigate(url)
        
    def OnNew(self, event):
        newForm = Form()

    cmd_handler(form.ID_NEW)(OnNew)
    

if __name__ == '__main__':
    mainForm = Form()        
    application = Application()
    application.Run()
