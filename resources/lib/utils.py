import xbmc,xbmcgui
from xbianconfig import xbianConfig
import time

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
    
def getText(header,default="",hidden=False):
    kb = xbmc.Keyboard(default,header,hidden)
    kb.doModal()
    if (kb.isConfirmed()):
        return kb.getText()
    else :
        return None

SSID = 0
SECURITYTYPE = 1
SECURITY = 2
SIGNAL = 3

def wifiConnect(interface):
    dialog = xbmcgui.Dialog()    
    progress = xbmcgui.DialogProgress()
    progress.create('Scanning','Scanning for wlan on %s'%interface)
    #progress.update(0) #should hide progress bar, don't work
    networklist = xbianConfig('network','scan',interface)
    networks = []
    for network in networklist :
        tmp = network.split(',')
        tmp[SSID] = tmp[SSID].replace('"','')
        networks.append(tmp)
        
    canceled = False
    
    while not canceled :
        if progress.iscanceled():
            canceled = True
        else :
            progress.close()
            displaylist = []
            for network in networks :
                name = '%s [COLOR blue](%s)[/COLOR]'%(network[SSID],network[SECURITYTYPE])
                displaylist.append(name)
            selectedNetwork = dialog.select('Select Network',displaylist)
            if selectedNetwork == -1 :
                canceled = True
            else :
                if networks[selectedNetwork][SECURITY] == 'on' :
                    key = getText('%s : Security Key'%networks[selectedNetwork][SSID])
                    if not key :
                        continue
                else :
                    key = ""
                        
                progress.create('Scanning','Connecting %s to %s'%(interface,networks[selectedNetwork][SSID]))
                rc = xbianConfig('network','credentials',interface,networks[selectedNetwork][SECURITYTYPE],networks[selectedNetwork][SSID],key)
                if rc and rc[0] == '1' :
                    rc = xbianConfig('network','restart',interface)
                    rc = '2'
                    while rc == '2' :
                        rc = xbianConfig('network','progress',interface)[0]
                        time.sleep(0.5)
                    if rc == '1' :
                        progress.close()
                        return True
                    else :
                        progress.close()
                        dialog.ok("Wireless",'%s : cannot connect to %s (%s)'%(interface,networks[selectedNetwork][SSID],rc))
                        
    return False
        
    
