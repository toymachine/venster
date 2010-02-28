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

from windows import *
from ctypes import *
from comtypes import IUnknown, STDMETHOD, GUID

##CTYPES, which of the struff below should be in ctypes.ole ??
OLESTR = c_wchar
OLECHAR = c_wchar

class IDataObject(IUnknown):
    _iid_ = GUID("{0000010E-0000-0000-C000-000000000046}")

class IDropSource(IUnknown):
    _iid_ = GUID("{00000121-0000-0000-C000-000000000046}")

class IDropTarget(IUnknown):
    _iid_ = GUID("{00000122-0000-0000-C000-000000000046}")
    
class IEnumFORMATETC(IUnknown):
    _iid_ = GUID("{00000103-0000-0000-C000-000000000046}")

class IAdviseSink(IUnknown):
    _iid_ = GUID("{0000010F-0000-0000-C000-000000000046}")

class IEnumSTATDATA(IUnknown):
    _iid_ = GUID("{00000105-0000-0000-C000-000000000046}")

    
class DVTARGETDEVICE(Structure):
    _fields_ = [("tdSize", DWORD),
                ("tdDriverNameOffset", WORD),
                ("tdDeviceNameOffset", WORD),
                ("tdPortNameOffset", WORD),
                ("tdExtDevmodeOffset", WORD),
                ("tdData", BYTE)]
    
class FORMATETC(Structure):
    _fields_ = [("cfFormat", CLIPFORMAT),
                ("ptd", POINTER(DVTARGETDEVICE)),
                ("dwAspect", DWORD),
                ("lindex", LONG),
                ("tymed", DWORD)]

    
class STGMEDIUM(Structure):
    _fields_ = [("tymed", DWORD),
                ("handle", HANDLE), #actually its a much more complicated union!
                ("pUnkForRelease", POINTER(IUnknown))]

DATADIR_GET = 1
DATADIR_SET = 2 

DVASPECT_CONTENT    = 1 
DVASPECT_THUMBNAIL  = 2 
DVASPECT_ICON       = 4 
DVASPECT_DOCPRINT   = 8


TYMED_HGLOBAL     = 1 
TYMED_FILE        = 2 
TYMED_ISTREAM     = 4 
TYMED_ISTORAGE    = 8 
TYMED_GDI         = 16 
TYMED_MFPICT      = 32 
TYMED_ENHMF       = 64 
TYMED_NULL        = 0 

DV_E_FORMATETC = 0x80040064
DV_E_DVTARGETDEVICE = 0x80040065
DV_E_STGMEDIUM = 0x80040066
DV_E_STATDATA = 0x80040067
DV_E_LINDEX = 0x80040068
DV_E_TYMED = 0x80040069
DV_E_CLIPFORMAT = 0x8004006A
DV_E_DVASPECT = 0x8004006B
DV_E_DVTARGETDEVICE_SIZE = 0x8004006C
DV_E_NOIVIEWOBJECT = 0x8004006D

DROPEFFECT_NONE   = 0 
DROPEFFECT_COPY   = 1 
DROPEFFECT_MOVE   = 2 
DROPEFFECT_LINK   = 4 
DROPEFFECT_SCROLL = 0x80000000 

DRAGDROP_S_DROP = 0x00040100
DRAGDROP_S_CANCEL = 0x00040101
DRAGDROP_S_USEDEFAULTCURSORS = 0x00040102


IDataObject._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetData", [POINTER(FORMATETC), POINTER(STGMEDIUM)]),
    STDMETHOD(HRESULT, "GetDataHere", [POINTER(FORMATETC), POINTER(STGMEDIUM)]),
    STDMETHOD(HRESULT, "QueryGetData", [POINTER(FORMATETC)]),
    STDMETHOD(HRESULT, "GetCanonicalFormatEtc", [POINTER(FORMATETC), POINTER(FORMATETC)]),
    STDMETHOD(HRESULT, "SetData", [POINTER(FORMATETC), POINTER(STGMEDIUM), BOOL]),
    STDMETHOD(HRESULT, "EnumFormatEtc", [DWORD, POINTER(POINTER(IEnumFORMATETC))]),
    STDMETHOD(HRESULT, "DAdvise", [POINTER(FORMATETC), DWORD, POINTER(IAdviseSink), POINTER(DWORD)]),
    STDMETHOD(HRESULT, "DUnadvise", [DWORD]),
    STDMETHOD(HRESULT, "EnumDAdvise", [POINTER(POINTER(IEnumSTATDATA))])]

IDropSource._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "QueryContinueDrag", [BOOL, DWORD]),
    STDMETHOD(HRESULT, "GiveFeedback", [DWORD])]

IDropTarget._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "DragEnter", [POINTER(IDataObject), DWORD, POINTL, POINTER(DWORD)]),
    STDMETHOD(HRESULT, "DragOver", [DWORD, POINTL, POINTER(DWORD)]),
    STDMETHOD(HRESULT, "DragLeave",[]),
    STDMETHOD(HRESULT, "Drop", [POINTER(IDataObject), DWORD, POINTL, DWORD])]

IEnumFORMATETC._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", [ULONG, POINTER(FORMATETC), POINTER(ULONG)]),
    STDMETHOD(HRESULT, "Skip", [ULONG]),
    STDMETHOD(HRESULT, "Reset",[]),
    STDMETHOD(HRESULT, "Clone", [POINTER(IEnumFORMATETC)])]

Initialize = windll.ole32.OleInitialize
SetClipboard = windll.ole32.OleSetClipboard    
GetClipboard = windll.ole32.OleGetClipboard
RegisterDragDrop = windll.ole32.RegisterDragDrop
RevokeDragDrop = windll.ole32.RevokeDragDrop
DoDragDrop = windll.ole32.DoDragDrop
