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
	progress = xbmcgui.DialogProgress()
	progress.create('Scanning','Scanning for wlan on %s'%interface)
	#progress.update(0) #should hide progress bar, don't work
	networklist = xbianConfig('network','scan',interface)
	if progress.iscanceled():
		cont = False
	else :
		progress.close()
		displaylist = []
		for ssid in networklist :
			ssiddetails = ssid.split(',')
			name =  ssiddetails[0]			
			#check security
			if ssiddetails[1] == 'on' :
				name += ' (%s)'%ssiddetails[2]
			displaylist.append(name)
		rc = dialog.select('Select Network',displaylist)
		cont = True
		if rc != -1 :
			selectSsid = networklist[rc].split(',') 
			print 'selected',selectSsid
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
		print interface,security,name,key
		rc = xbianConfig('network','credentials',interface,security,name,key)
		if rc and rc[0] == '1' :
			rc = xbianConfig('network','restart',interface)
			rc = 2
			while  rc == '2' :
				rc = xbianConfig('network','progress',interface)[0]
				xbmc.sleep(0.5)
			if rc == '1':
				return '%s (%s)'%(name,security) 
			else :
				dialog.ok("wifi",'Cant connect')
			
	
	return '%s (%s)'%(ssid,mode)
		
		
	
