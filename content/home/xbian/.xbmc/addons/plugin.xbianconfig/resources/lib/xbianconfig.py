import subprocess
import xbmc

import threading

xbmc.log('XBian-config : Initialise bash sessions',xbmc.LOGDEBUG)
process = subprocess.Popen(['/bin/bash'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
processlock = threading.Lock()

def sh_escape(s):
   return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")

def xbianConfig(*args,**kwargs) :        
        cmd = kwargs.get('cmd',['sudo','/usr/local/sbin/xbian-config'])        
        for arg in args :           
           cmd.append(sh_escape(arg))        
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
        xbmc.log('XBian-config : xbian-config %s : %s'%(' '.join(cmd[2:]),str(result)),xbmc.LOGDEBUG)        
        return result
        
