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

#TODO wrap shBrowseForFolder directory selection dialog

from windows import *
from wtl import *
from ctypes import *

LPOFNHOOKPROC = c_voidp #TODO

class OPENFILENAME(Structure):
    _fields_ = [("lStructSize", DWORD),
                ("hwndOwner", HWND),
                ("hInstance", HINSTANCE),
                ("lpstrFilter", LPCTSTR),
                ("lpstrCustomFilter", LPTSTR),
                ("nMaxCustFilter", DWORD),
                ("nFilterIndex", DWORD),
                ("lpstrFile", LPTSTR),
                ("nMaxFile", DWORD),
                ("lpstrFileTitle", LPTSTR),
                ("nMaxFileTitle", DWORD),
                ("lpstrInitialDir", LPCTSTR),
                ("lpstrTitle", LPCTSTR),
                ("flags", DWORD),
                ("nFileOffset", WORD),
                ("nFileExtension", WORD),
                ("lpstrDefExt", LPCTSTR),
                ("lCustData", LPARAM),
                ("lpfnHook", LPOFNHOOKPROC),
                ("lpTemplateName", LPCTSTR),
                ("pvReserved", LPVOID),
                ("dwReserved", DWORD),
                ("flagsEx", DWORD)]

GetOpenFileName = windll.comdlg32.GetOpenFileNameA
GetSaveFileName = windll.comdlg32.GetSaveFileNameA

OFN_ALLOWMULTISELECT = 512
OFN_CREATEPROMPT= 0x2000
OFN_ENABLEHOOK =32
OFN_ENABLETEMPLATE= 64
OFN_ENABLETEMPLATEHANDLE= 128
OFN_EXPLORER= 0x80000
OFN_EXTENSIONDIFFERENT= 0x400
OFN_FILEMUSTEXIST =0x1000
OFN_HIDEREADONLY= 4
OFN_LONGNAMES =0x200000
OFN_NOCHANGEDIR= 8
OFN_NODEREFERENCELINKS= 0x100000
OFN_NOLONGNAMES= 0x40000
OFN_NONETWORKBUTTON =0x20000
OFN_NOREADONLYRETURN= 0x8000
OFN_NOTESTFILECREATE= 0x10000
OFN_NOVALIDATE= 256
OFN_OVERWRITEPROMPT= 2
OFN_PATHMUSTEXIST= 0x800
OFN_READONLY= 1
OFN_SHAREAWARE= 0x4000
OFN_SHOWHELP= 16
OFN_SHAREFALLTHROUGH= 2
OFN_SHARENOWARN= 1
OFN_SHAREWARN= 0
OFN_NODEREFERENCELINKS = 0x100000
OPENFILENAME_SIZE_VERSION_400 = 76


class FileDialog(OPENFILENAME):
    def SetFilter(self, filter):
        self.lpstrFilter = filter.replace('|', '\0') + '\0\0'

    filter = property(None, SetFilter, None, "")
        
    def DoModal(self, parent = None):
        szPath = '\0' * 1024
        if versionInfo.isMajorMinor(4, 0): #fix for NT4.0
            self.lStructSize = OPENFILENAME_SIZE_VERSION_400
        else:
            self.lStructSize = sizeof(OPENFILENAME)
        self.lpstrFile = szPath
        self.nMaxFile = 1024
        self.hwndOwner = handle(parent)
        try:
            #the windows file dialogs change the current working dir of the app
            #if the user selects a file from a different dir
            #this prevents that from happening (it causes al sorts of problems with
            #hardcoded relative paths)
            import os
            cwd = os.getcwd()
            if self.DoIt() != 0:
                return szPath[:szPath.find('\0')].strip()
            else:
                return None
        finally:
            os.chdir(cwd) #return to old current working dir
            
        
    
class OpenFileDialog(FileDialog):
    def DoIt(self):
        return GetOpenFileName(byref(self))

class SaveFileDialog(FileDialog):
    def DoIt(self):
        return GetSaveFileName(byref(self))
    
