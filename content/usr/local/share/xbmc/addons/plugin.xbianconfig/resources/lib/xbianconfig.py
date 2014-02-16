import subprocess
import shelve
import hashlib
import json
try :
	import xbmc
	XBMC = True
except :
	XBMC = False

import threading

if XBMC :
	xbmc.log('XBian-config : Initialise bash sessions',xbmc.LOGDEBUG)

CACHEFILE = '/home/xbian/.xbmc/userdata/addon_data/plugin.xbianconfig/cache.db'

process = subprocess.Popen(['/bin/bash'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
processlock = threading.Lock()

cacheDB = shelve.open(CACHEFILE,'c',writeback=True)

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
        
