from windows import *
from wtl import *

from comtypes import GUID

NIN_SELECT          = (WM_USER + 0)
NINF_KEY            = 0x1
NIN_KEYSELECT       = (NIN_SELECT | NINF_KEY)

NIN_BALLOONSHOW     = (WM_USER + 2)
NIN_BALLOONHIDE     = (WM_USER + 3)
NIN_BALLOONTIMEOUT  = (WM_USER + 4)
NIN_BALLOONUSERCLICK = (WM_USER + 5)


NIM_ADD        = 0x00000000
NIM_MODIFY     = 0x00000001
NIM_DELETE     = 0x00000002
NIM_SETFOCUS   = 0x00000003
NIM_SETVERSION = 0x00000004


NIF_MESSAGE    = 0x00000001
NIF_ICON       = 0x00000002
NIF_TIP        = 0x00000004
NIF_STATE      = 0x00000008
NIF_INFO       = 0x00000010
NIF_GUID       = 0x00000020

NIS_HIDDEN            =  0x00000001
NIS_SHAREDICON        =  0x00000002

NIIF_NONE      = 0x00000000
NIIF_INFO      = 0x00000001
NIIF_WARNING   = 0x00000002
NIIF_ERROR     = 0x00000003
NIIF_ICON_MASK = 0x0000000F
NIIF_NOSOUND   = 0x00000010

NOTIFYICON_VERSION = 3

CSIDL_LOCAL_APPDATA = 0x001c

SHGFP_TYPE_CURRENT  = 0
SHGFP_TYPE_DEFAULT  = 1

class NOTIFYICONDATA(Structure):
    _fields_ = [("cbSize", DWORD),
                ("hWnd", HWND),
                ("uID", UINT),
                ("uFlags", UINT),
                ("uCallbackMessage", UINT),
                ("hIcon", HICON),
                ("szTip", TCHAR * 64),
                ("dwState", DWORD),
                ("dwStateMask", DWORD),
                ("szInfo", TCHAR * 256),
                ("uVersion", UINT), #todo really a union
                ("szInfoTitle", TCHAR * 64),
                ("dwInfoFlags", DWORD),
                ("guidItem", GUID)]

Shell_NotifyIcon = windll.shell32.Shell_NotifyIcon
SHGetFolderPath = windll.shell32.SHGetFolderPathA
