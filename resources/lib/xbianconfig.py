import subprocess

def xbianConfig(*args):
        cmd = ['sudo','/usr/local/sbin/xbian-config']
        cmd.extend(args)
        rc= subprocess.check_output(cmd)
        print rc
        rcs = rc.split('\n')
        return filter(lambda x: len(x)>0, rcs)
        

