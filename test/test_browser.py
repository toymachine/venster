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
from venster.lib import form
from venster.lib import dispatch
from venster.lib import browser
from venster.lib.browser import IDocHostUIHandler, ICustomDoc

from ctypes.com.automation import IDispatch, VARIANT
from ctypes.com import IUnknown, STDMETHOD, HRESULT, GUID, COMObject, E_NOTIMPL, S_OK

##CTYPES, yes a default factory would be very nice:
class Factory:
    def LockServer(self, a, b):
        pass

#the methods of this object are exposed in html trough 'window.external'
class Summer(object):
    def __init__(self, handler):
        self.handler = handler
        
    def sum(self, a, b):
        return a + b

    def announce(self, element):
        print "announce", element
        self.handler.element = dispatch.wrap(element)
        
    def roundtrip(self):
        self.handler.element.value = "Hello From Python!"
        
class UIHandler(COMObject):
    _com_interfaces_ = [IDocHostUIHandler]
    _factory = Factory()

    def __init__(self, *args, **kwargs):
        COMObject.__init__(self, *args, **kwargs)
        
    def GetExternal(self, this, ppDispatch):
        print "GetExternal!"
        dispSum = dispatch.wrap(Summer(self))

        iDispSum = dispSum._com_pointers_[0][1]
        addr = c_voidp.from_address(addressof(ppDispatch)).value            
        ptr = addressof(iDispSum)
        c_voidp.from_address(addr).value = ptr
        dispSum.AddRef(None)
        dispSum.AddRef(None)
        return S_OK
##CTYPES, the above pattern for giving out a COM pointer should be
##available trough the pointer itself, e.g.
##  dispSum._com_pointers_[0][1].copyto(ppDispatch)
##  return S_OK
##        
## ideally i should not care how _com_pointers_ is implemented, rather I would access
## it as a map, keyed by interface type:
## dispSum._com_pointers_[IDispatch].copyto(ppDispatch)
## return S_OK
##
## This would also make it alot easier if a python object implements multiple interfaces
##
## e.g. pyObj._com_pointers_[ISomeIface1],
##      pyObj._com_pointers_[ISomeIface2],
##

class MyBrowser(browser.Browser):
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

    ####
    ## DWebbrowserEvents2
    ####
    def DocumentComplete(self, a, b, c):
        #print "DOCCOMP!!!", type(a), type(b), type(c)
        #tries to set custom ui handler
        pDispDocument = POINTER(IDispatch)()
        self.pBrowser._get_Document(byref(pDispDocument))
        pCustomDoc = POINTER(ICustomDoc)()
        pDispDocument.QueryInterface(byref(ICustomDoc._iid_), byref(pCustomDoc))
        self.uiHandler = UIHandler()
        self.uiHandler.AddRef(None)
        pCustomDoc.SetUIHandler(byref(self.uiHandler._com_pointers_[0][1]))
        
        
        
class MyForm(form.Form):
    _window_title_ = "Venster Explorer"
    
    def __init__(self):
        form.Form.__init__(self)      

    def OnCreate(self, event):
        aBrowser = MyBrowser(parent = self)
        self.controls.Add(form.CTRL_VIEW, aBrowser)
        self.controls.Add(form.CTRL_STATUSBAR, comctl.StatusBar(parent = self))

        import os
        aBrowser.Navigate("%s%stest_html.html" % (os.getcwd(), os.sep))


if __name__ == '__main__':
    mainForm = MyForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()
