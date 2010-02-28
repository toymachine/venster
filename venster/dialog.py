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

## Thanx to Brad Clements for this contribution!

from types import IntType, LongType

from ctypes import *

from venster.windows import *
from venster.wtl import *
from venster import comctl

memcpy = cdll.msvcrt.memcpy


class StringOrOrd:
    """Pack up a string or ordinal"""
    def __init__(self, value):
        if value is None or value == "":
            self.value = c_ushort(0)
        elif type(value) in (IntType, LongType):
            # treat as an atom
            if not value:
                self.value = c_ushort(0)        # 0 is not a valid atom
            else:
                ordinaltype = c_ushort * 2
                ordinal = ordinaltype(0xffff, value)
                self.value = ordinal
        else:
            value = str(value)

            mbLen = MultiByteToWideChar(CP_ACP, 0, value, -1, 0, 0)
            if mbLen < 1:
                raise RuntimeError("Could not determine multibyte string length for %s" % \
                                   repr(value))

            #this does not work for me:, why needed?
            #if (mbLen % 2):
            #    mbLen += 1          # round up to next word in size
                
            stringtype = c_ushort * mbLen
            string = stringtype()
            result = MultiByteToWideChar(CP_ACP, 0, value, -1, addressof(string), sizeof(string))
            if result < 1:
                raise RuntimeError("could not convert multibyte string %s" % repr(value))
            self.value = string


    def __len__(self):
        return sizeof(self.value)

class DialogTemplate(WindowsObject):
    __dispose__ = GlobalFree
    _class_ = None
    _class_ws_style_ = WS_CHILD
    _class_ws_ex_style_ = 0
    _class_font_size_ = 8
    _class_font_name_ = "MS Sans Serif" 

    def __init__(self,
                 wclass = None,    # the window class
                 title = "",
                 menu=None,
                 style = None,
                 exStyle = None,
                 fontSize=None,
                 fontName=None,
                 rcPos = RCDEFAULT,
                 orStyle = None,
                 orExStyle = None,
                 nandStyle = None,
                 nandExStyle = None,
                 items=[]):


        if wclass is not None:
            wclass = StringOrOrd(wclass)
        else:
            wclass = StringOrOrd(self._class_)

        title = StringOrOrd(title)
        menu = StringOrOrd(menu)

        if style is None:
            style = self._class_ws_style_

        if exStyle is None:
            exStyle = self._class_ws_ex_style_

        if orStyle:
            style |= orStyle

        if orExStyle:
            exStyle |= orExStyle


        if nandStyle:
            style &= ~nandStyle

        if rcPos.left == CW_USEDEFAULT:
            cx = 50
            x = 0
        else:
            cx = rcPos.right
            x = rcPos.left

        if rcPos.top == CW_USEDEFAULT:
            cy = 50
            y = 0
        else:
            cy = rcPos.bottom
            y = rcPos.top

        if style & DS_SETFONT:
            if fontSize is None:
                fontSize = self._class_font_size_

            if fontName is None:
                fontName = StringOrOrd(self._class_font_name_)
        else:
            fontSize = None
            fontName = None

        header = DLGTEMPLATE()
        byteCount = sizeof(header)

        byteCount += len(wclass) + len(title) + len(menu)
        if fontName or fontSize:
            byteCount += 2 + len(fontName)

        d, rem = divmod(byteCount, 4)   # align on dword
        byteCount += rem
        itemOffset = byteCount  # remember this for later

        for i in items:
            byteCount += len(i)

        valuetype = c_ubyte * byteCount
        value = valuetype()

        header = DLGTEMPLATE.from_address(addressof(value))
        # header is overlayed on value
        header.exStyle = exStyle
        header.style = style
        header.cDlgItems = len(items)
        header.x = x
        header.y = y
        header.cx = cx
        header.cy = cy

        offset = sizeof(header)

        # now, memcpy over the menu
        memcpy(addressof(value)+offset, addressof(menu.value), len(menu))    # len really returns sizeof menu.value
        offset += len(menu)

        # and the window class
        memcpy(addressof(value)+offset, addressof(wclass.value), len(wclass))    # len really returns sizeof wclass.value
        offset += len(wclass)

        # now copy the title
        memcpy(addressof(value)+offset, addressof(title.value), len(title))
        offset += len(title)

        if fontSize or fontName:
            fsPtr = c_ushort.from_address(addressof(value)+offset)
            fsPtr.value = fontSize
            offset += 2

            # now copy the fontname
            memcpy(addressof(value)+offset, addressof(fontName.value), len(fontName))
            offset += len(fontName)



        # and now the items
        assert offset <= itemOffset, "offset %d beyond items %d" % (offset, itemOffset)
        offset = itemOffset
        for item in items:
            memcpy(addressof(value)+offset, addressof(item.value), len(item))
            offset += len(item)
            assert (offset % 4) == 0, "Offset not dword aligned for item"

        self.m_handle = GlobalAlloc(0, sizeof(value))
        memcpy(self.m_handle, addressof(value), sizeof(value))
        self.value = value

    def __len__(self):
        return sizeof(self.value)


class DialogItemTemplate(object):
    _class_ = None
    _class_ws_style_ = WS_CHILD|WS_VISIBLE
    _class_ws_ex_style_ = 0

    def __init__(self,
                 wclass = None,    # the window class
                 id = 0,              # the control id
                 title = "",
                 style = None,
                 exStyle = None,
                 rcPos = RCDEFAULT,
                 orStyle = None,
                 orExStyle = None,
                 nandStyle = None,
                 nandExStyle = None):


        if not self._class_ and not wclass:
            raise ValueError("A window class must be specified")

        if wclass is not None:
            wclass = StringOrOrd(wclass)
        else:
            wclass = StringOrOrd(self._class_)

        title = StringOrOrd(title)

        if style is None:
            style = self._class_ws_style_

        if exStyle is None:
            exStyle = self._class_ws_ex_style_

        if orStyle:
            style |= orStyle

        if orExStyle:
            exStyle |= orExStyle


        if nandStyle:
            style &= ~nandStyle

        if rcPos.left == CW_USEDEFAULT:
            cx = 50
            x = 0
        else:
            cx = rcPos.right
            x = rcPos.left

        if rcPos.top == CW_USEDEFAULT:
            cy = 50
            y = 0
        else:
            cy = rcPos.bottom
            y = rcPos.top

        header = DLGITEMTEMPLATE()
        byteCount = sizeof(header)
        byteCount += 2  # two bytes for extraCount
        byteCount += len(wclass) + len(title)
        d, rem = divmod(byteCount, 4)
        byteCount += rem            # must be a dword multiple

        valuetype = c_ubyte * byteCount
        value = valuetype()

        header = DLGITEMTEMPLATE.from_address(addressof(value))
        # header is overlayed on value
        header.exStyle = exStyle
        header.style = style
        header.x = x
        header.y = y
        header.cx = cx
        header.cy = cy
        header.id = id

        # now, memcpy over the window class
        offset = sizeof(header)
        memcpy(addressof(value)+offset, addressof(wclass.value), len(wclass))
        # len really returns sizeof wclass.value
        offset += len(wclass)
        # now copy the title
        memcpy(addressof(value)+offset, addressof(title.value), len(title))
        offset += len(title)
        extraCount = c_ushort.from_address(addressof(value)+offset)
        extraCount.value = 0
        self.value = value

    def __len__(self):
        return sizeof(self.value)

class PushButton(DialogItemTemplate):
    _class_ = PUSHBUTTON
    _class_ws_style_ = WS_CHILD|WS_VISIBLE|WS_TABSTOP

class DefPushButton(DialogItemTemplate):
    _class_ = PUSHBUTTON
    _class_ws_style_ = WS_CHILD|WS_VISIBLE|WS_TABSTOP|BS_DEFPUSHBUTTON

class GroupBox(DialogItemTemplate):
    _class_ = PUSHBUTTON
    _class_ws_style_ = WS_CHILD|WS_VISIBLE|BS_GROUPBOX

class EditText(DialogItemTemplate):
    _class_ = EDITTEXT
    _class_ws_style_ = WS_CHILD|WS_VISIBLE|WS_BORDER|WS_TABSTOP

class StaticText(DialogItemTemplate):
    _class_ = LTEXT
    _class_ws_style_ = WS_CHILD|WS_VISIBLE|WS_GROUP

class Dialog(WindowBase):
    """supports _dialog_id_ and _dialog_module_ class properties or
    use _dialog_template_"""
    _dialog_template_ = None
    _dialog_module_ = None
    _dialog_id_ = None
    
    def __init__(self, template = None, id = None, module = None):
        """module and dlgid can be passed as parameters or be given as class properties"""
        self.module = None
        self.id = None
        self.template = None

        if template or self._dialog_template_:
            self.template = template or self._dialog_template_
        elif module or self._dialog_module_:
            self.module = module or self._dialog_module_
            self.id = id or self._dialog_id_
        
        if self.module and type(self.module) == type(''): #module is given as path name
            self.module = LoadLibrary(self.module)

        self.m_handle = 0 #filled in on init dialog

    def DoModal(self, parent = 0, center = 1):
        self.center = center
        if self.template:
            return DialogBoxIndirectParam(self.module,
                                          self.template.handle,
                                          handle(parent),
                                          DialogProc(self.DlgProc),
                                          0)
        else:
            return DialogBoxParam(self.module, self.id, handle(parent),
                                  DialogProc(self.DlgProc), 0)

    def DlgProc(self, hwnd, uMsg, wParam, lParam):
        handled, result = self._msg_map_.Dispatch(self, hwnd, uMsg, wParam, lParam)
        return result
    
    def GetDlgItem(self, nIDDlgItem, windowClass = None):
        """specify window class to get a 'Venster' wrapped control"""
        hWnd = GetDlgItem(self.handle, nIDDlgItem)
        if hWnd and windowClass:
            return windowClass(hWnd = hWnd)
        else:
            return hWnd            

    def EndDialog(self, exitCode):
        EndDialog(self.handle, exitCode)

    def OnOK(self, event):
        self.EndDialog(IDOK)

    def OnCancel(self, event):
        self.EndDialog(IDCANCEL)

    def OnInitDialog(self, event):
        self.m_handle = event.handle
        if self.center: self.CenterWindow()
        return 0

    handle = property(lambda self: self.m_handle)

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_INITDIALOG, OnInitDialog),
                         CMD_ID_HANDLER(IDOK, OnOK),
                         CMD_ID_HANDLER(IDCANCEL, OnCancel)])

