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

## example of simplest 'pure' win32 windows application

from venster.windows import *
from venster.gdi import *
from venster.wtl import *

class MyWindow(Window):
    _window_title_ = "Minimal Venster Window Example"
    _window_background_ = GetStockObject(WHITE_BRUSH)
    _window_icon_ = _window_icon_sm_ = Icon("blinky.ico")

    @msg_handler(WM_DESTROY)
    def OnDestroy(self, event):
        application.Quit()

if __name__ == '__main__':     
    myWindow = MyWindow()
    application = Application()
    application.Run()

    



                              


