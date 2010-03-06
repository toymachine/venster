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

from ctypes import c_wchar_p, POINTER, byref, c_uint
from comtypes import COMObject, GUID
from comtypes.hresult import E_NOTIMPL, E_NOINTERFACE, S_OK
from comtypes.automation import *
from venster.windows import *

##CTYPES:
IID_NULL = GUID("{00000000-0000-0000-0000-000000000000}") #TODO move into ctypes

DISP_E_EXCEPTION = 0x80020009 #move into ctypes automation or?, (are from winerror.h)
DISP_E_MEMBERNOTFOUND = 0x80020003
DISP_E_BADINDEX = 0x8002000B
E_INVALID_ARG = 0x80070057

DISPID_PROPERTYPUT = -3


##CTYPES, should define a default factory
class Factory(object):
    def LockServer(self, arg, arg2):
        pass

class Invoker(object):
    def __init__(self, name, dispatchType, pDisp):
        self.name = name
        self.dispatchType = dispatchType
        self.pDisp = pDisp

    def __call__(self, *args, **kwargs):
        #get id of name (key), todo names of args
        #print "invok!"
        nameCount = 1
        names = (c_wchar_p * nameCount)()
        names[0] = self.name
        rgDispId = (DISPID * nameCount)()

        #TODO handle failure
        self.pDisp.GetIDsOfNames(byref(IID_NULL), names, 1, LOCALE_SYSTEM_DEFAULT, rgDispId)
        
        #prepare invoke, TODO kwargs
        params = DISPPARAMS()
        cArgs = len(args)
        params.cArgs = cArgs
        vargs = (VARIANT * cArgs)()
        for i in range(cArgs):
            vargs[i].value = args[i]
            
        params.rgvarg = vargs
        if self.dispatchType & DISPATCH_PROPERTYPUT:
            params.cNamedArgs = 1
            nArgs = (DISPID * 1)()
            nArgs[0] = DISPID_PROPERTYPUT
            params.rgdispidNamedArgs = nArgs
        
        v = VARIANT()
        e = EXCEPINFO()
        p = c_uint(0)

        self.pDisp.Invoke(rgDispId[0], byref(IID_NULL), LOCALE_SYSTEM_DEFAULT,
                          self.dispatchType, byref(params),
                          byref(v), byref(e), byref(p))

        #TODO handle exception
        if not self.dispatchType & DISPATCH_PROPERTYPUT:
            return v.value

class COMDispatchIn(object):
    """exposes a dispatch COM Object as a python object"""
    def __init__(self, pUnk):
        pDisp = POINTER(IDispatch)()
        pUnk.QueryInterface(byref(IDispatch._iid_), byref(pDisp))
        if not pDisp:
            raise "wrapped object does not support IDispatch"
        self.__dict__['pDisp'] = pDisp #avoids calling __setattr__

    def __setattr__(self, key, value):
        Invoker(key, DISPATCH_PROPERTYPUT, self.__dict__['pDisp'])(value)
        
    def __getattr__(self, key):
        return Invoker(key, DISPATCH_METHOD|DISPATCH_PROPERTYGET, self.__dict__['pDisp'])

class COMDispatchOut(COMObject):
    """exposes a python object to the COM world"""
    _com_interfaces_ = [IDispatch]
    _factory = Factory()

    def __init__(self, pyObj, *args, **kwargs):
        COMObject.__init__(self, *args, **kwargs)
        self._disp_map_ = {}
        self.pyObj = pyObj
        
    def GetIDsOfNames(self, this, riid, rgszNames, cNames, lcid, rgDispid):
        #print "GetIDsOfNames", this, riid, rgszNames, cNames, lcid, rgDispid
        if cNames != 1: raise "not impl"    
        methodName = rgszNames.contents.value
        if hasattr(self.pyObj, methodName):
            dispId = hash(methodName)
            self._disp_map_[dispId] = getattr(self.pyObj, methodName)
            rgDispid.contents.value = dispId
            return S_OK
        else:
            return E_NOINTERFACE
    
    def Invoke(self, this, dispid, refiid, lcid, wFlags,
               pDispParams, pVarResult, pExcepInfo, puArgErr):
        #print "Invoke", dispid, refiid, lcid, wFlags, pDispParams
        #print "wFlags", wFlags
        if not self._disp_map_.has_key(dispid): return DISP_E_MEMBERNOTFOUND

        try:
            #convert args
            args = [pDispParams.contents.rgvarg[i].value \
                    for i in range(pDispParams.contents.cArgs)]
            args.reverse()
            
            #call method
            res = self._disp_map_[dispid](*args)
            #make variant result
            if pVarResult:
                #setvariantvalue(pVarResult.contents, res)
                pVarResult.contents.value = res
                
        except:
            import traceback
            traceback.print_exc()
            #TODO fill dispatch exception structure
            return DISP_E_EXCEPTION
        
        return S_OK

    def GetTypeInfoCount(self, this, pctInfo):
        if pctInfo:
            pctInfo.contents = 0
            return S_OK
        else:
            return E_INVALIDARG

    def GetTypeInfo(self, this, index, lcid, ppTInfo):
        return DISP_E_BADINDEX

def wrap(something):
    """returns dispatch wrapped something based on type of something"""
    if hasattr(something, 'QueryInterface'): #assume its a com object exposed to python
        return COMDispatchIn(something)
    else:
        return COMDispatchOut(something) 
        

