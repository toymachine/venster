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
from venster import atl
from venster.lib import form


from ctypes import *
from comtypes.client import GetEvents, wrap

class FlashWindow(atl.AxWindow):
    def __init__(self, *args, **kwargs):
        atl.AxWindow.__init__(self, "ShockwaveFlash.ShockwaveFlash", *args, **kwargs)

        pUnk = self.GetControl()
        #get the Flash interface of the control
        pFlash = wrap(pUnk) # XXX replace 'wrap' with 'GetBestInterface'

        #receive events
        self.flashEvents = GetEvents(pFlash, self)

        #start the flash movie
        import os
        pFlash.LoadMovie(0, os.getcwd() + os.sep + "cow.swf")
        pFlash.Play()

    def _IShockwaveFlashEvents_OnReadyStateChange(self, this, state):
        # flash event handler
        print "OnReadyStateChange: ", state

    def dispose(self):
        #disconnect connectionpoint
        del self.flashEvents
        atl.AxWindow.dispose(self)

        
class MyForm(form.Form):
    _window_icon_ = _window_icon_sm_ = Icon("COW.ICO")
    
    _window_title_ = "Venster Flash Player"
    
    def OnCreate(self, event):
        self.controls.Add(form.CTRL_VIEW, FlashWindow(parent = self))

if __name__ == '__main__':
    mainForm = MyForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()

