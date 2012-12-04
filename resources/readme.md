##Note for Developper :
========================

###Add a category in xbian_addon :
add an xml file with all control in category directory.
./resources/category/

###Add a Control to a category :
there are 2 types of control
  
* **static** :
it never change, only his value can be updated
all settings from xbmc settings can be use.
more info : http://wiki.xbmc.org/index.php?title=Addon_Settings
     for action control :
        scipt to execute is in action.py
        param to script : mode=funcname

  * **dynamic** :
    this is complex control that have to be made on runtime
    it's a group of static controls.
    for that, choose a *type* for setting that is not a xbmc one
    ex :
    <setting label="test" type="xbianpackage"   id="xbianpackagelist" ... />
    when creating the window, when parsing this line a function with
    same name as type will be call.
    This function must be defined in controls.py in ./resources/libs/
    and return a xml list of controls.
    
  These controls can be a main setting, or a sublevel setting
  ex : *Fixed Ip* requires 5 parameters but it is only one setting
     
  --main setting :
    The first char of the id of setting is not a digit
    If the parameter is modified, a called is done to the API
    a function with same name than settingid is called 
    This function must be defined in xbianconfigAPI.py in ./resources/libs/
    it's the real call to bash xbian-config
    
  --subelevel setting
    The first char of the id of setting is a digit
    if one of this sublevel setting is modified, a call is do in previous main settings,
    with all sublevel value as parameters
    
    ex :
    
    <setting label="LAN" type="enum" id="lan"  lvalues="DHCP|FIXED" default="0" />
      <setting label="IP Adress" type="ipaddress" id="1adress"/>
      <setting label="Subnet Mask" type="ipaddress" id="1subnet"/>
      <setting label="Gateway" type="ipaddress" id="1gateway"/>
    if one of these setting is modified, a call is done to lan()
    with {'gateway':xxx,'subnet':XXX,'adress':xxx,'lan':0}
    
  
  
  TO DO :
   special control create on runtime.
      for some setting, it must be done on runtime, for this
   
