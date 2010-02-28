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
from ctypes import *

def ValidHandle(value):
    if value != 0:
        raise "fout"
    else:
        return value

KEY_READ = 0x20019

HKEY_CLASSES_ROOT   =   0x80000000
HKEY_CURRENT_USER   =   0x80000001
HKEY_LOCAL_MACHINE  =   0x80000002

REG_NONE = 0
REG_SZ = 1

RegOpenKeyEx = windll.advapi32.RegOpenKeyExA
RegOpenKeyEx.restype = ValidHandle

RegQueryValueEx = windll.advapi32.RegQueryValueExA
RegCloseKey = windll.advapi32.RegCloseKey
