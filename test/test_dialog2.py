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

## This example shows how to layout and show a dialog in Venster.
## Thanx to Brad Clements for this contribution!

from venster.wtl import *
from venster.dialog import *

class ExampleDialog(Dialog):    
    IDC_EDIT_A = 1000
    IDC_EDIT_B = 1001
    IDC_BUTTON_SUM = 1002
    IDC_EDIT_SUM = 1003
    IDC_EDIT_EVAL = 1004
    IDC_EDIT_EVAL_RES = 1006

    items = [
        DefPushButton(title="OK", id = IDOK,
                      rcPos = RECT(left = 130, top = 185, right = 50, bottom =14 )),
        PushButton(title="Cancel", id = IDCANCEL,
                   rcPos = RECT(left = 185, top = 185, right = 50, bottom = 14)),
        GroupBox(title="Sum:",rcPos=RECT(5, 7, 230, 58)),
        EditText(orStyle = ES_AUTOHSCROLL, rcPos=RECT(40, 21, 56, 12), id=IDC_EDIT_A),
        EditText(orStyle = ES_AUTOHSCROLL, rcPos=RECT(40, 41, 56, 12), id=IDC_EDIT_B),
        PushButton(title = "Sum", rcPos = RECT(105, 19, 55, 14), id = IDC_BUTTON_SUM),        
        StaticText(title="A:", rcPos=RECT(30, 25, 8, 8)),
        StaticText(title="B:", rcPos=RECT(30, 45, 8, 8)),
        EditText(orStyle=ES_AUTOHSCROLL|ES_READONLY, rcPos=RECT(105, 41, 56, 12), id=IDC_EDIT_SUM),
        GroupBox(title="Eval:",rcPos=RECT(5, 70, 230, 110)),
        EditText(orStyle=ES_AUTOHSCROLL, rcPos=RECT(10, 82, 220, 12), id=IDC_EDIT_EVAL),
        EditText(orStyle=ES_AUTOHSCROLL|ES_MULTILINE|ES_AUTOVSCROLL|ES_READONLY|WS_VSCROLL,
                 rcPos=RECT(10, 100, 220, 75), id=IDC_EDIT_EVAL_RES),
        ]
    

    _dialog_template_ = DialogTemplate(
        title = "Venster Test Dialog2",
        style = DS_MODALFRAME|WS_POPUP|WS_CAPTION|WS_SYSMENU|DS_SETFONT,
        rcPos = RECT(left=0,top=0,right=241,bottom=206),
        items = items
        )


    def OnSum(self, event):
        #get the values from box A and B and put the sum in the result box
        try:
            a = float(self.ctrlEditA.GetText())
            b = float(self.ctrlEditB.GetText())
            c = str(a + b)
        except:
            c = "Error!"

        self.ctrlEditSum.SetText(c)

    OnSum = cmd_handler(IDC_BUTTON_SUM)(OnSum)
                   
    def OnEval(self, event):
        #evaluates the line as a python expression and show the results
        try:
            evalResult = str(eval(self.ctrlEditEval.GetText()))
        except:
            #dump the stacktrace in a string for display
            import traceback
            import StringIO
            tmp = StringIO.StringIO()
            traceback.print_exc(file = tmp)
            #multiline edit box wants '\r\n' as linebreak:
            evalResult = tmp.getvalue().replace('\n', '\r\n') 

        self.ctrlEditEvalRes.SetText(evalResult)

    OnEval = cmd_handler(IDC_EDIT_EVAL, EN_CHANGE)(OnEval)
    
    def OnInitDialog(self, event):
        Dialog.OnInitDialog(self, event)

        #Windows has created dialog controls, so obtain references here...
        self.ctrlEditA = self.GetDlgItem(self.IDC_EDIT_A, comctl.Edit)
        self.ctrlEditB = self.GetDlgItem(self.IDC_EDIT_B, comctl.Edit)
        self.ctrlEditSum = self.GetDlgItem(self.IDC_EDIT_SUM, comctl.Edit) 
        self.ctrlEditEval = self.GetDlgItem(self.IDC_EDIT_EVAL, comctl.Edit)
        self.ctrlEditEvalRes = self.GetDlgItem(self.IDC_EDIT_EVAL_RES, comctl.Edit)
        #always nice to set the focus correctly:
        self.ctrlEditA.SetFocus()

if __name__ == '__main__':
    dialog = ExampleDialog()
    #show the dialog and return the result:
    dialogResult = dialog.DoModal()
    #dialResult == IDOK if user presses 'OK', IDCANCEL when user presses 'Cancel'
