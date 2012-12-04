import xbmc
import xbmcgui
import sys
from xbmcaddon import Addon

__addonID__      = "script.program.xbian"
 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString



def get_params():
  param=[]
  paramstring=sys.argv[1]
  print paramstring
  if len(paramstring)>=2:
    params=sys.argv[1]
    cleanedparams=params
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]
  return param
        
class API() : 
    def __init__(self):
        self.dialog = xbmcgui.Dialog()
        
    def kernel(self):
        self.dialog.ok(" My message title", " This is a nice message ")

    def normal(self) :
        rc = self.dialog.yesno("Back to Normal Mode", "Switch to normal Mode")
        if rc :
			xbmc.executebuiltin('Skin.Reset(advancedmode)')
        
    def advanced(self) :
        rc = self.dialog.yesno("Enter in Advanced Mode", "Warning : Enter in advanced mode\nmay be ask root password or can be simply deleted;")
        if rc :
			xbmc.executebuiltin('Skin.SetBool(advancedmode)')      
             
    

parameter = get_params()
mode=int(parameter["mode"])
api = API()

if mode == 1 :
    api.kernel()
elif mode == 2 :
    api.advanced()
elif mode == 3 :
    api.normal()
