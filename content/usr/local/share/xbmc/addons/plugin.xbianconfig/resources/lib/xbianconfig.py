import subprocess
import shelve
import hashlib
import json
import os

try :
	import xbmc
	XBMC = True
except :
	XBMC = False

import threading

if XBMC :
	xbmc.log('XBian-config : Initialise bash sessions',xbmc.LOGDEBUG)

CACHEDIR = '/home/xbian/.xbmc/userdata/addon_data/plugin.xbianconfig'
CACHEFILE = 'cache.db'

if not os.path.isdir(CACHEDIR) :
	os.makedirs(CACHEDIR)
	
cacheDB = shelve.open(os.path.join(CACHEDIR,CACHEFILE),'c',writeback=True)

process = subprocess.Popen(['/bin/bash'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
processlock = threading.Lock()



def sh_escape(s):
   return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")

def xbianConfig(*args,**kwargs) :        
        cmd = kwargs.get('cmd',['sudo','/usr/local/sbin/xbian-config'])
        cache = kwargs.get('cache',False)
        force_refresh = kwargs.get('forcerefresh',False)

        for arg in args :           
           cmd.append(sh_escape(arg))                                
        
        if cache or force_refresh :			
			key = hashlib.md5(json.dumps(cmd, sort_keys=True)).hexdigest()			
			if cacheDB.has_key(key) and not force_refresh :
				xbmc.log('XBian-config : xbian-config %s : return cached value : %s'%(' '.join(cmd[2:]),str(cacheDB[key])),xbmc.LOGDEBUG)						
				return cacheDB[key]
			        
        processlock.acquire()        
        process.stdin.write(' '.join(cmd) + ' ; echo EndCall\n')        
        rcs = []
        while True :			
			line = process.stdout.readline()[:-1]
			if line == 'EndCall':
				processlock.release()
				break
			rcs.append(line)
        result  = filter(lambda x: len(x)>0, rcs)        
        if cache or force_refresh:			
			cacheDB[key] = result
			cacheDB.sync()	
        if XBMC :
			xbmc.log('XBian-config : xbian-config %s : %s'%(' '.join(cmd[2:]),str(result)),xbmc.LOGDEBUG)        
        return result
        
