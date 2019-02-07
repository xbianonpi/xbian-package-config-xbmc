import subprocess
import shelve
import hashlib
import json
import os
import xbmc


bashThread = None
#print 'XBian-config running bashWorker'
import threading
#import psutil
#bashThread = bashWorker()
#bashThread.start()


def sh_escape(s):
    return s.replace("(", "\\(").replace(")", "\\)").replace(" ", "\\ ")


class bashWorker(threading.Thread):

    def __init__(self, ticks=6):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event()
        self.runtime = ticks
        self.timer = self.runtime
        self.bashRunning = False
        ###self.processlock = threading.Lock()
        print 'XBian-config : bashWorker started'

    def kill(self):
        if self.bashRunning:
            #pp = psutil.Process(self.process.pid)
            #for pc in pp.children(recursive=True):
            #    pc.kill()
            #pp.kill()
            self.bashRunning = False

    def run(self):
        while not self._stopevent.isSet():
            while self.timer > 0:
                xbmc.sleep(2500)
                self.timer = self.timer - 1
                if self.bashRunning:
                    print 'XBian-config : bashWorker tick %s' % self.timer
            self.kill()
            self.timer = 34560
            print 'XBian-config : bashWorker idle'
        print 'XBian-config : bashWorker terminate'
        self.kill()

    def stop(self):
        self.timer = 0
        self._stopevent.set()

    def execute(self, command):
        print 'XBian-config : write %s' % command
        self.timer = 240
        if not self.bashRunning:
            self.process = subprocess.Popen(['/bin/bash'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            self.bashRunning = True
        ###self.processlock = threading.Lock()
        ###self.processlock.acquire()
        self.process.stdin.write(command)

        print 'XBian-config : read start'
        rcs = []
        while True:
            line = self.process.stdout.readline()[:-1]
            #print 'XBian-config : read %s.' % line
            if line == 'EndCall' or line == '':
                if line == '':
                    print 'XBian-config : bashWorker: empty line received'
                ###self.processlock.release()
                self.kill()
                #print 'XBian-config : set timer %s' % self.runtime
                self.timer = self.runtime
                #print 'XBian-config : read end'
                return rcs
            rcs.append(line)


def xbianConfig(*args, **kwargs):
    global bashThread

    if not args:
        if bashThread and bashThread.isAlive():
            bashThread.stop()
        return

    cmd = kwargs.get('cmd', ['sudo', '/usr/local/sbin/xbian-config'])
    cache = kwargs.get('cache', False)
    force_refresh = kwargs.get('forcerefresh', False)
    force_clean = kwargs.get('forceclean', False)

    CACHEDIR = '/home/xbian/.kodi/userdata/addon_data/plugin.xbianconfig'
    CACHEFILE = 'cache.db'

    if not os.path.isdir(CACHEDIR):
        try:
            os.makedirs(CACHEDIR)
        except:
            exit(0)

    if force_clean:
        os.remove(os.path.join(CACHEDIR, CACHEFILE))

    cacheDB = shelve.open(os.path.join(CACHEDIR, CACHEFILE), 'c', writeback=True)

    for arg in args:
        cmd.append(sh_escape(arg))

    if cache or force_refresh:
        key = hashlib.md5(json.dumps(cmd, sort_keys=True)).hexdigest()
        if key in cacheDB and not force_refresh:
            xbmc.log('XBian-config : xbian-config %s : return cached value : %s' %
                     (' '.join(cmd[2:]), str(cacheDB[key])), xbmc.LOGDEBUG)
            return cacheDB[key]

    if bashThread:
        rcs = bashThread.execute(' '.join(cmd) + '; echo EndCall\n')
    else:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        rcs = []
        while True:
            line = process.stdout.readline()[:-1]
            if line == '':
                break
            rcs.append(line)
        process.wait()

    result = filter(lambda x: len(x) > 0, rcs)
    if cache or force_refresh:
        cacheDB[key] = result
        cacheDB.sync()
    xbmc.log('XBian-config : xbian-config %s : %s' % (' '.join(cmd[2:]), str(result)), xbmc.LOGDEBUG)
    if not bashThread:
        process.wait()
    return result
