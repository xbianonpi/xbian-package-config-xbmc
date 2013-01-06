import xbmc,xbmcgui

def getNumeric(header,default=None,min=False,max=False):
    dialog = xbmcgui.Dialog() 
    cont = True
    while cont :
        rc = dialog.numeric(0,header,default)
        cont = False
        if min :
            if int(rc) < min :
                dialog.ok(header,'Value must be greater than %d'%min)
                cont = True
        if max :
            if int(rc) > max :
                dialog.ok(header,'Value must be lower than %d'%max)
                cont = True
    return rc

def getIp(header,default=None):
    dialog = xbmcgui.Dialog() 
    return dialog.numeric(3,header,default)
    
def getText(header,default=None):
    kb = xbmc.Keyboard(default,header)
    kb.doModal()
    if (kb.isConfirmed()):
        return kb.getText()
    else :
        return None
