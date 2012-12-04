import os,time,subprocess

#API mode
SET = 0
GET = 1


#BASH CONSTANT
class BASH():
    TRUE = "1"
    FALSE = "0"
    @classmethod
    def Bool(cls,value) :
        if value == cls.TRUE :
            return True
        else :
            return False

#XBMC CONSTANT
class XBMC():
    TRUE = "true"
    FALSE = "false"
    
    @classmethod
    def toBool(cls,value) :
        if value :
            return cls.TRUE
        else :
            return cls.FALSE


class API():
    def __init__(self,mode) :
        self.mode = mode
    
    def dispatch(self,funcname,data=None):
        service = getattr(self,funcname)
        return service(data)
    
    def subSetting(self,varname):
        var = getattr(self,varname)
        return var
    
    def xbianConfig(self,params):
        cmd = ['xbian-config']
        cmd.extend(params)
        print cmd
        rc= subprocess.check_output(cmd)
        
        if self.mode == SET :
            return BASH.Bool(rc)
        else :
            return rc
        
    
    def toXbmcBool(self,value) :
        if BASH.Bool(value) :
            return XBMC.TRUE
        else :
            return XBMC.FALSE
            
    def toXbmcInt(self,value) :
        return str(value)
                
    def resize(self,data):
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'resize',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            #must return have to resize (true/false)
            return "true"
        
        
    def overclock(self,data):
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overclock',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "3"
        
    
    def hostname(self,data):
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overclock',str(data))
        if self.mode == SET :
            rc = self.xbianConfig(['hostname','update',data['hostname']])
            return rc
        elif self.mode == GET :
            rc = self.xbianConfig(['hostname','select'])
            return rc
        
    def rootpassword(self,data):
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'rootpassword',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "******"
        
    
    def xbianpassword(self,data):
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'xbianpassword',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "******"
        
    def wlan(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'wlan',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            self.wadress = '192.168.1.5'
            self.wsubnet = '255.255.255.0'
            self.wgateway = '192.168.1.1'
            self.wdns1 = '8.8.8.8'
            self.wdns2 ='8.8.8.8'
            return "0"
        
    
    def lan(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'lan',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
            pass
        elif self.mode == GET :
            #call xbian-config
            self.adress = '192.168.1.5'
            self.subnet = '255.255.255.0'
            self.gateway = '192.168.1.1'
            self.dns1 = '8.8.8.8'
            self.dns2 ='8.8.8.8'
            return "0"
            
        
    
    def rootlogin(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'rootlogin',str(data))
        if self.mode == SET :
            if data['rootlogin'] == True :
                rc = self.xbianConfig(['sshroot','enable'])
            else :
                rc = self.xbianConfig(['sshroot','disable'])
            return rc
        elif self.mode == GET :
            rc = self.xbianConfig(['sshroot','status'])
            return XBMC.toBool(rc)
    
    
    def forcehdmi(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'forcehdmi',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "false"
        
    
    def ignorehdmi(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'ignorehdmi',str(data))
        if self.mode == SET :
            #simulate delay config
            #time.sleep(5)
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "false"
    
    def cecinit(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'cecinit',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "false"
    
    def cec(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'cec',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "false"
    
    def overscan(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'overscan',str(data))
        if self.mode == SET :
            #call xbian-config
            return True
        elif self.mode == GET :
            #call xbian-config
            return "false"
    
    def vc1(self,data) :
        print 'API - mode : %d - Called to %s with params : %s'%(self.mode,'vc1',str(data))
        if self.mode == SET :
            rc = self.xbianConfig(['licensevc1','update',data['vc1']])
            return rc
        elif self.mode == GET :
            rc = self.xbianConfig(['licensevc1','select'])
            return rc
    
    def mpeg2(self,data) :
        print 'API - self.mode : %d - Called to %s with params : %s'%(self.mode,'mpeg2',str(data))
        if self.mode == SET :
            rc = self.xbianConfig(['licensempg2','update',data['mpeg2']])
            return rc
        elif self.mode == GET :
            rc = self.xbianConfig(['licensempg2','select'])
            return rc
    
APIset = API(SET)
APIget = API(GET)
    
    
