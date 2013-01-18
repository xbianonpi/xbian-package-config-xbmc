#!/usr/bin/env python
from xbianconfig import xbianConfig
import os,sys

version = sys.argv[1]

lockfile = '/var/lock/XBianUpdating'
resultFile = '/tmp/resultCode'

#create the update status file
open(lockfile,'w').close()
rc = xbianConfig('updates','update',version)

update = open(resultFile,'w')
update.writelines(rc)
update.close()
os.remove(lockfile)

