from venster.windows import *
from venster.wtl import *
from ctypes import c_char

try:
    LoadLibrary("SciLexer.DLL")
except Exception, e:
    MessageBox(0, "The Scintilla DLL could not be loaded.",
               "Error loading Scintilla", MB_OK | MB_ICONERROR)
    raise e

SCN_STYLENEEDED = 2000
SCN_CHARADDED = 2001
SCN_SAVEPOINTREACHED= 2002
SCN_SAVEPOINTLEFT= 2003
SCN_MODIFYATTEMPTRO= 2004
SCN_KEY= 2005
SCN_DOUBLECLICK= 2006
SCN_UPDATEUI= 2007
SCN_MODIFIED= 2008
SCN_MACRORECORD= 2009
SCN_MARGINCLICK= 2010
SCN_NEEDSHOWN= 2011
SCN_PAINTED= 2013
SCN_USERLISTSELECTION =2014
SCN_URIDROPPED= 2015
SCN_DWELLSTART= 2016
SCN_DWELLEND= 2017
SCN_ZOOM= 2018
SCN_HOTSPOTCLICK= 2019
SCN_HOTSPOTDOUBLECLICK= 2020
SCN_CALLTIPCLICK= 2021

SCI_SETTEXT = 2181
SCI_SETLEXERLANGUAGE = 4006
SCI_SETPROPERTY = 4004
SCI_GETLEXER = 4002
SCI_SETKEYWORDS = 4005
SCI_STYLESETFORE = 2051
SCI_STYLESETBACK= 2052
SCI_STYLESETBOLD= 2053
SCI_STYLESETITALIC= 2054
SCI_STYLESETSIZE= 2055
SCI_STYLESETFONT= 2056
SCI_STYLESETEOLFILLED= 2057
SCI_STYLERESETDEFAULT= 2058
SCI_STYLESETUNDERLINE= 2059
SCI_STYLECLEARALL= 2050
SCI_GETSELECTIONSTART= 2143
SCI_GETSELECTIONEND= 2145
SCI_GETSELTEXT= 2161
SCI_ADDTEXT= 2001
SCI_SETTABWIDTH= 2036
SCI_SETTABINDENTS= 2260
SCI_SETUSETABS= 2124
SCI_SETEOLMODE= 2031
SCI_SELECTALL= 2013
SCI_DOCUMENTEND= 2318
SCI_CUT= 2177
SCI_COPY= 2178
SCI_COPYRANGE= 2419
SCI_COPYTEXT= 2420
SCI_PASTE= 2179
SCI_REDO= 2011
SCI_UNDO= 2176
SCI_CANUNDO= 2174
SCI_CANREDO=2016
SCI_CANPASTE=2173
SCI_CLEAR=2180

STYLE_DEFAULT = 32
 
SCE_P_DEFAULT= 0
SCE_P_COMMENTLINE= 1
SCE_P_NUMBER= 2
SCE_P_STRING= 3
SCE_P_CHARACTER= 4
SCE_P_WORD= 5
SCE_P_TRIPLE= 6
SCE_P_TRIPLEDOUBLE= 7
SCE_P_CLASSNAME= 8
SCE_P_DEFNAME= 9
SCE_P_OPERATOR= 10
SCE_P_IDENTIFIER= 11
SCE_P_COMMENTBLOCK= 12
SCE_P_STRINGEOL= 13

SC_EOL_CRLF = 0
SC_EOL_CR = 1
SC_EOL_LF = 2

class SCNotification(Structure):
    _fields_ = [("nmhdr", NMHDR),
                ("position", c_int),
                ("ch", c_int),
                ("modifiers", c_int),
                ("modificationType", c_int),
                ("text", c_char_p),
                ("length", c_int),                
                ("linesAdded", c_int),
                ("message", c_int),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("line", c_int),
                ("foldLevelNow", c_int),
                ("foldLevelPrev", c_int),
                ("margin", c_int),
                ("listType", c_int),
                ("x", c_int),
                ("y", c_int)]
                

copyright = \
"""
Scintilla
Copyright 1998-2003 by Neil Hodgson <neilh@scintilla.org>
All Rights Reserved
"""

class Scintilla(Window):
    _class_ = "Scintilla"
    _class_ws_style_ = WS_VISIBLE | WS_CHILD

    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        self.InterceptParent()

    def GetNotification(self, event):
        return SCNotification.from_address(int(event.lParam))
    
    def SendScintillaMessage(self, msg, wParam, lParam):
        #TODO use fast path,e.g. retreive direct message fn from
        #scintilla as described in scintilla docs
        return self.SendMessage(msg, wParam, lParam)
        
    def SetText(self, txt):
        self.SendScintillaMessage(SCI_SETTEXT, 0, txt)

    def GetLexer(self):
        return self.SendScintillaMessage(SCI_GETLEXER, 0, 0)
    
    def SetLexerLanguage(self, lang):
        self.SendScintillaMessage(SCI_SETLEXERLANGUAGE, 0, lang)
        
    def SetProperty(self, key, value):
        self.SendScintillaMessage(SCI_SETPROPERTY, key, value)

    def SetKeyWords(self, keyWordSet, keyWordList):
        self.SendScintillaMessage(SCI_SETKEYWORDS, keyWordSet, " ".join(keyWordList))

    def StyleSetFore(self, styleNumber, color):
        self.SendScintillaMessage(SCI_STYLESETFORE, styleNumber, color)

    def StyleSetBack(self, styleNumber, color):
        self.SendScintillaMessage(SCI_STYLESETBACK, styleNumber, color)

    def StyleSetSize(self, styleNumber, size):
        self.SendScintillaMessage(SCI_STYLESETSIZE, styleNumber, size)

    def StyleSetFont(self, styleNumber, face):
        self.SendScintillaMessage(SCI_STYLESETFONT, styleNumber, face)

    def StyleClearAll(self):
        self.SendScintillaMessage(SCI_STYLECLEARALL, 0, 0)

    def GetSelText(self):
        start = self.SendScintillaMessage(SCI_GETSELECTIONSTART, 0, 0)
        end = self.SendScintillaMessage(SCI_GETSELECTIONEND, 0, 0)
        if start == end: return ""
        buff = (c_char * (end - start + 1))()
        self.SendScintillaMessage(SCI_GETSELTEXT, 0, byref(buff))
        return str(buff.value)

    def HasSelection(self):
        start = self.SendScintillaMessage(SCI_GETSELECTIONSTART, 0, 0)
        end = self.SendScintillaMessage(SCI_GETSELECTIONEND, 0, 0)
        return (end - start) > 0
    
    def AddText(self, text):
        self.SendScintillaMessage(SCI_ADDTEXT, len(text), text)
        
    def SetTabWidth(self, width):
        self.SendScintillaMessage(SCI_SETTABWIDTH, width, 0)
        
    def SetUseTabs(self, useTabs):
        self.SendScintillaMessage(SCI_SETUSETABS, int(useTabs), 0)

    def SetEolMode(self, eolMode):
        self.SendScintillaMessage(SCI_SETEOLMODE, eolMode, 0)

    def Undo(self):
        self.SendScintillaMessage(SCI_UNDO, 0, 0)

    def Redo(self):
        self.SendScintillaMessage(SCI_REDO, 0, 0)

    def CanUndo(self):
        return self.SendScintillaMessage(SCI_CANUNDO, 0, 0)

    def CanRedo(self):
        return self.SendScintillaMessage(SCI_CANREDO, 0, 0)

    def Cut(self):
        self.SendScintillaMessage(SCI_CUT, 0, 0)

    def Copy(self):
        self.SendScintillaMessage(SCI_COPY, 0, 0)

    def Clear(self):
        self.SendScintillaMessage(SCI_CLEAR, 0, 0)

    def Paste(self):
        self.SendScintillaMessage(SCI_PASTE, 0, 0)

    def CanPaste(self):
        return self.SendScintillaMessage(SCI_CANPASTE, 0, 0)

    def SelectAll(self):
        self.SendScintillaMessage(SCI_SELECTALL, 0, 0)
        

        
