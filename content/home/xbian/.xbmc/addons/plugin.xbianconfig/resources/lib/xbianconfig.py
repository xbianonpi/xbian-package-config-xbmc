import subprocess
import xbmc

def sh_escape(s):
   return s.replace("(","\\(").replace(")","\\)").replace(" ","\\ ")

def xbianConfig(*args,**kwargs) :
        cmd = kwargs.get('cmd',['sudo','/usr/local/sbin/xbian-config'])
        for arg in args :
           print arg
           cmd.append(sh_escape(arg))
        rc= subprocess.check_output(cmd)
        rcs = rc.split('\n')
        result  = filter(lambda x: len(x)>0, rcs)
        xbmc.log('XBian : xbian-config %s : %s '%(' '.join(cmd[2:]),str(result)),xbmc.LOGDEBUG)
        return result
        

