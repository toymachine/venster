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

from venster.lib import splitter
from venster.lib import form
from venster.lib import list

def createTestChild(parent):

    lst = list.List(parent = parent, orExStyle = WS_EX_CLIENTEDGE)
    lst.InsertColumns([("blaat", 100), ("col2", 150)])
    for i in range(20):
        lst.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])

    return lst

class MyForm(form.Form):
    _form_title_ = "Splitter Wnd test"
    
    def __init__(self):
        form.Form.__init__(self)      

        aSplitter1 = splitter.Splitter(parent = self,
                                       splitPos = self.clientRect.width / 2)

        aSplitter2 = splitter.Splitter(parent = aSplitter1,
                                       orientation = splitter.HORIZONTAL,
                                       splitPos = self.clientRect.width / 4)

        aSplitter3 = splitter.Splitter(parent = aSplitter1,
                                       orientation = splitter.HORIZONTAL,
                                       splitPos = self.clientRect.width / 4)


        child1 = createTestChild(aSplitter1)
        child2 = createTestChild(aSplitter1)
        child3 = createTestChild(aSplitter1)
        child4 = createTestChild(aSplitter1)
        
        aSplitter2.Add(0, child1)
        aSplitter2.Add(1, child2)

        aSplitter3.Add(0, child3)
        aSplitter3.Add(1, child4)

        aSplitter1.Add(0, aSplitter2)
        aSplitter1.Add(1, aSplitter3)
        
        self.controls.Add(child1)
        self.controls.Add(child2)
        self.controls.Add(child3)
        self.controls.Add(child4)
        self.controls.Add(aSplitter2)
        self.controls.Add(aSplitter3)

        self.controls.Add(form.CTRL_VIEW, aSplitter1)

if __name__ == '__main__':
    mainForm = MyForm()
    mainForm.ShowWindow()

    application = Application()
    application.Run()

