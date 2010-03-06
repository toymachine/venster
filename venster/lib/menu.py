from venster.windows import *
from venster.wtl import *

def EvalItem(item, parent):
    if item[0] == MF_POPUP:
        popupMenu = PopupMenu(managed = False)
        for subItem in item[2]:
            EvalItem(subItem, popupMenu)
        parent.AppendMenu(MF_POPUP, popupMenu, item[1])
    elif item[0] == MF_STRING:
        if item[1][0] == "*":
            parent.AppendMenu(MF_STRING, item[2], item[1][1:])
            parent.SetMenuDefaultItem(item[2])
        else:
            parent.AppendMenu(MF_STRING, item[2], item[1])
    elif item[0] == MF_SEPARATOR:
        parent.AppendMenu(MF_SEPARATOR, 0, 0)
    
def EvalPopupMenu(item, managed = False):
    popupMenu = PopupMenu(managed = managed)
    for subItem in item:
        EvalItem(subItem, popupMenu)
    return popupMenu

def EvalMenu(item, managed = False):
    menu = Menu(managed = managed)
    for subItem in item:
        EvalItem(subItem, menu)
    return menu
