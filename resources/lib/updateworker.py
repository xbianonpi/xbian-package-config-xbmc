import threading

class Updater(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event( )
        self.queue = queue
        
    def run(self):
        while not self._stopevent.isSet():
            functions = self.queue.get()
            ctrl = functions[0]
            rc = functions[1]()
            if functions[2] :
				functions[2](ctrl,rc)
            
    def stop(self):
        self._stopevent.set()
        self.queue.put([None,lambda : True == True,None])
         
