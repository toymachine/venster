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
from gdi import *
from ctypes import *

import weakref

class HandleMap(dict):
    """a special weakreference map for mapping window handles to python instances
    when a python instance becomes garbage, the __dispose__ method is called,
    freeing OS resources"""
    
    def __setitem__(self, handle, value):
        lmdisp = lambda wr, fndisp = value.__dispose__, dbgstr = str(value.__class__): \
            self.__dispose__(handle, wr, fndisp, dbgstr)
        dict.__setitem__(self, handle, weakref.ref(value, lmdisp))

    def __getitem__(self, handle):
        return dict.__getitem__(self, handle)()

    def get(self, k, d = None):
        value = dict.get(self, k, d)
        if value:
            return value()
        else:
            return d
    
    def __dispose__(self, handle, wr, fndisp, dbgstr):
        #print "dispose", handle, wr, fndisp, dbgstr
        self.__delitem__(handle)
        fndisp(handle)

hndlMap = HandleMap()

def globalWndProc(hWnd, nMsg, wParam, lParam):
    """The purpose of globalWndProc is to let each (python) window instance
    handle its own msgs, therefore is a mapping maintained from hWnd to window instance"""
    #print hWnd, nMsg, wParam, lParam
    #print hndlMap
    
    try:
        window = hndlMap.get(hWnd, None)
        if window:
            #let the window process its own msgs
            handled, result = window.WndProc(hWnd, nMsg, wParam, lParam)
            if handled: 
                return result
            #not handled yet
            if window._class_: 
                #its a subclassed window, try old window proc
                return CallWindowProc(window._old_wnd_proc_, hWnd, nMsg, wParam, lParam)
            #still not handles, fall trough to default processing
    except:
        try:
            import traceback
            traceback.print_exc()
        except:
            pass

    #note: def window proc should never raise exception, if it does it is probably fatal
    return DefWindowProc(hWnd, nMsg, wParam, lParam) #windows default processing
    
cGlobalWndProc = WndProc(globalWndProc)

def handle(obj):
    if not obj:
        return NULL
    elif hasattr(obj, 'handle'):
        return obj.handle
    else:
        return obj

def instanceFromHandle(handle):
    return hndlMap.get(handle, None)

def instanceOrHandle(handle):
    return hndlMap.get(handle, handle)

def windowFromHandle(handle):
    """returns None if handle = 0, the python Window instance if
    handle is known, or a new pseudo window if handle != 0 and not known"""
    if not handle: return None
    window = hndlMap.get(handle, None)
    if not window:
        window = Window(hWnd = handle)
    return window
        
class Event(object):
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self.hWnd = hWnd
        self.nMsg = nMsg
        self.lParam = lParam
        self.wParam = wParam
        self.handled = 0

    handle = property(lambda self: self.hWnd)
        
    def getSize(self):
        return LOWORD(self.lParam), HIWORD(self.lParam)

    size = property(getSize, None, None, "")

    def getPosition(self):
        x, y = GET_XY_LPARAM(GetMessagePos())
        return POINT(x, y)
    
    position = property(getPosition)

    def getClientPosition(self):
        x, y = GET_XY_LPARAM(self.lParam)
        return POINT(x, y)
              
    clientPosition = property(getClientPosition)

    def __str__(self):
        return "<event hWnd: %d, nMsg: %d, lParam: %d, wParam: %d>" % (self.hWnd, self.nMsg,
                                                                       self.lParam, self.wParam)

    
class MSG_MAP(list):
    def __init__(self, entries):
        list.__init__(self, entries)

        self._msg_map_ = {}
        self._chained_ = []
        
        for entry in self:
            self.append(entry)

    def append(self, entry):
        entry.__install__(self)
        
    def Dispatch(self, receiver, hWnd, nMsg, wParam, lParam):
        handler = self._msg_map_.get(nMsg, None)
        if handler:
            event = Event(hWnd, nMsg, wParam, lParam)
            event.handled = 1
            result = handler(receiver, event)
            if event.handled:
                if result == None:
                    return (1, 0)
                else:
                    return (1, result)

        #not handled, try chained
        for msgMap in self._chained_:
            result = msgMap.Dispatch(receiver, hWnd, nMsg, wParam, lParam)
            if result:
                handled, result = result
                if handled:
                    return (handled, result)

        #nobody handled msg
        return (0, 0)

    def DispatchMSG(self, receiver, msg):
        return self.Dispatch(receiver, msg.hWnd, msg.message,
                             msg.wParam, msg.lParam)

    def __str__(self):
        return str(self._msg_map_) + ' ' + str(self._chained_)

#this is the base class for all handlers defined in msg maps
class HANDLER(object):
   #the handler is given in the msg map as a unbound (static) method
   #on some class X, to enable a derived class to override a handler method
   #of a parent class Y, a lambda trick is needed to pick the correct handler
   #(that of the base class)
   def __init__(self, handler):
       #TODO how to determine if handler is a lambda or a named function without
       #looking at '__name__'?:
       if not handler:
           self.m_handler = None
       elif handler.__name__ == '<lambda>':
           self.m_handler = handler
       else:
           #trick to make handler 'virtual' again
           self.m_handler = lambda self, event: getattr(self, handler.__name__)(event)

   def __call__(self, receiver, event):
       return self.handler(receiver, event)

   handler = property(lambda self: self.m_handler)   
   
#Handler for normal window messages (e.g. WM_SIZE, WM_CLOSE, WM_PAINT etc)        
class MSG_HANDLER(HANDLER):
    def __init__(self, msg, handler):
        HANDLER.__init__(self, handler)
        self.msg = msg

    def __install__(self, msgMap):
        msgMap._msg_map_[self.msg] = self


#Allows chaining of msgs maps (used to call parent classes map at end of child class map)
class CHAIN_MSG_MAP(object):
    def __init__(self, msgMap):
        self.msgMap = msgMap

    def __install__(self, msgMap):
        msgMap._chained_.append(self.msgMap)

class NTF_MAP(dict):
    def __call__(self, receiver, event):
        nmhdr = NMHDR.from_address(int(event.lParam))
        handler = self.get(str(nmhdr.code), None)
        if handler:
            event.nmhdr = nmhdr
            return handler(receiver, event)
        else:
            event.handled = 0
            return 0

#handler for notification messages
#handles all notifications with the given code
class NTF_HANDLER(HANDLER):
    def __init__(self, code, handler):
        HANDLER.__init__(self, handler)
        self.code = code

    def __install__(self, msgMap):
        notifMap = msgMap._msg_map_.setdefault(WM_NOTIFY, NTF_MAP())
        notifMap[str(self.code)] = self


#support for WM_COMMAND msgs
#cmd is a map from id -> [(code, handler), ...]
#first handler in the list that matches the code is fired
#if code == -1, than handler is fired for any code
class CMD_MAP(dict):
    def __call__(self, receiver, event):
        code = HIWORD(event.wParam)
        id = LOWORD(event.wParam)
        for handlerCode, handler in self.get(id, []):
            if handlerCode == -1 or handlerCode == code:
                event.id = id
                event.code = code
                return handler(receiver, event)
        #not handled
        event.handled = 0
        return 0
    
#maps command message based on control id AND notification code
class CMD_HANDLER(HANDLER):
    def __init__(self, id, code, handler):
        HANDLER.__init__(self, handler)
        self.id, self.code = id, code
        
    def __install__(self, msgMap):
        cmdMap = msgMap._msg_map_.setdefault(WM_COMMAND, CMD_MAP())
        notifList = cmdMap.setdefault(self.id, [])
        notifList.append((self.code, self))

#maps command message based on control id    
class CMD_ID_HANDLER(HANDLER):
    def __init__(self, id, handler):
        HANDLER.__init__(self, handler)
        self.id = id
       
    def __install__(self, msgMap):
        cmdMap = msgMap._msg_map_.setdefault(WM_COMMAND, CMD_MAP())
        notifList = cmdMap.setdefault(self.id, [])
        notifList.append((-1, self))

class WindowsObject(object):
    def __init__(self, handle, managed = True):
        """managed objects are stored in a global map so that they can
        be looked up by their handle, also this allows for calling the
        appropriate destructor function (__dispose__) whenever the object
        becomes garbage"""
        self.m_handle = handle
        if managed: hndlMap[handle] = self
        #print hndlMap
        #print '__init__', self
        
    handle = property(lambda self: self.m_handle)

    def __str__(self):
        return '<%s handle: %d>' % (self.__class__.__name__, self.handle)

class MenuBase(object):
    def AppendMenu(self, flags, idNewItem, lpNewItem):
        if flags == MF_STRING or flags == MF_SEPARATOR:
            AppendMenu(self.handle, flags, idNewItem, lpNewItem)
        elif flags & MF_POPUP:
            AppendMenu(self.handle, flags, handle(idNewItem), lpNewItem)
    
    def EnableMenuItem(self, uIDEnableItem, uEnable):
        EnableMenuItem(self.handle, uIDEnableItem, uEnable)

    def GetSubMenu(self, id):
        return instanceFromHandle(GetSubMenu(self.handle, id))

    def GetItemCount(self):
        return GetMenuItemCount(self.handle)

    def __len__(self):
        return self.GetItemCount()

class Menu(MenuBase, WindowsObject):
    __dispose__ = DestroyMenu

    def __init__(self, hWnd = None, **kwargs):
        hWnd = hWnd or CreateMenu()
        WindowsObject.__init__(self, hWnd, **kwargs)
        
                   
class PopupMenu(MenuBase, WindowsObject):
    __dispose__ = DestroyMenu

    def __init__(self, *args, **kwargs):
        WindowsObject.__init__(self, CreatePopupMenu(), *args, **kwargs)

    def TrackPopupMenuEx(self, uFlags, x, y, wnd, lptpm):
        TrackPopupMenuEx(self.handle, uFlags, x, y, handle(wnd), lptpm)


RCDEFAULT = RECT(top = CW_USEDEFAULT, left = CW_USEDEFAULT,
                 bottom = 0, right = 0)    

hInstance = GetModuleHandle(NULL)

class WindowBase(object):
    def PostMessage(self, nMsg, wParam = 0, lParam = 0):
        return PostMessage(self.handle, nMsg, wParam, lParam)

    def SendMessage(self, nMsg, wParam = 0, lParam = 0):
        return SendMessage(self.handle, nMsg, wParam, lParam)

    def GetClientRect(self):
        rc = RECT()
        GetClientRect(self.handle, byref(rc))
        return rc

    clientRect = property(GetClientRect, None, None, "")

    def SetWindowPos(self, hWndInsertAfter, x, y, cx, cy, uFlags):
        SetWindowPos(self.handle, hWndInsertAfter, x, y, cx, cy, uFlags)
    
    def GetWindowRect(self):
        rc = RECT()
        GetWindowRect(self.handle, byref(rc))
        return rc

    windowRect = property(GetWindowRect, None, None, "")

    def ChildWindowFromPoint(self, point):
        return windowFromHandle(ChildWindowFromPoint(self.handle, point))
            
    def ScreenToClient(self, point):
        ScreenToClient(self.handle, byref(point))

    def ClientToScreen(self, point):
        ClientToScreen(self.handle, byref(point))
        
    def SetRedraw(self, bRedraw):
        self.SendMessage(WM_SETREDRAW, bRedraw, 0)

    def SetFont(self, hFont, bRedraw):
        self.SendMessage(WM_SETFONT, handle(hFont), bRedraw)

    def SetWindowText(self, txt):
        SetWindowText(self.handle, txt)

    def SetText(self, txt):
        self.SendMessage(WM_SETTEXT, 0, txt)
        
    def GetText(self):
        textLength = self.SendMessage(WM_GETTEXTLENGTH) + 1
        textBuff = ' ' * textLength
        self.SendMessage(WM_GETTEXT, textLength, textBuff)
        return textBuff[:-1]
        
    def MoveWindow(self, x, y, nWidth, nHeight, bRepaint):
        MoveWindow(self.handle, x, y, nWidth, nHeight, bRepaint)

    def GetParent(self):
        return instanceOrHandle(GetParent(self.handle))

    parent = property(GetParent)

    def GetMenu(self):
        """Return a non managed object wrapper for this windows menu,
        the menu is not destroyed when the wrapper goes out of scope (becomes
        garbage)"""
        return Menu(hWnd = GetMenu(self.handle), managed = False)
    
    def CenterWindow(self, parent = None):
        """centers this window in its parent window, or the given
        parent window. If no parent window is given or found, the
        window is centered on the desktop"""
        if not parent:
            parent = self.GetParent()
        if not parent:
            parent = Window(hWnd = GetDesktopWindow())
        
        x = (parent.windowRect.width / 2) - (self.windowRect.width / 2)
        y = (parent.windowRect.height / 2) - (self.windowRect.height / 2)
        self.SetWindowPos(0,
                          parent.windowRect.left + x,
                          parent.windowRect.top + y, 0, 0,
                          SWP_NOACTIVATE | SWP_NOSIZE | SWP_NOZORDER)

    def SetFocus(self):
        SetFocus(self.handle)

    def __equals__(self, other):
        return self.handle == other.handle
    
wndClasses = []

class Window(WindowBase, WindowsObject):
    _class_ = ''    
    _class_ws_style_ = WS_OVERLAPPEDWINDOW
    _class_ws_ex_style_ = 0
    _class_icon_ = LoadIcon(NULL, IDI_APPLICATION)
    _class_icon_sm_ = LoadIcon(NULL, IDI_APPLICATION)
    _class_background_ = GetStockObject(WHITE_BRUSH)
    _class_style_ = 0
    _class_clip_children_and_siblings = 1
    
    __dispose__ = DestroyWindow 
   
    _msg_map_ = MSG_MAP([])
    
    def __init__(self, title = "",
                 style = None,
                 exStyle = None,
                 parent = None,
                 menu = None,
                 rcPos = RCDEFAULT,
                 orStyle = None,
                 orExStyle = None,
                 nandStyle = None,
                 nandExStyle = None,
                 hWnd = None):

        if hWnd: #wrapping instead of creating
            self.m_handle = hWnd
            return
                    
        if not self._class_:
            wndClass = "python_wtl_%s" % str(self.__class__)
            cls = WNDCLASSEX()
            cls.cbSize = sizeof(cls)
            cls.lpszClassName = wndClass
            cls.hInstance = hInstance
            cls.lpfnWndProc = cGlobalWndProc
            cls.style = self._class_style_
            cls.hbrBackground = self._class_background_
            cls.hIcon = handle(self._class_icon_)
            cls.hIconSm = handle(self._class_icon_sm_)
            cls.hCursor = LoadCursor(NULL, IDC_ARROW)
            #cls structure needs to stay on heap
            wndClasses.append(cls)
            atom = RegisterClassEx(byref(cls))
        else:
            wndClass = self._class_

        if style is None:
            style = self._class_ws_style_

        if exStyle is None:
            exStyle = self._class_ws_ex_style_

        if orStyle:
            style |= orStyle

        if orExStyle:
            exStyle |= orExStyle

        if self._class_clip_children_and_siblings:
            style |= WS_CLIPCHILDREN
            style |= WS_CLIPSIBLINGS

        if nandStyle:
            style &= ~nandStyle
            
        if rcPos.left == CW_USEDEFAULT:
            nWidth = CW_USEDEFAULT
        else:
            nWidth = rcPos.right - rcPos.left
            
        if rcPos.top == CW_USEDEFAULT:
            nHeight = CW_USEDEFAULT
        else:
            nHeight = rcPos.bottom - rcPos.top

        
        hWnd = CreateWindowEx(exStyle,
                              wndClass,
                              title,
                              style,
                              rcPos.left,
                              rcPos.top,
                              nWidth,
                              nHeight,
                              handle(parent),
                              handle(menu),
                              hInstance,
                              0)
        
##         print """
## CreateWindowEx [exStyle = %d, wndClass = %s,
## title = %s, style = %d, x = %d, y = %d,
## nWidth = %d, nHeight = %d, hwndParent = %d,
## hMenu = %d, hInstance = %d] -> hWnd = %d""" % (exStyle, wndClass, title, style, rcPos.left,
##                                                rcPos.top, nWidth, nHeight, handle(parent),
##                                                handle(menu), hInstance, hWnd)

        WindowsObject.__init__(self, hWnd)
        if self._class_:
            self._old_wnd_proc_ = self.SubClass(cGlobalWndProc)


    def SubClass(self, newWndProc):
        return SetWindowLong(self.handle, GWL_WNDPROC, newWndProc)

    def ShowWindow(self, cmdShow = SW_SHOW):
        ShowWindow(self.handle, cmdShow)

    def GetClassLong(self, index):
        return GetClassLong(self.handle, index)

    def SetClassLong(self, index, dwNewLong):
        SetClassLong(self.handle, index, dwNewLong)
        
    def UpdateWindow(self):
        UpdateWindow(self.handle)

    def SetCapture(self):
        SetCapture(self.handle)
        
    def Invalidate(self, bErase = TRUE):
        InvalidateRect(self.handle, NULL, bErase)

    def InvalidateRect(self, rc, bErase = TRUE):
        InvalidateRect(self.handle, byref(rc), bErase)

    def GetDCEx(self, hrgnClip, flags):
        return GetDCEx(self.handle, hrgnClip, flags)

    def GetDC(self):
        return GetDC(self.handle)
    
    def ReleaseDC(self, hdc):
        ReleaseDC(self.handle, hdc)
        
    def BeginPaint(self, paintStruct):
        return BeginPaint(self.handle, byref(paintStruct))

    def EndPaint(self, paintStruct):
        return EndPaint(self.handle, byref(paintStruct))
        
    def DestroyWindow(self):
        DestroyWindow(self.handle)

    def CloseWindow(self):
        CloseWindow(self.handle)
        
    def EnumChildWindows(self):
        """returns a list of this windows child windows"""
        childWindows = []
        def enumChildProc(hWnd, lParam):
            childWindows.append(Window(hWnd = hWnd))
        EnumChildWindows(self.handle, EnumChildProc(enumChildProc), 0)
        return childWindows
            
    class Interceptor(object):
        def __init__(self, receiver, window, msg_map, nMsg = [WM_NOTIFY]):
            self.nMsg = dict([(x, 1) for x in nMsg])
            self.newProc = WndProc(self.WndProc)
            self.oldProc = window.SubClass(self.newProc)
            self._msg_map_ = msg_map
            self.receiver = receiver
            

        def dispose(self):
            self.WndProc = lambda self, hWnd, nMsg, wParam, lParam: 0
            del self.receiver
            del self._msg_map_
            del self.newProc
            
            
        def WndProc(self, hWnd, nMsg, wParam, lParam):
            if nMsg in self.nMsg and hasattr(self, 'receiver'):
                handled, res = self._msg_map_.Dispatch(self.receiver, hWnd, nMsg, wParam, lParam)
            else:
                handled = 0
            if not handled:
                return CallWindowProc(self.oldProc, hWnd, nMsg, wParam, lParam)
            else:
                return res
            
    def Intercept(self, receiver, msgMap, nMsg = [WM_NOTIFY]):
        return Window.Interceptor(self, receiver, msgMap, nMsg = nMsg)

    def InterceptParent(self, nMsg = [WM_NOTIFY]):
        """intercepts msg proc in order to reroute msgs to self"""
        self._interceptParent = self.Intercept(self.GetParent(), self._msg_map_, nMsg = nMsg)

    def dispose(self):
        if hasattr(self, '_interceptParent'):
            self._interceptParent.dispose()
            del self._interceptParent
            
    def WndProc(self, hWnd, nMsg, wParam, lParam):
        return self._msg_map_.Dispatch(self, hWnd, nMsg, wParam, lParam)
    
    def IsDialogMessage(self, lpmsg):
        return IsDialogMessage(self.handle, lpmsg)
    
    def PreTranslateMessage(self, msg):
        return 0

    def TranslateAccelerator(self, msg):
        return 0

    def __repr__(self):
        return '<Window hWnd: %d>' % self.handle
    
        
class Bitmap(WindowsObject):
    __dispose__ = DeleteObject

    def __init__(self, path):
        WindowsObject.__init__(self, LoadImage(NULL, path, IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE))
        bm = BITMAP()
        GetObject(self.handle, sizeof(bm), byref(bm))
        self.m_width, self.m_height = bm.bmWidth, bm.bmHeight

    def getWidth(self):
        return self.m_width

    width = property(getWidth, None, None, "")
    
    def getHeight(self):
        return self.m_height

    height = property(getHeight, None, None, "")
        
class Icon(WindowsObject):
    __dispose__ = DestroyIcon
    
    def __init__(self, path):
        WindowsObject.__init__(self, LoadImage(NULL, path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE))

#TODO refactor into Brush class with static factory class methods
class SolidBrush(WindowsObject):
    __dispose__ = DeleteObject

    def __init__(self, colorRef):
        WindowsObject.__init__(self, CreateSolidBrush(colorRef))
        
class Pen(WindowsObject):
    __dispose__ = DeleteObject

    def Create(cls, fnPenStyle = PS_SOLID,  nWidth = 1, crColor = 0x00000000):
        return Pen(CreatePen(fnPenStyle, nWidth, crColor))

    Create = classmethod(Create)
    
    def CreateEx(cls, dwPenStyle = PS_COSMETIC | PS_SOLID, dwWidth = 1, lbStyle = BS_SOLID,
                 lbColor = 0x00000000, lbHatch = 0,
                 dwStyleCount = 0, lpStyle = 0):
        lb = LOGBRUSH(lbStyle, lbColor, lbHatch)
        return Pen(ExtCreatePen(dwPenStyle, dwWidth, byref(lb), dwStyleCount, lpStyle))

    CreateEx  = classmethod(CreateEx)
    

class Font(WindowsObject):
    __dispose__ = DeleteObject

    def __init__(self, **kwargs):
        #TODO move these kwargs to init, use default values
        hfont = CreateFont(kwargs.get('height', 0),
                           kwargs.get('width', 0),
                           kwargs.get('escapement', 0),
                           kwargs.get('orientation', 0),
                           kwargs.get('weight', 0),
                           kwargs.get('italic', 0),
                           kwargs.get('underline', 0),
                           kwargs.get('strikeout', 0),
                           kwargs.get('charset', ANSI_CHARSET),
                           kwargs.get('outputPrecision', OUT_DEFAULT_PRECIS),
                           kwargs.get('clipPrecision', CLIP_DEFAULT_PRECIS),
                           kwargs.get('quality', DEFAULT_QUALITY),
                           kwargs.get('pitchAndFamily', DEFAULT_PITCH|FF_DONTCARE),
                           kwargs.get('face', ""))
        WindowsObject.__init__(self, hfont)

        
#TODO allow the addition of more specific filters
#TODO make filters weak so that remove filter is not needed
class MessageLoop:
    def __init__(self):
        self.m_filters = {}

    def AddFilter(self, filterFunc):
        self.m_filters[filterFunc] = 1

    def RemoveFilter(self, filterFunc):
        del self.m_filters[filterFunc]
        
    def Run(self):
        msg = MSG()
        lpmsg = byref(msg)
        while GetMessage(lpmsg, 0, 0, 0):
            if not self.PreTranslateMessage(msg):
                TranslateMessage(lpmsg)
                DispatchMessage(lpmsg)
                    
    def PreTranslateMessage(self, msg):
        for filter in self.m_filters.keys():
            if filter(msg):
                return 1
        return 0
    
theMessageLoop = MessageLoop()

def GetMessageLoop():
    return theMessageLoop

def Run():
    theMessageLoop.Run()
    #hWndMap should be empty at this point, container widgets
    #should auto-dispose of their children! (somehow)
    #print hndlMap
    #import gc
    #print gc.garbage


class Application(object):
    def Run(self):
        return Run()
