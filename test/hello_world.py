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

from venster import gdi

class MyWindow(Window):
    _window_title_ = "Hello World"
    _window_background_ = gdi.GetStockObject(WHITE_BRUSH)
    _window_class_style_ = CS_HREDRAW | CS_VREDRAW 

    #@msg_handler(WM_PAINT) #python 2.4 style decorator
    def OnPaint(self, event):
        ps = PAINTSTRUCT()
        hdc = self.BeginPaint(ps)
        rc = self.GetClientRect()

        msg = "Hello World"
        gdi.TextOut(hdc, rc.width / 2, rc.height / 2, msg, len(msg))
        
        self.EndPaint(ps)

    msg_handler(WM_PAINT)(OnPaint) #python 2.3 style decorator

        
    def OnDestroy(self, event):
        PostQuitMessage(NULL)

    msg_handler(WM_DESTROY)(OnDestroy)

myWindow = MyWindow()

application = Application()
application.Run()

    



                              


