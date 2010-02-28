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

WND_CLASS_NAME = "TestWindowClass"
hInstance = GetModuleHandle(0)

def wndProc(hWnd, nMsg, wParam, lParam):
    if nMsg == WM_DESTROY:
        PostQuitMessage(0)
        return 0
    else:
        return DefWindowProc(hWnd, nMsg, wParam, lParam)
    
cls = WNDCLASSEX()
cls.cbSize = 48
cls.lpszClassName = WND_CLASS_NAME
cls.hInstance = hInstance
cls.lpfnWndProc = WndProc(wndProc)
cls.style = CS_HREDRAW | CS_VREDRAW
cls.hbrBackground = GetStockObject(WHITE_BRUSH)
cls.hIcon = LoadIcon(0, IDI_APPLICATION)
cls.hIconSm = LoadIcon(0, IDI_APPLICATION)
cls.hCursor = LoadCursor(0, IDC_ARROW)


atom = RegisterClassEx(byref(cls))
hWnd = CreateWindowEx(0,
                      WND_CLASS_NAME,
                      "Test Window",
                      WS_OVERLAPPEDWINDOW,
                      10,
                      10,
                      320,
                      200,
                      0,
                      0,
                      0,
                      0)


ShowWindow(hWnd, SW_SHOW)
UpdateWindow(hWnd)

msg = MSG()
lpmsg = byref(msg)

while GetMessage(lpmsg, 0, 0, 0):
    TranslateMessage(lpmsg)
    DispatchMessage(lpmsg)
    



                              


