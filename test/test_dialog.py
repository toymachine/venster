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
from venster.dialog import *
from venster import comctl


RESDLL = "resdll\\Release\\resdll.dll"
IDD_EXAMPLE_1 = "#101"


class ExampleDialog(Dialog):    
    _dialog_module_ = RESDLL
    _dialog_id_ = IDD_EXAMPLE_1

    #controls ID as defined in resource dll:
    IDC_EDIT_A = 1000
    IDC_EDIT_B = 1001
    IDC_BUTTON_SUM = 1002
    IDC_EDIT_SUM = 1003
    IDC_EDIT_EVAL = 1004
    IDC_EDIT_EVAL_RES = 1006

    def OnSum(self, event):
        #get the values from box A and B and put the sum in the result box
        try:
            a = float(self.ctrlEditA.GetText())
            b = float(self.ctrlEditB.GetText())
            c = str(a + b)
        except:
            c = "Error!"
            
        self.ctrlEditSum.SetText(c)

    cmd_handler(IDC_BUTTON_SUM)(OnSum)

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

    cmd_handler(IDC_EDIT_EVAL, EN_CHANGE)(OnEval)

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

                      
