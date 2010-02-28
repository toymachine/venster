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
from venster.atl import *

from venster.lib import form

class Static(Window):
    _class_ = 'static'
    _class_ws_style_ = WS_CHILD | WS_VISIBLE
    
class MyForm(form.Form):
    def __init__(self):
        form.Form.__init__(self, title = "Static windows test (NOT WORKING)")      

        ## why can't static be child of other static??
        
        #aStatic1 = Static(parent = self)
        #aStatic1.SetText('blaat1')
        #print aStatic1.handle
        
        aStatic2 = Static(parent = self)
        aStatic2.SetText('blaat2')
        
        aStatic2.MoveWindow(100, 100, 200, 200, 1)
        aStatic2.UpdateWindow()
##         aStatic2.ShowWindow()
##         aStatic2.SetWindowPos(0, 100, 100, 200, 200,
##                               SWP_NOACTIVATE|SWP_NOZORDER)
        
        #aStatic2.SetWindowPos(HWND_TOP, 0, 0, 0, 0,
        #                      SWP_NOACTIVATE|SWP_NOMOVE|SWP_NOREDRAW|SWP_NOSIZE)



        #self.controls.Add(form.CTRL_VIEW, aStatic2)

    def OnSize(self, event):
        print "onsize"
        form.Form.OnSize(self, event)
        #self.controls[form.CTRL_VIEW].MoveWindow(10,10,100,100,1)

mainForm = MyForm()        
mainForm.ShowWindow()

Run()
