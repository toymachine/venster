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

from venster.ole import *
from comtypes import COMObject
from comtypes.hresult import S_OK

##CTYPES:
S_FALSE = 1 #TODO move to ctypes

#initialize OLE whenever this module is imported...
Initialize(0)

class Factory(object):
    def LockServer(self, arg, arg2):
        pass

class SimpleEnumFORMATETCImpl(COMObject):
    _com_interfaces_ = [IEnumFORMATETC]

    _factory = Factory()
    
    def __init__(self, cfFormat):
        COMObject.__init__(self)
        self.cfFormat = cfFormat
        self.i = 0
        
    def Reset(self, this):
        self.i = 0
        return S_OK

    def Next(self, this, celt, rgelt, pceltFetched):
        if self.i:
            return S_FALSE
        else:
            rgelt.contents.cfFormat = self.cfFormat
            rgelt.contents.dwAspect = DVASPECT_CONTENT
            rgelt.contents.lindex = -1
            rgelt.contents.tymed = TYMED_HGLOBAL
            self.i = 1
            return S_OK
    
class SimpleDataObjectImpl(COMObject):
    _com_interfaces_ = [IDataObject]
    _clipboard_format_ = "SimpleDataObjectImplClipboardFormat"

    _factory = Factory()
    
    def __init__(self, dataFunc):
        COMObject.__init__(self)
        self.cfFormat = RegisterClipboardFormat(self._clipboard_format_)
        self.dataFunc = dataFunc

    def SetClipboard(self):
        iDataObject = self._com_pointers_[0][1]
        SetClipboard(byref(iDataObject))

    def _getFORMATETC(self):
        pIDataObject = POINTER(IDataObject)()
        GetClipboard(byref(pIDataObject))
        pIEnumFORMATETC = POINTER(IEnumFORMATETC)()
        pIDataObject.EnumFormatEtc(DATADIR_GET, byref(pIEnumFORMATETC))
        fmt = FORMATETC()
        celtFetched = ULONG()
        hres = pIEnumFORMATETC.Reset()
        while 1:
            hres = pIEnumFORMATETC.Next(1, byref(fmt), byref(celtFetched))
            if hres == S_OK:
                if fmt.cfFormat == self.cfFormat:
                    return fmt, pIDataObject
            else:
                break
        
    DataAvailable = property(lambda self: self._getFORMATETC != None)

    def GetClipboard(self):
        dataAvailable = self._getFORMATETC()
        if dataAvailable == None: return None
        fmt, pIDataObject = dataAvailable
        med = STGMEDIUM()
        
        pIDataObject.GetData(byref(fmt), byref(med))
        if not med.handle: return None
        pBuff = GlobalLock(med.handle)
        if not pBuff: return None
        dataLen = DWORD.from_address(pBuff).value
        strData = ((c_char * (dataLen)).from_address(pBuff + sizeof(DWORD))).value
        GlobalUnlock(med.handle)
        GlobalFree(med.handle)
        return strData

    ######################################################################
    ## IDataObject:
    def EnumFormatEtc(self, this, dwDirection, ppenumFormatetc):
        print "efe"
        if dwDirection == DATADIR_GET:
            enumFormatEtc = SimpleEnumFORMATETCImpl(self.cfFormat)
            iEnumFormatEtc = enumFormatEtc._com_pointers_[0][1]
            # We don't do it this way, because it confuses ctypes COM
            # reference counting:
            ## ppenumFormatetc.contents = pointer(iEnumFormatEtc)

            # calculate the address (as integer) where we have to
            # store the COM pointer.
            addr = c_voidp.from_address(addressof(ppenumFormatetc)).value
            
            # calculate (as integer, again), the value we have to store there
            ptr = addressof(iEnumFormatEtc)

            # store it away
            c_voidp.from_address(addr).value = ptr

            # I think we have to call AddRef two times:
            # the first one because the object is created with an
            # initial refcount of 0, wich is wrong.
            enumFormatEtc.AddRef(None)
            # the second one because we hand out a reference
            #enumFormatEtc.AddRef(None)
            return S_OK
        else:
            return E_NOTIMPL

    def QueryGetData(self, this, pFormatetc):
        print "qgd"
        if pFormatetc.contents.cfFormat != self.cfFormat:
            return DV_E_FORMATETC
        elif pFormatetc.contents.dwAspect != DVASPECT_CONTENT:
            return DV_E_DVASPECT
        elif pFormatetc.contents.lindex != -1:
            return DV_E_LINDEX
        elif pFormatetc.contents.tymed != TYMED_HGLOBAL:
            return DV_E_TYMED
        else:
            return S_OK
        
            
    def GetData(self, this, pFormatetc, pMedium):
        print "gd"
        hres = self.QueryGetData(this, pFormatetc)
        if hres != S_OK: return hres
        strData = str(self.dataFunc())
        hClipboardData = GlobalAlloc(GMEM_DDESHARE, len(strData) + 1 + sizeof(DWORD))        
        if not hClipboardData: raise "could not allocate global mem"
        pClipboardData = GlobalLock(hClipboardData)
        if not pClipboardData: raise "could not lock global mem"
        #set length of data at front
        DWORD.from_address(pClipboardData).value = len(strData)
        #copy...
        buff = (c_char * (len(strData) + 1)).from_address(pClipboardData + sizeof(DWORD))
        buff.value = strData + '\0'
        if not GlobalUnlock(hClipboardData): raise "could not unlock clipboard data"
        pMedium.contents.handle = hClipboardData
        return S_OK
        
