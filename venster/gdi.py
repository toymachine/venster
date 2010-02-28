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
from windows import *

class BITMAP(Structure):
    _fields_ = [("bmType", LONG),
    		("bmWidth", LONG),
    		("bmHeight", LONG),
    		("bmWidthBytes", LONG),
    		("bmPlanes", WORD),
    		("bmBitsPixel", WORD),
    		("bmBits", LPVOID)]

LF_FACESIZE = 32

class LOGFONT(Structure):
    _fields_ = [("lfHeight", LONG),
                ("lfWidth", LONG),                
                ("lfEscapement", LONG),
                ("lfOrientation", LONG),
                ("lfWeight", LONG),
                ("lfItalic", BYTE),
                ("lfUnderline", BYTE),
                ("lfStrikeOut", BYTE),
                ("lfCharSet", BYTE),
                ("lfOutPrecision", BYTE),
                ("lfClipPrecision", BYTE),
                ("lfQuality", BYTE), 
                ("lfPitchAndFamily", BYTE),
                ("lfFaceName", TCHAR * LF_FACESIZE)]

class LOGBRUSH(Structure):
    _fields_ = [("lbStyle", UINT),
                ("lbColor", COLORREF),
                ("lbHatch", LONG)]
    
class ENUMLOGFONTEX(Structure):
    _fields_ = [("elfLogFont", LOGFONT),
                ("elfFullName", TCHAR * LF_FACESIZE),
                ("elfStyle", TCHAR * LF_FACESIZE),
                ("elfScript", TCHAR * LF_FACESIZE)]

EnumFontFamExProc = WINFUNCTYPE(c_int, POINTER(ENUMLOGFONTEX), POINTER(DWORD), DWORD, LPARAM)    

MONO_FONT = 8
OBJ_FONT = 6
ANSI_FIXED_FONT  = 11
ANSI_VAR_FONT = 12
DEVICE_DEFAULT_FONT= 14
DEFAULT_GUI_FONT= 17
OEM_FIXED_FONT= 10
SYSTEM_FONT= 13
SYSTEM_FIXED_FONT= 16

ANSI_CHARSET          =  0
DEFAULT_CHARSET       =  1
SYMBOL_CHARSET        =  2
SHIFTJIS_CHARSET      =  128
HANGEUL_CHARSET       =  129
HANGUL_CHARSET        =  129
GB2312_CHARSET        =  134
CHINESEBIG5_CHARSET   =  136
OEM_CHARSET           =  255

FIXED_PITCH = 1

CLR_NONE = 0xffffffff

HS_BDIAGONAL   =3
HS_CROSS       =4
HS_DIAGCROSS   =5
HS_FDIAGONAL   =2
HS_HORIZONTAL  =0
HS_VERTICAL    =1

PATINVERT     =  0x5A0049

OUT_DEFAULT_PRECIS  =  0
CLIP_DEFAULT_PRECIS  = 0
DEFAULT_QUALITY      =  0
DEFAULT_PITCH        =  0

FF_DONTCARE   =  (0<<4)
FF_MODERN     =  (3<<4)

PS_GEOMETRIC=   65536
PS_COSMETIC  =  0
PS_ALTERNATE  = 8
PS_SOLID      = 0
PS_DASH       = 1
PS_DOT= 2
PS_DASHDOT    = 3
PS_DASHDOTDOT = 4
PS_NULL       = 5
PS_USERSTYLE  = 7
PS_INSIDEFRAME= 6
PS_ENDCAP_ROUND =       0
PS_ENDCAP_SQUARE=       256
PS_ENDCAP_FLAT= 512
PS_JOIN_BEVEL = 4096
PS_JOIN_MITER = 8192
PS_JOIN_ROUND = 0
PS_STYLE_MASK = 15
PS_ENDCAP_MASK= 3840
PS_TYPE_MASK  = 983040

BS_SOLID     =  0
BS_NULL       = 1
BS_HOLLOW     = 1
BS_HATCHED    = 2
BS_PATTERN    = 3
BS_INDEXED    = 4
BS_DIBPATTERN = 5
BS_DIBPATTERNPT =       6
BS_PATTERN8X8 = 7
BS_DIBPATTERN8X8 =      8
 
GetStockObject = windll.gdi32.GetStockObject
LineTo = windll.gdi32.LineTo
MoveToEx = windll.gdi32.MoveToEx
FillRect = windll.user32.FillRect
DrawEdge = windll.user32.DrawEdge
CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
CreateCompatibleDC.restype = ValidHandle
SelectObject = windll.gdi32.SelectObject
GetObject = windll.gdi32.GetObjectA
DeleteObject = windll.gdi32.DeleteObject
BitBlt = windll.gdi32.BitBlt
StretchBlt = windll.gdi32.StretchBlt
GetSysColorBrush = windll.user32.GetSysColorBrush
CreateHatchBrush = windll.gdi32.CreateHatchBrush
CreatePatternBrush = windll.gdi32.CreatePatternBrush
CreateSolidBrush = windll.gdi32.CreateSolidBrush
CreateBitmap = windll.gdi32.CreateBitmap
PatBlt = windll.gdi32.PatBlt
CreateFont = windll.gdi32.CreateFontA
EnumFontFamiliesEx = windll.gdi32.EnumFontFamiliesExA
InvertRect = windll.user32.InvertRect
DrawFocusRect = windll.user32.DrawFocusRect
ExtCreatePen = windll.gdi32.ExtCreatePen
CreatePen = windll.gdi32.CreatePen


