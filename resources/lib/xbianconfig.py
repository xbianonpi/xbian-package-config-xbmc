import subprocess
import xbmc

def xbianConfig(*args):
        cmd = ['sudo','/usr/local/sbin/xbian-config']
        cmd.extend(args)
        rc= subprocess.check_output(cmd)
        print rc
        rcs = rc.split('\n')
        result  = filter(lambda x: len(x)>0, rcs)
        xbmc.log('XBian : %s : %s '%(' '.join(cmd),str(result)),xbmc.LOGDEBUG)
        return result
        

