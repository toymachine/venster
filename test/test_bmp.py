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
from venster.lib import form

from venster import gdi

class MyForm(form.Form):
    _window_icon_ = Icon("blinky.ico")
    _window_icon_sm_ = _window_icon_
    _window_background_ = 0 #prevents windows from redrawing background, prevent flicker
    _window_class_style_ = CS_HREDRAW | CS_VREDRAW#make windows invalidate window on resize

    _window_title_ = "Real Slick Looking Windows Application in 100% Python"
    
    def __init__(self):
        form.Form.__init__(self)      

        #find some bitmap to show:
        try:
            self.bitmap = gdi.Bitmap("test.bmp")
        except:
            try:
                self.bitmap = gdi.Bitmap("c:\\Windows\\Web\\Wallpaper\\Bliss.bmp")
            except:
                print "put a bitmap file 'test.bmp' in the current directory"
                import os
                os._exit(-1)

        #create a memory dc containing the bitmap
        self.bitmapdc = gdi.CreateCompatibleDC(NULL)
        gdi.SelectObject(self.bitmapdc, self.bitmap.handle)

    def OnPaint(self, event):
        ps = PAINTSTRUCT()
        hdc = self.BeginPaint(ps)
        
        rc = self.GetClientRect()

        #blit the in memory bitmap to the screen
        gdi.StretchBlt(hdc, 0, 0, rc.right , rc.bottom,
                       self.bitmapdc, 0, 0, self.bitmap.width, self.bitmap.height,
                       SRCCOPY)
        
        self.EndPaint(ps)

    msg_handler(WM_PAINT)(OnPaint)
    
if __name__ == '__main__':
    mainForm = MyForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()
