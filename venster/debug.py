from venster.windows import *
from venster.wtl import *

class MsgFormatter:
    RMSGS = dict([(x, y) for (y, x) in MSGS]) #reverse msg dict for debugging

    def formatMouseMove(self, wParam, lParam):
        return "wParam: %d, lParam: %d, x: %d, y: %d" % ((wParam, lParam) + GET_XY_LPARAM(lParam))

    def formatDefault(self,blaat, wParam, lParam):
        return "wParam: %d, lParam: %d" % (wParam, lParam)
    
    formatters = {WM_MOUSEMOVE: formatMouseMove,
                  WM_LBUTTONDOWN: formatMouseMove}
    
    def format(self, nMsg, wParam, lParam):
        return "%s %s" % (self.RMSGS.get(nMsg, nMsg),
                          self.formatters.get(nMsg, self.formatDefault)(self, wParam, lParam))
                          
