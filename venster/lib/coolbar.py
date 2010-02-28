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

from venster.windows import *
from venster.comctl import *

WM_TRACK = WM_USER + 1

class CommandBar(ToolBar):
    def __init__(self, *args, **kwargs):
        ToolBar.__init__(self, *args, **kwargs)
        
        self.SendMessage(TB_SETIMAGELIST, 0, 0)
        self.SendMessage(TB_SETDRAWTEXTFLAGS, DT_HIDEPREFIX, DT_HIDEPREFIX)
        
        self.parentNotify = self.Intercept(self.GetParent(), self._msg_map2_)

        #TODO remove on dispose
        GetMessageLoop().AddFilter(self.PreTranslateMessage)        
        self.cbHook = MessageProc(self.OnHook)
        #TODO remove on dispose
        
        self.iCurMenu = -1
        self.inTrackPopupMenu = 0
        self.isHotTracking = 0
        self.inCancel = 0
        self.menuActive = 0
        self.atPopupItem = 0 #>0 when menu item is selected which will popup submenu
        
    def OnHook(self, nCode, wParam, lParam):
        if nCode > 0:            
            msg = MSG.from_address(int(lParam))
            #print msg
            result, handled = self._msg_hook_.DispatchMSG(self, msg)
            if handled:
                return 1 #prevent other hooks from processing
            
        return CallNextHookEx(self.hHook, nCode, wParam, lParam)
        
    def MenuActiveToggle(self):
        if not self.menuActive:        
            SendMessage(self.handle, TB_SETDRAWTEXTFLAGS, DT_HIDEPREFIX, 0)
            self.menuActive = 1
        else:
            SendMessage(self.handle, TB_SETDRAWTEXTFLAGS, DT_HIDEPREFIX, DT_HIDEPREFIX)
            self.menuActive = 0

        self.Invalidate()
        self.UpdateWindow()

    def AttachMenu(self, menu):
        idc = 0
        self.menu = menu
        
        self.SetRedraw(FALSE)

        minfo = MENUITEMINFO()
        strbuff = '\0' * 255
        for i in range(GetMenuItemCount(handle(menu))):
            minfo.cbSize = sizeof(MENUITEMINFO)
            minfo.fMask = MIIM_STATE | MIIM_TYPE | MIIM_SUBMENU
            minfo.fType = MFT_STRING
            minfo.cch = 255 #TODO max
            minfo.dwTypeData = strbuff
            GetMenuItemInfo(menu.handle, i, 1, byref(minfo))
            tbButt = TBBUTTON()
            tbButt.iBitmap = I_IMAGENONE
            tbButt.idCommand = i
            tbButt.fsState = TBSTATE_ENABLED
            tbButt.fsStyle = TBSTYLE_BUTTON | TBSTYLE_AUTOSIZE | TBSTYLE_DROPDOWN
            tbButt.dwData = 0
            tbButt.iString = 0

            SendMessage(self.handle, TB_INSERTBUTTON, -1, byref(tbButt))

            bi = TBBUTTONINFO()
            bi.cbSize = sizeof(TBBUTTONINFO)
            bi.dwMask = TBIF_TEXT
            bi.pszText = "  " + minfo.dwTypeData

            SendMessage(self.handle, TB_SETBUTTONINFO, i, byref(bi))

        self.SetRedraw(TRUE)
        self.Invalidate()
        self.UpdateWindow()

    def OnDropDown(self, event):
        if event.nmhdr.hwndFrom != self.handle: return
        #print "dropdown"
        nmtoolbar = NMTOOLBAR.from_address(int(event.lParam))
        self.isHotTracking = 1
        self.TrackPopupMenu(nmtoolbar.iItem)

    def OnTrackPopupMenu(self, event):
        self.Cancel()

        print "track: ", event.wParam, self.inTrackPopupMenu, self.isHotTracking
        self.TrackPopupMenu(event.wParam)
        
    def TrackPopupMenu(self, iMenu):
        print "tpm", iMenu
        if iMenu < 0: return
        self.iCurMenu = iMenu

        self.PressButton(iMenu, 1)
        
        self.hHook = SetWindowsHookEx(WH_MSGFILTER, self.cbHook, hInstance, GetCurrentThreadId())

        #position popup menu right under button
        btnRc = self.GetRect(iMenu)
        pt = POINT(btnRc.left, btnRc.bottom)
        self.ClientToScreen(pt)
        self.inTrackPopupMenu = 1
        print "inTrackPopupMenu"
        self.menu.GetSubMenu(iMenu).TrackPopupMenuEx(TPM_LEFTBUTTON | TPM_VERTICAL |\
                                                     TPM_LEFTALIGN | TPM_TOPALIGN,\
                                                     int(pt.x), int(pt.y), self, 0)
        print "exitTrackPopupMenu"
        self.inTrackPopupMenu = 0

        UnhookWindowsHookEx(self.hHook)
        if not self.inCancel:
            #drop out of hot tracking mode
            self.isHotTracking = 0
        self.inCancel = 0
        
        self.PressButton(iMenu, 0)
        
    def OnHotItemChange(self, event):
        print "onhic"
        nmhi = NMTBHOTITEM.from_address(int(event.lParam))
        if nmhi.idNew != self.iCurMenu and not self.inTrackPopupMenu and self.isHotTracking:
            self.TrackPopupMenu(nmhi.idNew)
            
    def Cancel(self):
        self.inCancel = 1
        self.SendMessage(WM_CANCELMODE)
        
    def OnHookMouseMove(self, event):
        """test if mouse moves out of current popup menu and cancels
        it when so"""
        pt = GET_POINT_LPARAM(event.lParam)
        self.ScreenToClient(pt)
        hit = self.HitTest(pt)
        if hit >= 0 and hit != self.iCurMenu:
            self.Cancel()
            
        event.handled = 0

    def OnKeyDown(self, event):
        if event.wParam == VK_DOWN:
            pass
##            self.TrackPopupMenu(self.GetHotItem())
        elif event.wParam == VK_LEFT:
            print "left"
        elif event.wParam == VK_RIGHT and not self.atPopupItem:
            print "select next menu", self.iCurMenu
            self.PostMessage(WM_TRACK, self.iCurMenu + 1)
            
        event.handled = 0

    def OnPtlSysKeyDown(self, event):
        self.MenuActiveToggle()
        event.handled = 0

    def OnPtlSysKeyUp(self, event):
        event.handled = 0
    
    def PreTranslateMessage(self, msg):
        self._msg_ptl_.DispatchMSG(self, msg)

    def OnDestroy(self, event):
        #print "destroy commandbar"
        GetMessageLoop().RemoveFilter(self.PreTranslateMessage)

    def OnMenuPopup(self, event):
        print "omp"

    def OnHookMenuSelect(self, event):
        self.atPopupItem = HIWORD(event.wParam) & MF_POPUP
        
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_DESTROY, OnDestroy),
                         MSG_HANDLER(WM_INITMENUPOPUP, OnMenuPopup),
                         MSG_HANDLER(WM_TRACK, OnTrackPopupMenu)])
    
    #parent notifications comming from common control
    _msg_map2_ = MSG_MAP([NTF_HANDLER(TBN_DROPDOWN, OnDropDown),
                          NTF_HANDLER(TBN_HOTITEMCHANGE, OnHotItemChange)])

    #msgs received during popup tracking from msg hook
    _msg_hook_ = MSG_MAP([MSG_HANDLER(WM_MOUSEMOVE, OnHookMouseMove),
                          MSG_HANDLER(WM_KEYDOWN, OnKeyDown),
                          MSG_HANDLER(WM_MENUSELECT, OnHookMenuSelect)])

    #pretranslate msgs
    _msg_ptl_ = MSG_MAP([MSG_HANDLER(WM_KEYDOWN, OnKeyDown),
                         MSG_HANDLER(WM_SYSKEYDOWN, OnPtlSysKeyDown),
                         MSG_HANDLER(WM_SYSKEYUP, OnPtlSysKeyUp)])
    
class CoolBar(Rebar):
    def AddSimpleRebarBandCtrl(self, ctrl, nID = 0, title = NULL, bNewRow = FALSE,
                               cxWidth = 0, bFullWidthAlways = FALSE):

        hWndBand = ctrl.handle

        #Get number of buttons on the toolbar
        nBtnCount = SendMessage(hWndBand, TB_BUTTONCOUNT, 0, 0)

        #Set band info structure
        rbBand = REBARBANDINFO()
        rbBand.cbSize = sizeof(REBARBANDINFO)

        if WIN32_IE >= 0x0400:
            rbBand.fMask = RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_STYLE | RBBIM_ID | RBBIM_SIZE\
                           | RBBIM_IDEALSIZE
        else:
            rbBand.fMask = RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_STYLE | RBBIM_ID | RBBIM_SIZE

        if title != NULL:
            rbBand.fMask |= RBBIM_TEXT

        rbBand.fStyle = RBBS_CHILDEDGE

        if WIN32_IE >= 0x0500 and nBtnCount > 0:
            # add chevron style for toolbar with buttons
            #rbBand.fStyle |= RBBS_USECHEVRON
            #TODO find RBBS_USECHEVRON constant
            pass        

        if bNewRow:
            rbBand.fStyle |= RBBS_BREAK

        if title != NULL:
            rbBand.lpText = title
            
        rbBand.hwndChild = hWndBand
        
        if nID == 0: # calc band ID
            nID = ATL_IDW_BAND_FIRST + SendMessage(self.handle, RB_GETBANDCOUNT, 0, 0)

        rbBand.wID = nID

        rcTmp = RECT()
        if nBtnCount > 0:
            bRet = SendMessage(hWndBand, TB_GETITEMRECT, nBtnCount - 1, byref(rcTmp))
            if cxWidth != 0:
                rbBand.cx = cxWidth
            else:
                rbBand.cx = rcTmp.right
            rbBand.cyMinChild = rcTmp.bottom - rcTmp.top
            if bFullWidthAlways:
                rbBand.cxMinChild = rbBand.cx
            elif title == 0:
                SendMessage(hWndBand, TB_GETITEMRECT, 0, byref(rcTmp))
                rbBand.cxMinChild = rcTmp.right
            else:
                rbBand.cxMinChild = 0
        else: #	// no buttons, either not a toolbar or really has no buttons
            GetWindowRect(hWndBand, byref(rcTmp))
            if cxWidth != 0:
               rbBand.cx = cxWidth
            else:
                rbBand.cx = rcTmp.right - rcTmp.left

            if bFullWidthAlways:
                rbBand.cxMinChild = rbBand.cx
            else:
                rbBand.cxMinChild = 0
                
            rbBand.cyMinChild = rcTmp.bottom - rcTmp.top

        if WIN32_IE >= 0x0400:
            rbBand.cxIdeal = rbBand.cx;
            
        #Add the band
        SendMessage(self.handle, RB_INSERTBAND, -1, byref(rbBand))

        #if WIN32_IE >= 0x0501:
        #    exStyle = SendMessage(hWndBand, TB_GETEXTENDEDSTYLE, 0, 0)
        #    SendMessage(hWndBand, TB_SETEXTENDEDSTYLE, 0, dwExStyle | \
        #                TBSTYLE_EX_HIDECLIPPEDBUTTONS)
