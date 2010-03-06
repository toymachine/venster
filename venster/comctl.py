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
from wtl import *

ATL_IDW_BAND_FIRST = 0xEB00
HTREEITEM = HANDLE
HIMAGELIST = HANDLE

UINT_MAX = (1l << 32)

LVCF_FMT     =1
LVCF_WIDTH   =2
LVCF_TEXT    =4
LVCF_SUBITEM =8
LVCF_IMAGE= 16
LVCF_ORDER= 32

TVIF_TEXT    = 1
TVIF_IMAGE   =2
TVIF_PARAM   =4
TVIF_STATE   =8
TVIF_HANDLE = 16
TVIF_SELECTEDIMAGE  = 32
TVIF_CHILDREN      =  64
TVIF_INTEGRAL      =  0x0080
TVIF_DI_SETITEM    =  0x1000

LVIF_TEXT   = 1
LVIF_IMAGE  = 2
LVIF_PARAM  = 4
LVIF_STATE  = 8
LVIF_DI_SETITEM =  0x1000

class MaskedStructureType(Structure.__class__):
    def __new__(cls, name, bases, dct):
        fields = []
        for field in dct['_fields_']:
            fields.append((field[0], field[1]))
            if len(field) == 4: #masked field
                dct[field[3]] = property(None,
                                         lambda self, val, field = field:
                                         self.setProperty(field[0], field[2], val))
        dct['_fields_'] = fields
        return Structure.__class__.__new__(cls, name, bases, dct)
    
class MaskedStructure(Structure):
    __metaclass__ = MaskedStructureType
    _fields_ = []

    def setProperty(self, name, mask, value):
        setattr(self, self._mask_, getattr(self, self._mask_) | mask)
        setattr(self, name, value)

    def clear(self):
        setattr(self, self._mask_, 0)
        
class NMCBEENDEDIT(Structure):
    _fields_ = [("hdr", NMHDR),
                ("fChanged", BOOL),
                ("iNewSelection", INT),
                ("szText", POINTER(TCHAR)),
                ("iWhy", INT)]

class LVCOLUMN(MaskedStructure):
    _mask_ = 'mask'
    _fields_ = [("mask", UINT),
                ("fmt", INT, LVCF_FMT, "format"),
                ("cx", INT, LVCF_WIDTH, 'width'),
                ("pszText", LPTSTR, LVCF_TEXT, 'text'),
                ("cchTextMax", INT),
                ("iSubItem", INT),
                ("iImage", INT),
                ("iOrder", INT)]

class LVITEM(Structure):
    _fields_ = [("mask", UINT),
                ("iItem", INT),
                ("iSubItem", INT),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM),
                ("iIndent", INT)]


class TVITEMEX(MaskedStructure):
    _mask_ = 'mask'
    _fields_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR, TVIF_TEXT, 'text'),
                ("cchTextMax", INT),
                ("iImage", INT, TVIF_IMAGE, 'image'),
                ("iSelectedImage", INT, TVIF_SELECTEDIMAGE, 'selectedImage'),
                ("cChildren", INT, TVIF_CHILDREN, 'children'),
                ("lParam", LPARAM, TVIF_PARAM, 'param'),
                ("iIntegral", INT)]

class TVITEM(Structure):
    _fields_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("iSelectedImage", INT),
                ("cChildren", INT),
                ("lParam", LPARAM)]

class TBBUTTON(Structure):
    _fields_ = [("iBitmap", INT),
                ("idCommand", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                ("bReserved", BYTE * 2),
                ("dwData", DWORD_PTR),
                ("iString", INT_PTR)]

class TBBUTTONINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("dwMask", DWORD),
                ("idCommand", INT),
                ("iImage", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                ("cx", WORD),
                ("lParam", DWORD_PTR),
                ("pszText", LPTSTR),
                ("cchText", INT)]

class TVINSERTSTRUCT(Structure):
    _fields_ = [("hParent", HTREEITEM),
                ("hInsertAfter", HTREEITEM),
                ("itemex", TVITEMEX)]

class TCITEM(Structure):
    _fields_ = [("mask", UINT),
                ("dwState", DWORD),
                ("dwStateMask", DWORD),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM)]

class NMTREEVIEW(Structure):
    _fields_ = [("hdr", NMHDR),
                ("action", UINT),
                ("itemOld", TVITEM),
                ("itemNew", TVITEM),
                ("ptDrag", POINT)]

class NMLISTVIEW(Structure):
    _fields_ = [("hrd", NMHDR),
                ("iItem", INT),
                ("iSubItem", INT),
                ("uNewState", UINT),
                ("uOldState", UINT),
                ("uChanged", UINT),
                ("ptAction", POINT),
                ("lParam", LPARAM)]
    
class INITCOMMONCONTROLSEX(Structure):
    _fields_ = [("dwSize", DWORD),
                ("dwICC", DWORD)]

class REBARINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("himl", HIMAGELIST)]

class REBARBANDINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("fStyle", UINT),
                ("clrFore", COLORREF),
                ("clrBack", COLORREF),
                ("lpText", LPTSTR),
                ("cch", UINT),
                ("iImage", INT),
                ("hwndChild", HWND),
                ("cxMinChild", UINT),
                ("cyMinChild", UINT),
                ("cx", UINT),
                ("hbmBack", HBITMAP),
                ("wID", UINT),
                ("cyChild", UINT),
                ("cyMaxChild", UINT),
                ("cyIntegral", UINT),
                ("cxIdeal", UINT),
                ("lParam", LPARAM),
                ("cxHeader", UINT)]

class NMTOOLBAR(Structure):
    _fields_ = [("hdr", NMHDR),
                ("iItem", INT),
                ("tbButton", TBBUTTON),
                ("cchText", INT),
                ("pszText", LPTSTR),
                ("rcButton", RECT)]

class NMTBHOTITEM(Structure):
    _fields_ = [("hdr", NMHDR),
                ("idOld", INT),
                ("idNew", INT),
                ("dwFlags", DWORD)]

class PBRANGE(Structure):
    _fields_ = [("iLow", INT),
                ("iHigh", INT)]
    
class NMITEMACTIVATE(Structure):
    _fields_ = [("hdr", NMHDR),
                ("iItem", c_int),
                ("iSubItem", c_int),
                ("uNewState", UINT),
                ("uOldState", UINT),
                ("uChanged", UINT),
                ("ptAction", POINT),
                ("lParam", LPARAM),
                ("uKeyFlags", UINT)]

NM_FIRST    =   UINT_MAX

SBS_BOTTOMALIGN = 4
SBS_HORZ = 0
SBS_LEFTALIGN = 2
SBS_RIGHTALIGN = 4
SBS_SIZEBOX = 8
SBS_SIZEBOXBOTTOMRIGHTALIGN = 4
SBS_SIZEBOXTOPLEFTALIGN = 2
SBS_SIZEGRIP = 16
SBS_TOPALIGN = 2
SBS_VERT = 1

CCS_NODIVIDER =	64
CCS_NOPARENTALIGN = 8
CCS_NORESIZE = 4
CCS_TOP = 1


CBS_DROPDOWN = 2

RBBS_BREAK = 1
RBBS_FIXEDSIZE = 2
RBBS_CHILDEDGE = 4
RBBS_HIDDEN = 8
RBBS_NOVERT = 16
RBBS_FIXEDBMP = 32
RBBS_VARIABLEHEIGHT = 64
RBBS_GRIPPERALWAYS = 128
RBBS_NOGRIPPER = 256

RBS_TOOLTIPS = 256
RBS_VARHEIGHT = 512
RBS_BANDBORDERS = 1024
RBS_FIXEDORDER = 2048

RBS_REGISTERDROP = 4096
RBS_AUTOSIZE = 8192
RBS_VERTICALGRIPPER = 16384
RBS_DBLCLKTOGGLE = 32768

RBN_FIRST	= ((UINT_MAX) - 831)
RBN_HEIGHTCHANGE = RBN_FIRST

TBSTYLE_FLAT = 2048
TBSTYLE_LIST = 4096
TBSTYLE_DROPDOWN = 8
TBSTYLE_TRANSPARENT = 0x8000
TBSTYLE_REGISTERDROP = 0x4000
TBSTYLE_BUTTON = 0x0000
TBSTYLE_AUTOSIZE = 0x0010
    
TB_BUTTONSTRUCTSIZE = WM_USER+30
TB_ADDBUTTONS       = WM_USER+20
TB_INSERTBUTTONA    = WM_USER + 21
TB_INSERTBUTTON     = WM_USER + 21
TB_BUTTONCOUNT      = WM_USER + 24
TB_GETITEMRECT      = WM_USER + 29
TB_SETBUTTONINFOW  =  WM_USER + 64
TB_SETBUTTONINFOA  =  WM_USER + 66
TB_SETBUTTONINFO   =  TB_SETBUTTONINFOA
TB_SETIMAGELIST    =  WM_USER + 48
TB_SETDRAWTEXTFLAGS =  WM_USER + 70
TB_PRESSBUTTON       = WM_USER + 3
TB_GETRECT        =      (WM_USER + 51)
TB_SETHOTITEM   =        (WM_USER + 72)
TB_HITTEST     =         (WM_USER + 69)
TB_GETHOTITEM  =         (WM_USER + 7)
TB_SETBUTTONSIZE     =  (WM_USER + 31)
TB_AUTOSIZE          =  (WM_USER + 33)

TVIF_TEXT    = 1
TVIF_IMAGE   =2
TVIF_PARAM   =4
TVIF_STATE   =8
TVIF_HANDLE = 16
TVIF_SELECTEDIMAGE  = 32
TVIF_CHILDREN      =  64
TVIF_INTEGRAL      =  0x0080
TVIF_DI_SETITEM    =  0x1000
 
TVI_ROOT     = 0xFFFF0000l
TVI_FIRST    = 0xFFFF0001l
TVI_LAST     = 0xFFFF0002l
TVI_SORT     = 0xFFFF0003l

TVGN_CHILD   =  4
TVGN_NEXT    =  1
TVGN_ROOT    =  0
TVGN_CARET   =           0x0009

TVIS_FOCUSED = 1
TVIS_SELECTED =       2
TVIS_CUT    = 4
TVIS_DROPHILITED   =  8
TVIS_BOLD  =  16
TVIS_EXPANDED      =  32
TVIS_EXPANDEDONCE  =  64
TVIS_OVERLAYMASK   =  0xF00
TVIS_STATEIMAGEMASK = 0xF000
TVIS_USERMASK      =  0xF000

TV_FIRST = 0x1100
TVM_INSERTITEMA =     TV_FIRST
TVM_INSERTITEMW =    (TV_FIRST+50)
TVM_INSERTITEM = TVM_INSERTITEMA
TVM_SETIMAGELIST =    (TV_FIRST+9)
TVM_DELETEITEM   =   (TV_FIRST+1)
TVM_GETNEXTITEM   =   (TV_FIRST+10)
TVM_EXPAND =   (TV_FIRST+2)
TVM_GETITEMSTATE=        (TV_FIRST + 39)
TVM_ENSUREVISIBLE=       (TV_FIRST + 20)
TVM_SELECTITEM=          (TV_FIRST + 11)
TVM_SETITEMA=            (TV_FIRST + 13)
TVM_SETITEMW =           (TV_FIRST + 63)
TVM_SETITEM= TVM_SETITEMA
TVM_GETITEMA=            (TV_FIRST + 12)
TVM_GETITEMW =           (TV_FIRST + 62)
TVM_GETITEM = TVM_GETITEMA


TVS_HASBUTTONS =       1
TVS_HASLINES = 2
TVS_LINESATROOT =      4
TVS_EDITLABELS  =      8
TVS_DISABLEDRAGDROP =  16
TVS_SHOWSELALWAYS =   32
TVS_CHECKBOXES =  256
TVS_TOOLTIPS = 128
TVS_RTLREADING = 64
TVS_TRACKSELECT = 512
TVS_FULLROWSELECT = 4096
TVS_INFOTIP = 2048
TVS_NONEVENHEIGHT = 16384
TVS_NOSCROLL  = 8192
TVS_SINGLEEXPAND  =1024
TVS_NOHSCROLL   =     0x8000

CBEN_FIRST  =  (UINT_MAX) - 800
CBEN_ENDEDITA = CBEN_FIRST - 5
CBEN_ENDEDITW = CBEN_FIRST - 6
CBEN_ENDEDIT = CBEN_ENDEDITA

# trackbar styles
TBS_AUTOTICKS =           0x0001
TBS_VERT =                0x0002
TBS_HORZ =                0x0000
TBS_TOP =                 0x0004
TBS_BOTTOM =              0x0000
TBS_LEFT =                0x0004
TBS_RIGHT =               0x0000
TBS_BOTH =                0x0008
TBS_NOTICKS =             0x0010
TBS_ENABLESELRANGE =      0x0020
TBS_FIXEDLENGTH =         0x0040
TBS_NOTHUMB =             0x0080
TBS_TOOLTIPS =            0x0100

# trackbar messages
TBM_GETPOS =              (WM_USER)
TBM_GETRANGEMIN =         (WM_USER+1)
TBM_GETRANGEMAX =         (WM_USER+2)
TBM_GETTIC =              (WM_USER+3)
TBM_SETTIC =              (WM_USER+4)
TBM_SETPOS =              (WM_USER+5)
TBM_SETRANGE =            (WM_USER+6)
TBM_SETRANGEMIN =         (WM_USER+7)
TBM_SETRANGEMAX =         (WM_USER+8)
TBM_CLEARTICS =           (WM_USER+9)
TBM_SETSEL =              (WM_USER+10)
TBM_SETSELSTART =         (WM_USER+11)
TBM_SETSELEND =           (WM_USER+12)
TBM_GETPTICS =            (WM_USER+14)
TBM_GETTICPOS =           (WM_USER+15)
TBM_GETNUMTICS =          (WM_USER+16)
TBM_GETSELSTART =         (WM_USER+17)
TBM_GETSELEND =           (WM_USER+18)
TBM_CLEARSEL =            (WM_USER+19)
TBM_SETTICFREQ =          (WM_USER+20)
TBM_SETPAGESIZE =         (WM_USER+21)
TBM_GETPAGESIZE =         (WM_USER+22)
TBM_SETLINESIZE =         (WM_USER+23)
TBM_GETLINESIZE =         (WM_USER+24)
TBM_GETTHUMBRECT =        (WM_USER+25)
TBM_GETCHANNELRECT =      (WM_USER+26)
TBM_SETTHUMBLENGTH =      (WM_USER+27)
TBM_GETTHUMBLENGTH =      (WM_USER+28)
TBM_SETTOOLTIPS =         (WM_USER+29)
TBM_GETTOOLTIPS =         (WM_USER+30)
TBM_SETTIPSIDE =          (WM_USER+31)
TBM_SETBUDDY =            (WM_USER+32) 
TBM_GETBUDDY =            (WM_USER+33) 

# trackbar top-side flags
TBTS_TOP =                0
TBTS_LEFT =               1
TBTS_BOTTOM =             2
TBTS_RIGHT =              3


TB_LINEUP =               0
TB_LINEDOWN =             1
TB_PAGEUP =               2
TB_PAGEDOWN =             3
TB_THUMBPOSITION =        4
TB_THUMBTRACK =           5
TB_TOP =                  6
TB_BOTTOM =               7
TB_ENDTRACK =             8

# trackbar custom draw item specs
TBCD_TICS =    0x0001
TBCD_THUMB =   0x0002
TBCD_CHANNEL = 0x0003



STATUSCLASSNAME = "msctls_statusbar32"

REBARCLASSNAMEW = u"ReBarWindow32"
REBARCLASSNAMEA = "ReBarWindow32"
REBARCLASSNAME = REBARCLASSNAMEA

PROGRESS_CLASSW = u"msctls_progress32"
PROGRESS_CLASSA = "msctls_progress32"
PROGRESS_CLASS = PROGRESS_CLASSA

TRACKBAR_CLASSW = u"msctls_trackbar32"
TRACKBAR_CLASSA = "msctls_trackbar32"
TRACKBAR_CLASS = TRACKBAR_CLASSA


EDIT = "Edit"
BUTTON = "BUTTON"

WC_COMBOBOXEXW = u"ComboBoxEx32"
WC_COMBOBOXEXA = "ComboBoxEx32"
WC_COMBOBOXEX = WC_COMBOBOXEXA

WC_TREEVIEWA = "SysTreeView32"
WC_TREEVIEWW = u"SysTreeView32"
WC_TREEVIEW = WC_TREEVIEWA

WC_LISTVIEWA = "SysListView32"
WC_LISTVIEWW = u"SysListView32"
WC_LISTVIEW = WC_LISTVIEWA

TOOLBARCLASSNAMEW = u"ToolbarWindow32"
TOOLBARCLASSNAMEA = "ToolbarWindow32"
TOOLBARCLASSNAME = TOOLBARCLASSNAMEA

WC_TABCONTROLA =    "SysTabControl32"
WC_TABCONTROLW =      u"SysTabControl32"
WC_TABCONTROL = WC_TABCONTROLA

LVS_ICON    = 0
LVS_REPORT   =1
LVS_SMALLICON =       2
LVS_LIST    = 3
LVS_TYPEMASK= 3
LVS_SINGLESEL=        4
LVS_SHOWSELALWAYS=    8
LVS_SORTASCENDING =   16
LVS_SORTDESCENDING =  32
LVS_SHAREIMAGELISTS = 64
LVS_NOLABELWRAP     = 128
LVS_AUTOARRANGE     = 256
LVS_EDITLABELS      = 512
LVS_NOSCROLL= 0x2000
LVS_TYPESTYLEMASK  =  0xfc00
LVS_ALIGNTOP= 0
LVS_ALIGNLEFT =       0x800
LVS_ALIGNMASK  =      0xc00
LVS_OWNERDRAWFIXED=   0x400
LVS_NOCOLUMNHEADER =  0x4000
LVS_NOSORTHEADER   =  0x8000
LVS_OWNERDATA =4096
LVS_EX_CHECKBOXES= 4
LVS_EX_FULLROWSELECT= 32
LVS_EX_GRIDLINES =1
LVS_EX_HEADERDRAGDROP= 16
LVS_EX_ONECLICKACTIVATE= 64
LVS_EX_SUBITEMIMAGES= 2
LVS_EX_TRACKSELECT= 8
LVS_EX_TWOCLICKACTIVATE= 128
LVS_EX_FLATSB       = 0x00000100
LVS_EX_REGIONAL     = 0x00000200
LVS_EX_INFOTIP      = 0x00000400
LVS_EX_UNDERLINEHOT = 0x00000800
LVS_EX_UNDERLINECOLD= 0x00001000
LVS_EX_MULTIWORKAREAS =       0x00002000
LVS_EX_LABELTIP     = 0x00004000
LVS_EX_BORDERSELECT = 0x00008000

LVIS_FOCUSED         =   0x0001
LVIS_SELECTED        =   0x0002
LVIS_CUT             =   0x0004
LVIS_DROPHILITED     =   0x0008
LVIS_ACTIVATING      =   0x0020

LVIS_OVERLAYMASK      =  0x0F00
LVIS_STATEIMAGEMASK   =  0xF000

LVM_FIRST = 0x1000
LVM_INSERTCOLUMNA = (LVM_FIRST+27)
LVM_INSERTCOLUMN = LVM_INSERTCOLUMNA
LVM_INSERTITEMA = (LVM_FIRST+7)
LVM_SETITEMA = (LVM_FIRST+6)
LVM_INSERTITEM = LVM_INSERTITEMA
LVM_SETITEM = LVM_SETITEMA
LVM_DELETEALLITEMS =  (LVM_FIRST + 9)
LVM_SETITEMSTATE  =  (LVM_FIRST + 43)
LVM_GETITEMCOUNT  =  (LVM_FIRST + 4)
LVM_GETITEMSTATE   =  (LVM_FIRST + 44)
LVM_GETSELECTEDCOUNT =   (LVM_FIRST + 50)
LVM_SETCOLUMNA  =        (LVM_FIRST + 26)
LVM_SETCOLUMNW  =        (LVM_FIRST + 96)
LVM_SETCOLUMN = LVM_SETCOLUMNA
LVM_SETCOLUMNWIDTH =  (LVM_FIRST + 30)
LVM_GETITEMA   =         (LVM_FIRST + 5)
LVM_GETITEMW   =         (LVM_FIRST + 75)
LVM_GETITEM = LVM_GETITEMA
LVM_SETEXTENDEDLISTVIEWSTYLE = (LVM_FIRST + 54)

LVN_FIRST = (UINT_MAX) - 100
LVN_ITEMCHANGING    =    (LVN_FIRST-0)
LVN_ITEMCHANGED     =    (LVN_FIRST-1)
LVN_INSERTITEM      =    (LVN_FIRST-2)
LVN_DELETEITEM       =   (LVN_FIRST-3)
LVN_DELETEALLITEMS    =  (LVN_FIRST-4)
LVN_BEGINLABELEDITA   =  (LVN_FIRST-5)
LVN_BEGINLABELEDITW   =  (LVN_FIRST-75)
LVN_ENDLABELEDITA     =  (LVN_FIRST-6)
LVN_ENDLABELEDITW     =  (LVN_FIRST-76)
LVN_COLUMNCLICK       =  (LVN_FIRST-8)
LVN_BEGINDRAG         =  (LVN_FIRST-9)
LVN_BEGINRDRAG        =  (LVN_FIRST-11)


NM_OUTOFMEMORY    =      (NM_FIRST-1)
NM_CLICK          =      (NM_FIRST-2)   
NM_DBLCLK         =      (NM_FIRST-3)
NM_RETURN         =      (NM_FIRST-4)
NM_RCLICK         =      (NM_FIRST-5)   
NM_RDBLCLK        =      (NM_FIRST-6)
NM_SETFOCUS       =      (NM_FIRST-7)
NM_KILLFOCUS      =      (NM_FIRST-8)
NM_CUSTOMDRAW     =      (NM_FIRST-12)
NM_HOVER          =      (NM_FIRST-13)
NM_NCHITTEST      =      (NM_FIRST-14)  
NM_KEYDOWN        =      (NM_FIRST-15)  
NM_RELEASEDCAPTURE=      (NM_FIRST-16)
NM_SETCURSOR      =      (NM_FIRST-17)  
NM_CHAR           =      (NM_FIRST-18)  

LVCFMT_LEFT = 0
LVCFMT_RIGHT= 1
LVCFMT_CENTER   =     2
LVCFMT_JUSTIFYMASK =  3
LVCFMT_BITMAP_ON_RIGHT =4096
LVCFMT_COL_HAS_IMAGES = 32768
LVCFMT_IMAGE =2048


ICC_LISTVIEW_CLASSES =1
ICC_TREEVIEW_CLASSES =2
ICC_BAR_CLASSES      =4
ICC_TAB_CLASSES      =8
ICC_UPDOWN_CLASS =16
ICC_PROGRESS_CLASS =32
ICC_HOTKEY_CLASS =64
ICC_ANIMATE_CLASS= 128
ICC_WIN95_CLASSES= 255
ICC_DATE_CLASSES =256
ICC_USEREX_CLASSES =512
ICC_COOL_CLASSES =1024
ICC_INTERNET_CLASSES =2048
ICC_PAGESCROLLER_CLASS =4096
ICC_NATIVEFNTCTL_CLASS= 8192

TCN_FIRST  =  (UINT_MAX) -550
TCN_LAST   =  (UINT_MAX) -580
TCN_KEYDOWN   =  TCN_FIRST
TCN_SELCHANGE =        (TCN_FIRST-1)
TCN_SELCHANGING  =     (TCN_FIRST-2)

TVE_COLLAPSE =1
TVE_EXPAND   =2
TVE_TOGGLE   =3
TVE_COLLAPSERESET   = 0x8000

TCM_FIRST   = 0x1300
TCM_INSERTITEMA  =    (TCM_FIRST+7)
TCM_INSERTITEMW  =   (TCM_FIRST+62)
TCM_INSERTITEM = TCM_INSERTITEMA
TCM_ADJUSTRECT = (TCM_FIRST+40)
TCM_GETCURSEL   =     (TCM_FIRST+11)
TCM_SETCURSEL   =     (TCM_FIRST+12)
TCM_GETITEMA = (TCM_FIRST+5)
TCM_GETITEMW = (TCM_FIRST+60)
TCM_GETITEM = TCM_GETITEMA

TVN_FIRST  =  ((UINT_MAX)-400)
TVN_LAST   =  ((UINT_MAX)-499)
TVN_ITEMEXPANDINGA =  (TVN_FIRST-5)
TVN_ITEMEXPANDINGW =  (TVN_FIRST-54)
TVN_ITEMEXPANDING = TVN_ITEMEXPANDINGA
TVN_SELCHANGEDA  =    (TVN_FIRST-2)
TVN_SELCHANGEDW  =    (TVN_FIRST-51)
TVN_SELCHANGED  =  TVN_SELCHANGEDA
TVN_DELETEITEMA  =     (TVN_FIRST-9)
TVN_DELETEITEMW  =    (TVN_FIRST-58)
TVN_DELETEITEM = TVN_DELETEITEMA


SB_SIMPLE =   (WM_USER+9)
SB_SETTEXTA = (WM_USER+1)
SB_SETTEXTW = (WM_USER+11)
SB_SETTEXT = SB_SETTEXTA

SBT_OWNERDRAW   =     0x1000
SBT_NOBORDERS   =     256
SBT_POPOUT   = 512
SBT_RTLREADING =      1024
SBT_OWNERDRAW  =      0x1000
SBT_NOBORDERS  =      256
SBT_POPOUT   = 512
SBT_RTLREADING = 1024
SBT_TOOLTIPS = 0x0800

TBN_FIRST          =  ((UINT_MAX)-700)
TBN_DROPDOWN       =     (TBN_FIRST - 10)
TBN_HOTITEMCHANGE  =  (TBN_FIRST - 13)
TBDDRET_DEFAULT       =  0
TBDDRET_NODEFAULT     =  1
TBDDRET_TREATPRESSED  =  2

PBS_SMOOTH   = 0x01
PBS_VERTICAL = 0x04

CCM_FIRST      = 0x2000 # Common control shared messages
CCM_SETBKCOLOR = (CCM_FIRST + 1)

PBM_SETRANGE    = (WM_USER+1)
PBM_SETPOS      = (WM_USER+2)
PBM_DELTAPOS    = (WM_USER+3)
PBM_SETSTEP     = (WM_USER+4)
PBM_STEPIT      = (WM_USER+5)
PBM_SETRANGE32  = (WM_USER+6)
PBM_GETRANGE    = (WM_USER+7)
PBM_GETPOS      = (WM_USER+8)
PBM_SETBARCOLOR = (WM_USER+9)
PBM_SETBKCOLOR  = CCM_SETBKCOLOR

LB_ADDSTRING = 384
LB_INSERTSTRING = 385
LB_DELETESTRING = 386
LB_RESETCONTENT = 388
LB_GETCOUNT = 395
LB_SETTOPINDEX = 407

ImageList_Create = windll.comctl32.ImageList_Create
ImageList_Destroy = windll.comctl32.ImageList_Destroy
ImageList_AddMasked = windll.comctl32.ImageList_AddMasked
ImageList_AddIcon = windll.comctl32.ImageList_AddIcon
ImageList_SetBkColor = windll.comctl32.ImageList_SetBkColor


InitCommonControlsEx = windll.comctl32.InitCommonControlsEx

class Button(Window):
    _window_class_ = BUTTON
    _window_style_ = WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON
    
        
class StatusBar(Window):
    _window_class_ = STATUSCLASSNAME
    _window_style_ = WS_CHILD | WS_VISIBLE | SBS_SIZEGRIP

    def Simple(self, fSimple):
        self.SendMessage(SB_SIMPLE, fSimple, 0)
        
    def SetText(self, txt):
        self.SendMessage(SB_SETTEXT, (255 | SBT_NOBORDERS), txt)

class ComboBox(Window):
    _window_class_ = WC_COMBOBOXEX
    _window_style_ = WS_VISIBLE | WS_CHILD | CBS_DROPDOWN

class Edit(Window):
    _window_class__ = EDIT
    _window_style_ = WS_VISIBLE | WS_CHILD

class ListBox(Window):
    _window_class_ = 'ListBox'
    _window_style_ = WS_VISIBLE | WS_CHILD

    def AddString (self, txt):
        self.SendMessage(LB_ADDSTRING, 0, txt)

    def InsertString (self, idx, txt):
        self.SendMessage(LB_INSERTSTRING, idx, txt)

    def DeleteString (self, idx):
        self.SendMessage(LB_DELETESTRING, idx)

    def ResetContent (self):
        self.SendMessage(LB_RESETCONTENT)

    def GetCount (self):
        return self.SendMessage(LB_GETCOUNT)

    def SetTopIndex (self, idx):
        self.SendMessage (LB_SETTOPINDEX, idx)

class ProgressBar(Window):
    _window_class_ = PROGRESS_CLASS
    _window_style_ = WS_VISIBLE | WS_CHILD

    def SetRange(self, nMinRange, nMaxRange):
        if nMinRange > 65535 or nMaxRange > 65535:
            return self.SendMessage(PBM_SETRANGE32, nMinRange, nMaxRange)
        else:
            return self.SendMessage(PBM_SETRANGE, 0, MAKELPARAM(nMinRange, nMaxRange))

    def GetRange(self, fWhichLimit): # True=get low, False=get high range
        return self.SendMessage(PBM_GETRANGE, fWhichLimit, 0)

    def SetPos(self, nNewPos):
        return self.SendMessage(PBM_SETPOS, nNewPos, 0)

    def GetPos(self):
        return self.SendMessage(PBM_GETPOS, 0, 0)

    def SetBarColor(self, clrBar):
        return self.SendMessage(PBM_SETBARCOLOR, 0, clrBar)

    def SetBkColor(self, clrBk):
        return self.SendMessage(PBM_SETBKCOLOR, 0, clrBk)

    def SetStep(self, nStepInc):
        return self.SendMessage(PBM_SETSTEP, nStepInc, 0)

    def StepIt(self):
        return self.SendMessage(PBM_STEPIT, 0, 0)

    def DeltaPos(self, nIncrement):
        return self.SendMessage(PBM_DELTAPOS, nIncrement, 0)

class TrackBar(Window):
    _window_class_ = TRACKBAR_CLASS
    _window_style_ = WS_VISIBLE | WS_CHILD | TBS_AUTOTICKS | TBS_TOOLTIPS
    _window_style_ex_ = 0

    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)

    def SetRange(self, nMinRange, nMaxRange):
        return self.SendMessage(TBM_SETRANGE, 0, MAKELPARAM(nMinRange, nMaxRange))

    def SetPageSize(self, nSize):
        return self.SendMessage(TBM_SETPAGESIZE, 0, nSize)

    def GetPageSize(self):
        return self.SendMessage(TBM_GETPAGESIZE, 0, 0)

    def SetLineSize(self, nSize):
        return self.SendMessage(TBM_SETLINESIZE, 0, nSize)

    def GetLineSize(self):
        return self.SendMessage(TBM_GETLINESIZE, 0, 0)

    def GetRangeMin(self):
        return self.SendMessage(TBM_GETRANGEMIN, 0, 0)

    def GetRangeMax(self):
        return self.SendMessage(TBM_GETRANGEMAX, 0, 0)

    def SetPos(self,lPosition, fRedraw=1):
        return self.SendMessage(TBM_SETPOS, fRedraw, lPosition)

    def GetPos(self):
        return self.SendMessage(TBM_GETPOS, 0, 0)

    def ClearSel(self, fRedraw=0):
        return self.SendMessage(TBM_CLEARSEL, fRedraw, 0)

    def SetTickFreq(self, wFreq):
        return self.SendMessage(TBM_SETTICFREQ, wFreq, 0)

    def SetBuddy(self, hwndBuddy, fLocation=0):
        return self.SendMessage(TBM_SETBUDDY, fLocation, hwndBuddy)
    
class TabControl(Window):
    _window_class_ = WC_TABCONTROL
    _window_style_ = WS_VISIBLE | WS_CHILD | TCS_MULTILINE

    def InsertItem(self, iItem, item):        
        return self.SendMessage(TCM_INSERTITEM, iItem, byref(item))

    def GetItem(self, index, mask):
        item = TCITEM()
        item.mask = mask
        if self.SendMessage(TCM_GETITEM, index, byref(item)):
            return item
        else:
            raise "error"
        
    def AdjustRect(self, fLarger, rect):
        lprect = byref(rect)
        self.SendMessage(TCM_ADJUSTRECT, fLarger, lprect)

    def GetCurSel(self):
        return self.SendMessage(TCM_GETCURSEL)

    def SetCurSel(self, iItem):
        return self.SendMessage(TCM_SETCURSEL, iItem)
        
    
class TreeView(Window):
    _window_class_ = WC_TREEVIEW
    _window_style_ = WS_CHILD | WS_VISIBLE | WS_TABSTOP |\
                       TVS_HASBUTTONS|TVS_LINESATROOT|TVS_HASLINES
    _window_style_ex_ = 0

    def InsertItem(self, hParent, hInsertAfter, itemEx):
        insertStruct = TVINSERTSTRUCT()
        insertStruct.hParent = hParent
        insertStruct.hInsertAfter = hInsertAfter
        insertStruct.itemex = itemEx
        
        return self.SendMessage(TVM_INSERTITEM, 0, byref(insertStruct))
    
    def GetItem(self, item):
        return self.SendMessage(TVM_GETITEM, 0, byref(item))
        
    def SetImageList(self, imageList, iImage = TVSIL_NORMAL):
        return self.SendMessage(TVM_SETIMAGELIST, iImage, handle(imageList))

    def GetChildItem(self, hitem):
        """gets the first child of item"""
        return self.SendMessage(TVM_GETNEXTITEM, TVGN_CHILD, hitem)

    def GetNextItem(self, hitem):
        """gets the next sibling from item"""
        return self.SendMessage(TVM_GETNEXTITEM, TVGN_NEXT, hitem)
        
    def GetRootItem(self):
        """returns the root item"""
        return self.SendMessage(TVM_GETNEXTITEM, TVGN_ROOT)
    
    def CollapseAndReset(self, hitem):
        self.SendMessage(TVM_EXPAND, TVE_COLLAPSE|TVE_COLLAPSERESET, hitem)

    def DeleteAllItems(self):
        return self.SendMessage(TVM_DELETEITEM)

    def IsExpanded(self, hitem):
        return self.SendMessage(TVM_GETITEMSTATE, hitem, TVIS_EXPANDED)

    def Expand(self, hitem):
        return self.SendMessage(TVM_EXPAND, TVE_EXPAND, hitem)

    def EnsureVisible(self, hitem):
        return self.SendMessage(TVM_ENSUREVISIBLE, 0, hitem)

    def SelectItem(self, hitem):
        return self.SendMessage(TVM_SELECTITEM, TVGN_CARET, hitem)

    def GetSelection(self):
        return self.SendMessage(TVM_GETNEXTITEM, TVGN_CARET)
    
class ListView(Window):
    _window_class_ = WC_LISTVIEW
    _window_style_ = WS_CHILD | WS_VISIBLE | LVS_REPORT 
    _window_style_ex_ = 0
    _listview_style_ex_ = 0

    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        self.SetExtendedListViewStyle(self._listview_style_ex_, self._listview_style_ex_)
        
    def InsertColumn(self, iCol, lvcolumn):
        return self.SendMessage(LVM_INSERTCOLUMN, iCol, byref(lvcolumn))

    def SetColumn(self, iCol, lvcolumn):
        return self.SendMessage(LVM_SETCOLUMN, iCol, byref(lvcolumn))

    def SetColumnWidth(self, iCol, width):
        return self.SendMessage(LVM_SETCOLUMNWIDTH, iCol, width)
    
    def InsertItem(self, item):
        if item.iItem == -1: item.iItem = self.GetItemCount()
        return self.SendMessage(LVM_INSERTITEM, 0, byref(item))

    def SetItem(self, item):
        return self.SendMessage(LVM_SETITEM, 0, byref(item))

    def DeleteAllItems(self):
        return self.SendMessage(LVM_DELETEALLITEMS)

    def SetItemState(self, i, state, stateMask):
        item = LVITEM()
        item.iItem = i
        item.mask = LVIF_STATE
        item.state = state
        item.stateMask = stateMask
        return self.SendMessage(LVM_SETITEMSTATE, i, byref(item))

    def GetItemState(self, i, stateMask):
        return self.SendMessage(LVM_GETITEMSTATE, i, stateMask)
    
    def GetItemCount(self):
        return self.SendMessage(LVM_GETITEMCOUNT)

    def GetItemParam(self, i):
        item = LVITEM()
        item.iItem = i
        item.mask = LVIF_PARAM
        self.SendMessage(LVM_GETITEM, 0, byref(item))
        return item.lParam
    
    def SetItemCount(self, cItems, dwFlags = 0):
        self.SendMessage(LVM_SETITEMCOUNT, cItems, dwFlags)
        
    def GetSelectedCount(self):
        return self.SendMessage(LVM_GETSELECTEDCOUNT)

    def SetExtendedListViewStyle(self, dwExMask, dwExStyle):
        return self.SendMessage(LVM_SETEXTENDEDLISTVIEWSTYLE, dwExMask, dwExStyle)
    
class ToolBar(Window):
    _window_class_ = TOOLBARCLASSNAME
    _window_style_ = WS_CHILD | WS_VISIBLE

    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        self.SendMessage(TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)
        
    def PressButton(self, idButton, fPress):
        return self.SendMessage(TB_PRESSBUTTON, idButton, fPress)

    def GetRect(self, idCtrl):
        rc = RECT()
        self.SendMessage(TB_GETRECT, idCtrl, byref(rc))
        return rc

    def HitTest(self, pt):
        return self.SendMessage(TB_HITTEST, 0, byref(pt))
        
    def SetHotItem(self, idButton):
        return self.SendMessage(TB_SETHOTITEM, idButton)

    def GetHotItem(self):
        return self.SendMessage(TB_GETHOTITEM)

    def InsertButton(self, iButton, tbButton):
        return self.SendMessage(TB_INSERTBUTTON, iButton, byref(tbButton))

    def SetImageList(self, imageList, iImage = 0):
        return self.SendMessage(TB_SETIMAGELIST, iImage, handle(imageList))

    def SetButtonSize(self, dxButton, dyButton):
        return self.SendMessage(TB_SETBUTTONSIZE, 0, MAKELONG(dxButton, dyButton))
            
class Rebar(Window):
    _window_class_ = REBARCLASSNAME
    _window_style_ = WS_CHILDWINDOW|WS_VISIBLE|WS_CLIPSIBLINGS|WS_CLIPCHILDREN|WS_BORDER|\
                       RBS_VARHEIGHT|RBS_BANDBORDERS|RBS_AUTOSIZE|RBS_DBLCLKTOGGLE|\
                       RBS_REGISTERDROP|CCS_NODIVIDER|CCS_TOP|CCS_NOPARENTALIGN
    _window_style_ex_ = WS_EX_LEFT|WS_EX_LTRREADING|WS_EX_RIGHTSCROLLBAR|WS_EX_TOOLWINDOW

    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        
        rebarInfo = REBARINFO()
        rebarInfo.cbSize = sizeof(REBARINFO)
        rebarInfo.fMask = 0
        rebarInfo.himl = NULL
        self.SendMessage(RB_SETBARINFO, 0, byref(rebarInfo))

class ImageList(WindowsObject):
    __dispose__ = ImageList_Destroy
    
    def __init__(self, cx, cy, flags, cInitial, cGrow):
        WindowsObject.__init__(self, ImageList_Create(cx, cy, flags, cInitial, cGrow))

    def AddMasked(self, bitmap, crMask):
        return ImageList_AddMasked(self.handle, handle(bitmap), crMask)

    def SetBkColor(self, clrRef):
        ImageList_SetBkColor(self.handle, clrRef)
        
    def AddIcon(self, hIcon):
        return ImageList_AddIcon(self.handle, hIcon)

    def AddIconsFromModule(self, moduleName, cx, cy, uFlags):
        hdll = GetModuleHandle(moduleName)
        i = 1
        #dont know how many icons there are in module, this loop
        #breaks if there are no more because then an exception is thrown:
        while 1:
            try:
                hIcon = LoadImage(hdll, i , IMAGE_ICON, cx, cy, uFlags)
                self.AddIcon(hIcon)
            except:
                break
            i += 1

        
def InitCommonControls(dwICC):
    iccex = INITCOMMONCONTROLSEX()
    iccex.dwSize = sizeof(INITCOMMONCONTROLSEX)
    iccex.dwICC = dwICC
    InitCommonControlsEx(byref(iccex))
