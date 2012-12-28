import subprocess

def xbianConfig(*args):
        cmd = ['sudo','/usr/local/sbin/xbian-config']
        cmd.extend(args)
        rc= subprocess.check_output(cmd)
        rcs = rc.split('\n')
        print rcs
        return filter(lambda x: len(x)>0, rcs)
        

