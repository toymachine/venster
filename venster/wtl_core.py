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

import sys
import weakref

quit = False

class HandleMap(dict):
    """a special weakreference map for mapping window handles to python instances
    when a python instance becomes garbage, the __dispose__ method of HandleMap
    is called, deleting the handle from the map and freeing OS resources by calling
    the method stored in the __dispose__ variable of the garbage python instance.
    This latter method should be bound to a windows-free-routine corresponding to the
    type of the handle"""
    
    def __setitem__(self, handle, value):
        # watch the lambda closure, freezing the binding of:
        # - fndisp to the __dispose__ variable of the value object
        # - handle to the provided windows-handle in the first actual parameter
        lmdisp = lambda wr, fndisp = value.__dispose__, dbgstr = str(value.__class__): \
            self.__dispose__(handle, wr, fndisp, dbgstr)
        dict.__setitem__(self, handle, weakref.ref(value, lmdisp))

    def __getitem__(self, handle):
        return dict.__getitem__(self, handle)() # weak refs are 'called' to return the referred object

    def get(self, k, d = None):
        if self.has_key(k):
            return self[k]
        else:
            return d
    
    def __dispose__(self, handle, wr, fndisp, dbgstr): # callback of weakref wr, called when wr() is garbage
        self.__delitem__(handle)
        if not quit:
            fndisp(handle)


hndlMap = HandleMap() #contains the mapping from python instances (of Window) to windows HANDLES
createHndlMap = {} #used while handling messages during CreateWindow(Ex)

def globalWndProc(hWnd, nMsg, wParam, lParam):
    """The purpose of globalWndProc is route messages coming in on the global queue
    to the appropriate python Window instance for handling.
    Also it establishes the mapping from python instances to window HANDLES by processing the WM_NCCREATE message
    """
    #print hWnd, nMsg, wParam, lParam
    #print hndlMap
    try:
        if nMsg == WM_NCCREATE:
            #a venster window is being creaated trough CreateWindowEx,
            #establish the mapping between the windows HANDLE and the Window instance
            #the window instance is to be found in the createHndlMap by looking up
            #the key that was given as a parameter to CreateWindowEx
            createStruct = CREATESTRUCT.from_address(int(lParam))
            window = createHndlMap.get(int(createStruct.lpCreateParams), None)
            if window:
                #it is a venster window being created, establish the mapping:
                WindowsObject.__init__(window, hWnd)

        handled = False
        result = None
        
        window = hndlMap.get(hWnd, None)
        if window:
            #this is a known venster window, let the window process its own msgs
            handled, result = window.WndProc(hWnd, nMsg, wParam, lParam)
            if not handled and window._issubclassed_:
                #its a subclassed window, try old window proc
                result = CallWindowProc(window._old_wnd_proc_, hWnd, nMsg, wParam, lParam)
                handled = True #always handled, either by old window proc, or old window proc called default handling

        if not handled:
            #still not handled, perform default processing
            return DefWindowProc(hWnd, nMsg, wParam, lParam) #windows default processing
        else:
            return result
    except:
        try:
            import traceback
            traceback.print_exc()
        except:
            pass #this happens when the python runtime is already exitting, but we are still registered
            #as a window proc and windows keeps calling the callback
        

cGlobalWndProc = WNDPROC(globalWndProc)

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
        

class WindowsObject(object):
    def __init__(self, handle, managed = True):
        """managed objects are stored in a global map so that they can
        be looked up by their handle, also this allows for calling the
        appropriate destructor function (__dispose__) whenever the object
        becomes garbage"""
        self.m_handle = handle
        if managed: hndlMap[handle] = self
        
    handle = property(lambda self: self.m_handle)

    def __str__(self):
        return '<%s handle: %d>' % (self.__class__.__name__, self.handle)

    def __equals__(self, other):
        return self.handle == other.handle

class Event(object):
    def __init__(self, hWnd, nMsg, wParam, lParam):
        self.hWnd = hWnd
        self.nMsg = nMsg
        self.lParam = lParam
        self.wParam = wParam
        self.handled = 0

    def structure(self, nmStructure):
        return nmStructure.from_address(int(self.lParam))
               
    def __str__(self):
        return "<event hWnd: %d, nMsg: %d, lParam: %d, wParam: %d>" % (self.hWnd, self.nMsg,
                                                                       self.lParam, self.wParam)

    
class MSG_MAP(list):
    def __init__(self, entries):
        list.__init__(self, entries)

        self._msg_map_ = {}
        
        for entry in self:
            self.append(entry)

    def append(self, entry):
        entry.__install__(self)
        
    def Handle(self, receiver, hWnd, nMsg, wParam, lParam, clazz):
        handler = self._msg_map_.get(nMsg, None)

        if handler:
            event = Event(hWnd, nMsg, wParam, lParam)
            event.handled = True #the presence of a handler means that by default we assume the event to be handled
            #if the handler wants to force further processing by parent class map
            #the handler will set event.handled to False
            result = handler(receiver, event)
            if event.handled:
                if result == None:
                    return (True, NULL)
                else:
                    return (True, int(result))

        return (False, NULL)

    def HandleBaseClasses(self, receiver, hWnd, nMsg, wParam, lParam, clazz):
        for baseClass in clazz.__bases__:
            if issubclass(baseClass, Window):
                handled, result = baseClass._msg_map_.Dispatch(receiver, hWnd, nMsg, wParam, lParam, baseClass)
                if handled:
                    return (True, result)
        return (False, NULL)

    def Dispatch(self, receiver, hWnd, nMsg, wParam, lParam, clazz = None):
        clazz = clazz or receiver.__class__
        
        handled, result = self.Handle(receiver, hWnd, nMsg, wParam, lParam, clazz)
        if handled:
            return (True, result)
        handled, result = self.HandleBaseClasses(receiver, hWnd, nMsg, wParam, lParam, clazz)
        if handled:
            return (True, result)
        #nobody handled msg
        return (False, NULL)

    def DispatchMSG(self, receiver, msg):
        return self.Dispatch(receiver, msg.hWnd, msg.message, msg.wParam, msg.lParam)

    def __str__(self):
        return str(self._msg_map_)

class WindowType(type):
    def __init__(cls, name, bases, dct):
        #make sure every window class has its own msg map
        if not dct.has_key('_msg_map_'):
            cls._msg_map_ = MSG_MAP([])
        super(WindowType, cls).__init__(name, bases, dct)
        #see if decorators were used to map events to handlers,
        #and install the handlers in the msgmap
        for item in dct.values():
            if hasattr(item, 'handler'):
                cls._msg_map_.append(item.handler)
                    
hInstance = GetModuleHandle(NULL)
wndClasses = []
RCDEFAULT = RECT(top = CW_USEDEFAULT, left = CW_USEDEFAULT, right = 0, bottom = 0)   


class Window(WindowsObject):
    __metaclass__ = WindowType
    
    _window_class_ = ''
    _window_title_ = ''
    _window_style_ = WS_OVERLAPPEDWINDOW | WS_VISIBLE
    _window_style_ex_ = 0
    _window_icon_ = LoadIcon(NULL, IDI_APPLICATION)
    _window_icon_sm_ = LoadIcon(NULL, IDI_APPLICATION)
    _window_background_ = 0
    _window_class_style_ = 0
    _window_style_clip_children_and_siblings_ = True
    _window_dbg_msg_ = False
    _window_width_ = CW_USEDEFAULT
    _window_height_ = CW_USEDEFAULT
    
    __dispose__ = DestroyWindow 
   
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
                 width = CW_USEDEFAULT,
                 height = CW_USEDEFAULT,
                 hWnd = None):

        if hWnd: #wrapping instead of creating
            self.m_handle = hWnd #note client is responsible for deleting
            return

        windowClassExists = False
        cls = WNDCLASSEX()
        if self._window_class_:
            if GetClassInfo(hInstance, self._window_class_, byref(cls)):
                windowClassExists = True
        
        #determine whether we are going to subclass an existing window class
        #or create a new windowclass
        self._issubclassed_ = self._window_class_ and windowClassExists
        
        if not self._issubclassed_:
            #if no _window_class_ is given, generate a new one
            className = self._window_class_ or "venster_wtl_%s" % str(id(self.__class__))
            cls = WNDCLASSEX()
            cls.cbSize = sizeof(cls)
            cls.lpszClassName = className
            cls.hInstance = hInstance
            cls.lpfnWndProc = cGlobalWndProc
            cls.style = self._window_class_style_
            cls.hbrBackground = self._window_background_
            cls.hIcon = handle(self._window_icon_)
            cls.hIconSm = handle(self._window_icon_sm_)
            cls.hCursor = LoadCursor(NULL, IDC_ARROW)
            #cls structure needs to stay on heap
            wndClasses.append(cls)
            atom = RegisterClassEx(byref(cls))
        else:
            #subclass existing window class.
            className = self._window_class_

        title = title or self._window_title_
        
        if style is None:
            style = self._window_style_

        if exStyle is None:
            exStyle = self._window_style_ex_

        if orStyle:
            style |= orStyle

        if orExStyle:
            exStyle |= orExStyle

        if self._window_style_clip_children_and_siblings_:
            style |= WS_CLIPCHILDREN
            style |= WS_CLIPSIBLINGS

        if nandStyle:
            style &= ~nandStyle

        left, right = rcPos.left, rcPos.right
        top, bottom = rcPos.top, rcPos.bottom

        if width == CW_USEDEFAULT:
            width = self._window_width_
        if left == CW_USEDEFAULT and width != CW_USEDEFAULT:
            right = CW_USEDEFAULT + width

        if height == CW_USEDEFAULT:
            height = self._window_height_
        if top == CW_USEDEFAULT and height != CW_USEDEFAULT:
            bottom = CW_USEDEFAULT + height
        
        #for normal windows created trough venster, the mapping between window handle
        #and window instance will be established by processing the WM_NCCREATE msg
        #and looking up the instance in the createhndlMap
        createHndlMap[id(self)] = self
        hWnd = CreateWindowEx(exStyle,
                              className,
                              title,
                              style,
                              left,
                              top,
                              right - left,
                              bottom - top,
                              handle(parent),
                              handle(menu),
                              hInstance,
                              id(self))       

        del createHndlMap[id(self)]

##         print """
##         CreateWindowEx [exStyle = %d, className = %s,
##         title = %s, style = %d, x = %d, y = %d,
##         nWidth = %d, nHeight = %d, hwndParent = %d,
##         hMenu = %d, hInstance = %d] -> hWnd = %d""" % (exStyle, className, title, style, rcPos.left,
##                                                        rcPos.top, nWidth, nHeight, handle(parent),
##                                                        handle(menu), hInstance, hWnd)
        if self._issubclassed_:
            #for subclassed windows, we establish the instance <-> handle mapping here
            WindowsObject.__init__(self, hWnd)
            self._old_wnd_proc_ = self.SubClass(cGlobalWndProc)
            
    def SubClass(self, newWndProc):
        return SetWindowLong(self.handle, GWL_WNDPROC, newWndProc)

            
    class Interceptor(object):
        def __init__(self, receiver, window, msg_map, nMsg = [WM_NOTIFY]):
            self.nMsg = dict([(x, 1) for x in nMsg])
            self.newProc = WNDPROC(self.WndProc)
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
        if self._window_dbg_msg_: print self, hWnd, nMsg, wParam, lParam
        return self._msg_map_.Dispatch(self, hWnd, nMsg, wParam, lParam)
    
    def IsDialogMessage(self, lpmsg):
        return IsDialogMessage(self.handle, lpmsg)
    
    def PreTranslateMessage(self, msg):
        return 0

    def TranslateAccelerator(self, msg):
        return 0

    def __repr__(self):
        return '<Window hWnd: %d>' % self.handle
    
        

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

#deprecated, will be removed before 1.0
class CHAIN_MSG_MAP (object):
    def __init__(self, msgMap): pass
    def __install__(self, msgMap): pass
    
#decorator versions of the above    
def msg_handler(msg):
    def decorator_func(func):
        func.handler = MSG_HANDLER(msg, func)
        return func
    return decorator_func

def cmd_handler(id, code = None):
    def decorator_func(func):
        if code:
            func.handler = CMD_HANDLER(id, code, func)
        else:
            func.handler = CMD_ID_HANDLER(id, func)
        return func
    return decorator_func

def ntf_handler(code):
    def decorator_func(func):
        func.handler = NTF_HANDLER(code, func)
        return func
    return decorator_func



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
        global quit
        quit = True
                    
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

    def Quit(self, nExitCode = 0):
        """quits the application by posting the WM_QUIT message with the given
        exitCode"""
        PostQuitMessage(nExitCode)
