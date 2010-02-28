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

from windows import *
from ctypes import *
import wtl

AtlAxWinInit = windll.atl.AtlAxWinInit
AtlAxGetControl = windll.atl.AtlAxGetControl

from comtypes import IUnknown

class AxWindow(wtl.Window):
    _class_ = "AtlAxWin"
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
    
    def __init__(self, ctrlId, *args, **kwargs):
        """ctrlId can be progId, clsId or url"""
        AtlAxWinInit()
        kwargs['title'] = ctrlId
        #AtlAxWin window class uses title to instantiate activex control
        #can be either progid, clsid or url (start browser control)
        wtl.Window.__init__(self, *args, **kwargs)

    def GetControl(self):
        """gets the IUnknown interface of the activex control"""
        pUnk = POINTER(IUnknown)()
        AtlAxGetControl(self.handle, byref(pUnk))
        return pUnk
