from venster.windows import *
from venster.atl import *
from venster.ole import *
from venster import wtl
from venster.lib import dispatch

from ctypes import *

from comtypes import IUnknown, STDMETHOD, GUID, COMObject
from comtypes.ole import IOleInPlaceActiveObject, IOleInPlaceUIWindow
from comtypes.automation import IDispatch, VARIANT
from comtypes.connectionpoints import dispinterface_EventReceiver

class IDocHostUIHandler(IUnknown):
    _iid_ = GUID("{BD3F23C0-D43E-11CF-893B-00AA00BDCE1A}")

##CTYPES, maybe the following 2 ifaces should be in ctypes?
class IOleCommandTarget(IUnknown):
    _iid_ = GUID("{B722BCCB-4E68-101B-A2BC-00AA00404770}")

class IOleInPlaceFrame(IUnknown):
    _iid_ = GUID("{00000116-0000-0000-C000-000000000046}")

##CTYPES, change default behaviour for addreffing iface pointers on
##methods that are not implemented on python side so that __del__ does
IDocHostUIHandler._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "ShowContextMenu", [DWORD, DWORD, DWORD, DWORD]),
    STDMETHOD(HRESULT, "GetHostInfo", [DWORD]), #TODO wrap DOCHOSTUIINFO struct
    STDMETHOD(HRESULT, "ShowUI", [DWORD, DWORD, DWORD, DWORD, DWORD]),
    STDMETHOD(HRESULT, "HideUI", []),
    STDMETHOD(HRESULT, "UpdateUI", []),
    STDMETHOD(HRESULT, "EnableModeless", [BOOL]),
    STDMETHOD(HRESULT, "OnDocWindowActivate", [BOOL]),
    STDMETHOD(HRESULT, "OnFrameWindowActivate", [BOOL]),
    STDMETHOD(HRESULT, "ResizeBorder", [DWORD, DWORD, BOOL]),
    STDMETHOD(HRESULT, "TranslateAccelerator", [POINTER(MSG), POINTER(GUID), DWORD]),
    STDMETHOD(HRESULT, "GetOptionKeyPath", [DWORD, DWORD]),
    STDMETHOD(HRESULT, "GetDropTarget", [DWORD, DWORD]),
    STDMETHOD(HRESULT, "GetExternal", [POINTER(POINTER(IDispatch))]),
    STDMETHOD(HRESULT, "TranslateUrl", [DWORD, DWORD, DWORD]),
    STDMETHOD(HRESULT, "FilterDataObject", [WORD, DWORD]),
    ]

class ICustomDoc(IUnknown):
    _iid_ = GUID("{3050F3F0-98B5-11CF-BB82-00AA00BDCE0B}")

ICustomDoc._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "SetUIHandler", [POINTER(IDocHostUIHandler)])
    ]
    
from ie6_gen import DWebBrowserEvents2, IWebBrowser2

class Browser(AxWindow, dispinterface_EventReceiver):
    """Internet Explorer as ActiveX Control"""    
    _class_ws_style_ = AxWindow._class_ws_style_ | WS_HSCROLL | WS_VSCROLL

    _com_interfaces_ = [DWebBrowserEvents2]

    def __init__(self, url = "about:blank", *args, **kwargs):
        kwargs['ctrlId'] = url #if url is passed to axwindow, IE control is launched
        AxWindow.__init__(self, *args, **kwargs)
        dispinterface_EventReceiver.__init__(self)

        pUnk = self.GetControl() #IUnknown of IE
        pOle = POINTER(IOleInPlaceActiveObject)() #automation object
        pUnk.QueryInterface(byref(IOleInPlaceActiveObject._iid_), byref(pOle))        
        self.pOle = pOle

        self.pBrowser = POINTER(IWebBrowser2)() #the interface to IE
        pUnk.QueryInterface(byref(IWebBrowser2._iid_), byref(self.pBrowser))

        self.connectInfo = self.connect(pUnk) #receive callbacks from IE
            
        #makes accelerator keys work in IE:
        wtl.GetMessageLoop().AddFilter(self.PreTranslateMessage)

        
    
    def dispose(self):
        self.disconnect(self.connectInfo)
        wtl.GetMessageLoop().RemoveFilter(self.PreTranslateMessage)
        del self.pOle
        del self.pBrowser
        del self.connectInfo
        
    def Navigate(self, url):
         v = VARIANT()
         self.pBrowser.Navigate(url, byref(v), byref(v), byref(v), byref(v))

    #filter needed to make 'del' and other accel keys work
    #within IE control. @see http://www.microsoft.com/mind/0499/faq/faq0499.asp
    #insert into wtl ptl loop
    def PreTranslateMessage(self, msg):
        #here any keyboard message from the app passes:
        if msg.message >= WM_KEYFIRST and  msg.message <= WM_KEYLAST:
            #now we see if the control which sends these msgs is a child of
            #this axwindow (for instance input control embedded in html page)
            parent = msg.hWnd
            while parent:
                parent = GetParent(int(parent))
                if parent == self.handle:
                    #yes its a child of mine
                    if self.pOle.TranslateAccelerator(byref(msg)) == 0:
                        #translation has happened
                        return 1



