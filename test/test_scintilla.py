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

copyright = \
"""
Snakepad
Copyright 2003 by Henk Punt <henk@entree.nl>
All Rights Reserved
"""

from venster.windows import *
from venster.wtl import *
from venster import comctl
from venster import gdi

from venster.lib import form
from venster.lib import scintilla
from venster.lib import splitter

import sys
import keyword
import code

#some colors:
Black = 0x000000
White = 0xFFFFFF
Blue = 0xFF0000
RosyBrown = 0x8F8FBC
FireBrick = 0x2222B2
Purple = 0x800080
ForestGreen = 0x228B22

class PyScintilla(scintilla.Scintilla):
    #the foreground colors for the diffent python code components defined by scintilla
    _styles_ = [(scintilla.SCE_P_WORD, Purple),
                (scintilla.SCE_P_COMMENTLINE, FireBrick),
                (scintilla.SCE_P_STRING, RosyBrown),
                (scintilla.SCE_P_TRIPLE, RosyBrown),
                (scintilla.SCE_P_TRIPLEDOUBLE, RosyBrown),
                (scintilla.SCE_P_CHARACTER, RosyBrown),
                (scintilla.SCE_P_CLASSNAME, ForestGreen),
                (scintilla.SCE_P_DEFNAME, Blue),
                (scintilla.SCE_P_COMMENTBLOCK, FireBrick)]
    
    def __init__(self, *args, **kwargs):
        scintilla.Scintilla.__init__(self, *args, **kwargs)

        self.SetLexerLanguage("python")
        #set default style:
        self.StyleSetFore(scintilla.STYLE_DEFAULT, Black)
        self.StyleSetBack(scintilla.STYLE_DEFAULT, White)
        self.StyleSetSize(scintilla.STYLE_DEFAULT, 9)
        niceFont = self.GetNiceFont()
        if niceFont: self.StyleSetFont(scintilla.STYLE_DEFAULT, niceFont)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetEolMode(scintilla.SC_EOL_LF)
        self.StyleClearAll() #copy defaults to all styles
        
        #set font color for python keywords, comments etc
        self.SetKeyWords(0, keyword.kwlist)
        for styleNumber, fore in self._styles_:
            self.StyleSetFore(styleNumber, fore)

    def FontNameProc(self, lpelfe, lpntme, FontType, lParam):
        """Callback called by windows to enumerate fonts"""
        if lpelfe.contents.elfLogFont.lfPitchAndFamily & FIXED_PITCH:
            self.monoFonts[lpelfe.contents.elfFullName] = 1
        
    def GetNiceFont(self):
        """gets the name of the nicest monospace font on the system"""
        logfont = gdi.LOGFONT()
        logfont.lfCharSet = gdi.DEFAULT_CHARSET
        logfont.lfPitchAndFamily = gdi.FIXED_PITCH
        hdc = GetDC(0);
        self.monoFonts = {}
        #callback fills in self.monoFonts
        gdi.EnumFontFamiliesEx(hdc, byref(logfont), gdi.EnumFontFamExProc(self.FontNameProc), 0, 0)
        ReleaseDC(0, hdc)
        for niceFont in ["Andale Mono", "Courier New", "Courier", "Fixedsys"]:
            if self.monoFonts.has_key(niceFont):
                return niceFont
        return None

class Editor(PyScintilla):
    """A python editor based on the scintilla control"""

    def __init__(self, *args, **kwargs):
        PyScintilla.__init__(self, *args, **kwargs)


class Console(PyScintilla, code.InteractiveConsole):
    """a python console based on the scintilla editor"""
    
    def __init__(self, *args, **kwargs):
        PyScintilla.__init__(self, *args, **kwargs)
        code.InteractiveConsole.__init__(self)

        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "

        cprt = 'Type "copyright", "credits" or "license" for more information.'
        self.write("## Python %s on %s\n## %s\n" %
                   (sys.version, sys.platform, cprt))

        self.buff = []
        self.more = 0
        self.prompt()

        self.olderr = sys.stderr
        sys.stdout = self
        sys.stderr = self
        
    def write(self, msg):
        self.AddText(msg)

    def prompt(self):
        if self.more:
            prompt = sys.ps2
        else:
            prompt = sys.ps1

        self.AddText(prompt)
        
    def OnCharAdded(self, event):
        ch = self.GetNotification(event).ch
        if ch == 10: #line added
            line = "".join(map(chr, self.buff))
            self.buff = []
            print >> self.olderr, line
            self.more = self.push(line)
            self.prompt()
        else:
            self.buff.append(ch)

    _msg_map_ = MSG_MAP(\
        [NTF_HANDLER(scintilla.SCN_CHARADDED, OnCharAdded)])


ID_EVAL = 8001
CTRL_EDITOR = "editor"

class MainForm(form.Form):
    _class_icon_ = _class_icon_sm_ = Icon("CHICKEN.ICO")

    _class_accels_ = [(FCONTROL|FVIRTKEY, ord("E"), ID_EVAL),
                      (FCONTROL|FVIRTKEY, ord("N"), form.ID_NEW)]
    
    _class_form_exit_ = form.EXIT_ONLASTDESTROY

    _class_form_status_msgs_ = {form.ID_NEW: "Creates a new window."}

    _form_title_ = "Snakepad"

    _form_menu_ = [(MF_POPUP, "&File",
                    [(MF_STRING, "&New\tCtrl+N", form.ID_NEW),
                     (MF_SEPARATOR,),
                     (MF_STRING, "&Exit", form.ID_EXIT)]),
                   (MF_POPUP, "&Edit",
                    [(MF_STRING, "&Undo\tCtrl+Z", form.ID_UNDO),
                     (MF_STRING, "&Redo\tCtrl+Y", form.ID_REDO),
                     (MF_SEPARATOR,),
                     (MF_STRING, "Cu&t\tCtrl+X", form.ID_CUT),
                     (MF_STRING, "&Copy\tCtrl+C", form.ID_COPY),
                     (MF_STRING, "&Paste\tCtrl+V", form.ID_PASTE),
                     (MF_STRING, "&Delete\tDel", form.ID_CLEAR),
                     (MF_SEPARATOR,),
                     (MF_STRING, "Select &All\tCtrl+A", form.ID_SELECTALL)])]
                     
    def __init__(self):
        form.Form.__init__(self)      

        aSplitter = splitter.Splitter(parent = self,
                                      orientation = splitter.HORIZONTAL,
                                      splitPos = int(self.clientRect.height * 0.6))

        aEditor =  Editor(parent = aSplitter, orExStyle = WS_EX_CLIENTEDGE)
        aConsole = Console(parent = aSplitter, orExStyle = WS_EX_CLIENTEDGE)

        aSplitter.Add(0, aEditor)
        aSplitter.Add(1, aConsole)

        self.controls.Add(form.CTRL_VIEW, aSplitter)
        self.controls.Add(form.CTRL_STATUSBAR, comctl.StatusBar(parent = self))
        self.controls.Add(CTRL_EDITOR, aEditor)
        self.controls.Add(aConsole)

    def OnNew(self, event):
        form = MainForm()
        form.ShowWindow()

    editor = property(lambda self: self.controls[CTRL_EDITOR])
    
    def OnEval(self, event):
        self.console.Eval()
        
    def OnActivate(self, event):
        #if form is activated, set focus to editor
        if (HIWORD(event.wParam), LOWORD(event.wParam)) == (0, 1): self.editor.SetFocus()
        
    _msg_map_ = MSG_MAP(\
        [MSG_HANDLER(WM_ACTIVATE, OnActivate),
         CMD_ID_HANDLER(form.ID_NEW, OnNew),
         CMD_ID_HANDLER(form.ID_UNDO,
                        lambda self, event: self.editor.Undo()),
         form.CMD_UI_UPDATE(form.ID_UNDO,
                            lambda self, event: event.Enable(self.editor.CanUndo())),
         CMD_ID_HANDLER(form.ID_REDO,
                        lambda self, event: self.editor.Redo()),
         form.CMD_UI_UPDATE(form.ID_REDO,
                            lambda self, event: event.Enable(self.editor.CanRedo())),
         CMD_ID_HANDLER(form.ID_CUT,
                        lambda self, event: self.editor.Cut()),
         form.CMD_UI_UPDATE(form.ID_CUT,
                            lambda self, event: event.Enable(self.editor.HasSelection())),
         CMD_ID_HANDLER(form.ID_COPY,
                        lambda self, event: self.editor.Copy()),
         form.CMD_UI_UPDATE(form.ID_COPY,
                            lambda self, event: event.Enable(self.editor.HasSelection())),
         CMD_ID_HANDLER(form.ID_PASTE,
                        lambda self, event: self.editor.Paste()), 
         form.CMD_UI_UPDATE(form.ID_PASTE,
                            lambda self, event: event.Enable(self.editor.CanPaste())),
         CMD_ID_HANDLER(form.ID_CLEAR,
                        lambda self, event: self.editor.Clear()), 
         form.CMD_UI_UPDATE(form.ID_CLEAR,
                            lambda self, event: event.Enable(self.editor.HasSelection())),
         CMD_ID_HANDLER(form.ID_SELECTALL,
                        lambda self, event: self.editor.SelectAll()),
         CMD_ID_HANDLER(ID_EVAL, OnEval),
         CHAIN_MSG_MAP(form.Form._msg_map_)])

if __name__ == '__main__':
    mainForm = MainForm()        
    mainForm.ShowWindow()

    application = Application()
    application.Run()


