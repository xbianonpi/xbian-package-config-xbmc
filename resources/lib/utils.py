import xbmc,xbmcgui
from xbianconfig import xbianConfig

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

def wifiConnect(interface,ssid,mode):
	dialog = xbmcgui.Dialog()
	networklist = xbianConfig('network','scan',interface)
	displaylist = []
	for ssid in networklist :
		ssiddetails = ssid.split(',')
		#check if hidden ssid
		if ssiddetails[0] == '' :
			name = 'hidden'
		else :
			name =  ssiddetails[0]
		
		#check security
		if ssiddetails[1] == 'on' :
			name += ' (%s)'%ssiddetails[2]
		displaylist.append(name)
	rc = dialog.select('Select Network',displaylist)
	cont = True
	if rc != -1 :
		selectSsid = networklist[rc].split(',') 
		#if hidden, ask ssid
		if selectSsid[0] == '' :
			name = getText('ssid')
			if not name :
				cont = False
		else :
			name =  selectSsid[0]
		
		#if not open, ask key :
		if selectSsid[1] == 'on' and cont :
			key = getText('Network Key')
			if not key :
				cont = False
			else :
				security = selectSsid[2]
		elif selectSsid[1] == 'off' :
			security = 'Open'
			key = ''
	else :
		cont = False	
		
	if cont :
		rc = xbianConfig('network','credentials',interface,security,name,key)
		if rc == '1' :
			return '%s (%s)'%(name,security) 
		
	
	return '%s (%s)'%(ssid,mode)
		
		
	
