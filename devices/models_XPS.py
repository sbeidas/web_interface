import socket

class XPS():
    server = '172.16.0.254'
    port = 5001
    timeOut = 20
    receive_pending = False
    def __init__(self):   
        print 'XPS: connecting to Newport server ',self.server
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server,self.port))
            self.socket.settimeout(self.timeOut)
            self.socket.setblocking(1)
            self.pos_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.pos_socket.connect((self.server,self.port))
            self.pos_socket.settimeout(self.timeOut)
            self.pos_socket.setblocking(1)
        except:
            print 'Connection to XPS failed, check IP & Port'
        
    def close(self):
        try:
            self.socket.close()
            self.pos_socket.close()
        except socket.error:
            pass

    def ErrorStringGet (self, ErrorCode):
        command = 'ErrorStringGet(' + str(ErrorCode) + ',char *)'
        [error, returnedString] = self.__sendAndReceive(command)
        return [error, returnedString]
        
    def displayError (self,errorCode, APIName):
        # Display error function : simplify error print out
        if (errorCode != -2) and (errorCode != -108):
            [errorCode2, errorString] = self.ErrorStringGet(errorCode)
            if (errorCode2 != 0):
                print APIName + ' : ERROR ' + str(errorCode)
            else:
                print APIName + ' : ' + errorString
        else:
            if (errorCode == -2):
                print APIName + ' : TCP timeout'
            if (errorCode == -108):
                print APIName + \
                ' : The TCP/IP connection was closed by an administrator'
        return
    
    def _send(self, command, sock=None):
        try:
            if not sock:
                sock = self.socket
            sock.send(command)
        except socket.timeout:
            return [-2, '']
        except socket.error,(errNb, errString):
            print 'Socket error : ' + errString
            return [-2, '']
        return [0,'']
        
    def _receive(self, sock=None, buffersize=1024):
        try:
            if not sock:
                sock = self.socket
            ret = sock.recv(buffersize)
            while (ret.find(',EndOfAPI') == -1):
                ret += sock.recv(buffersize)                
        except socket.timeout:
            return [-2, '']
        except socket.error,(errNb, errString):
            print 'Socket error : ' + errString
            return [-2, '']
        for i in range(len(ret)):
            if (ret[i] == ','):
                return [int(ret[0:i]), ret[i+1:-9]]
    
    def __sendAndReceive(self,command, sock=None):
        ret = self._send(command,sock=sock)
        if ret != -2:
            ret = self._receive(sock=sock)
        return ret
    
    def do(self,command,function_name,wait=True,sock=None):
        if ((not sock) and (self.receive_pending)):
            self._receive(buffersize=4096)
            self.receive_pending = False
        if wait:
            [error, returnedString] = self.__sendAndReceive(command,sock=sock)
        else:
            [error, returnedString] = self._send(command,sock=sock)
            self.receive_pending = True
        if (error != 0):
            self.displayError(error,function_name)
        return returnedString

class RotationStage(XPS):
    def __init__ (self, group='',positioner='',min_angle=0,max_angle=360,offset=0.0):
        self.group = group
        self.positioner = self.group+'.'+positioner
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.offset = offset
        XPS.__init__(self)
        print 'XPS: Initializing ',self.group,self.positioner
        self.GroupKill()
        self.GroupInitialize()
        self.setVelocity(self.getMaxVelocity())
        print 'XPS: homing...'
        self.GroupHomeSearch()
        self.current_position = self.getPosition()
    
    def close(self):
       #self.moveTo(0.0)
       try:
           self.socket.close()
           self.pos_socket.close()
       except socket.error:
           pass
    
    def GroupKill(self):
        function_name = 'GroupKill'
        command = function_name +'(' + self.group + ')'
        return self.do(command,function_name)
        
    def GroupInitialize(self):
        function_name = 'GroupInitialize'
        command = function_name + '(' + self.group + ')'
        return self.do(command,function_name)
    
    def GroupHomeSearch(self):
        function_name = 'GroupHomeSearch'
        command = function_name+'(' + self.group + ')'
        return self.do(command,function_name)
    
    def moveTo(self,pos,wait=True):
        pos += self.offset
        if ((pos > self.max_angle) or (pos < self.min_angle)):
            print 'XPS: moveTo: target position out of bounds'
            return None
        function_name = 'GroupMoveAbsolute'
        command = function_name+'(' + self.group + ',' + \
                  '%.4f' %pos + ')'
        return self.do(command,function_name,wait=wait)

    def moveRel(self, pos, wait=True):
        function_name = 'GroupMoveRelative'
        command = function_name+'(' + self.group + ',' + \
                  '%.4f' %pos + ')'
        return self.do(command,function_name,wait=wait)
    
    def getPosition(self):
        function_name = 'GroupPositionCurrentGet'
        command = function_name+'(' + self.group + ',' + 'double *)'
        x = self.do(command,function_name,sock=self.pos_socket)
        self.current_position = eval(x)
        return self.current_position - self.offset
    
    def setVelocity(self, vel):
        v,a,j1,j2 = self.get_motion_parameters()
        return self.set_motion_parameters(vel,a,j1,j2)
    
    def getMaxVelocity(self):
        max_vel, max_acc = self.get_max_motion_parameters()
        return max_vel
    
    def getCurrentVelocity(self):
        function_name = 'GroupVelocityCurrentGet'
        command = function_name + '(' + self.group + ', double *)'
        returnedString = self.do(command,function_name,sock=self.pos_socket)
        i, j, retList = 0, 0, []
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))
        retVal = retList[0]
        return retVal
    
    def get_motion_parameters(self):
        function_name = 'PositionerSGammaParametersGet'
        command = function_name+'(' + self.positioner + ',double *,double *,double *, double *)'
        returnedString = self.do(command,function_name)
        i, j, retList = 0, 0, []
        for paramNb in range(4):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0
        vel, acc, min_jerk, max_jerk = retList
        return vel,acc,min_jerk,max_jerk
    
    def get_max_motion_parameters(self):
        function_name = 'PositionerMaximumVelocityAndAccelerationGet'
        command = function_name+'(' + self.positioner + ',double *,double *)'
        returnedString = self.do(command,function_name)
        i, j, retList = 0, 0, []
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0
        vel, acc = retList
        return vel,acc
    
    def set_motion_parameters(self,vel,acc,min_jerk,max_jerk):
        function_name = 'PositionerSGammaParametersSet'
        command = function_name+'(' + self.positioner + ',' + str(vel) + ',' + str(acc) + \
                  ',' + str(min_jerk) + ',' + str(max_jerk) + ')'
        return self.do(command,function_name)
    
    def isMoving(self):
        function_name = 'GroupStatusGet'
        command = function_name+'(' + self.group + ',int *)'
        returnedString = self.do(command,function_name,sock=self.pos_socket)
        i, j, retList = 0, 0, []
        while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
            j += 1
        retList.append(eval(returnedString[i:i+j]))
        retVal = retList[0]
        if retVal == 44:
            return True
    
class Sample(RotationStage):
    def __init__(self):
        #-45 degress is normal incidence -- range 35 - 45+70
        RotationStage.__init__(self,group='GROUP8',positioner='POSITIONER',
                               min_angle=-75, max_angle=35)
        self.offset = -45.0
    def angle_scan(self, angle_start, angle_stop, velocity):
        print 'In angle scan'
        self.angle_start = angle_start
        self.angle_stop = angle_stop
        self.moveTo(angle_start)
        self.setVelocity(velocity)
        self.moveTo(angle_stop, wait=False)
    def angle_scan_finished(self):
        if abs(self.getPosition()-self.angle_stop) < 1.0:
            self.setVelocity(self.getMaxVelocity())
            return True
        else:
            return False
        
class Grating(RotationStage):
    def __init__(self):
        RotationStage.__init__(self,group='GROUP8',positioner='POSITIONER',
                               min_angle=-50, max_angle=148)
        
class Polarization(RotationStage):
    max_velocity = 720.0
    max_acceleration = 500.0
    def __init__(self, offset=0.0):
        RotationStage.__init__(self,group='GROUP8',positioner='POSITIONER',
                               min_angle=0, max_angle=360, offset=offset)
    def spin(self, vel=max_velocity, acc=max_acceleration,wait=True):
        function_name = 'GroupSpinParametersSet'
        command = function_name + '(' + self.group + ',' + \
                  str(vel) + ',' + str(acc) + ')'
        return self.do(command,function_name,wait=wait)
        
    def stop(self, acc=max_acceleration):
        function_name = 'GroupSpinModeStop'
        command = function_name + '(' + self.group + ',' + \
                  str(acc) + ')'
        return self.do(command,function_name)
        
    def get_spin_parameters(self):
        function_name = 'GroupSpinCurrentGet'
        command = function_name+'(' + self.group + ',double *,double *)'
        returnedString = self.do(command,function_name)
        i, j, retList = 0, 0, []
        for paramNb in range(2):
            while ((i+j) < len(returnedString) and returnedString[i+j] != ','):
                j += 1
            retList.append(eval(returnedString[i:i+j]))
            i, j = i+j+1, 0
        vel, acc = retList
        return vel,acc
        
class Valve(XPS):
    def __init__(self, GPIOName = 'GPIO1.DO'):
        XPS.__init__(self)
        self.GPIOName = GPIOName
        self.state = 0
    def _setState(self,DigitalOutputValue):
        self.state = DigitalOutputValue
        Mask = '1'
        function_name = 'GPIODigitalSet'
        command = function_name+'(' + self.GPIOName + ',' + str(Mask) + ',' + \
                  str(DigitalOutputValue)+')'
        return self.do(command,function_name)
    def on(self):
        return self._setState(1)
    def off(self):
        return self._setState(0)
    def switch(self):
        if self.state == 0:
            return self._setState(1)
        elif self.state == 1:
            return self._setState(0)
    def test(self):
        print 'on',self.on()
        time.sleep(1)
        print 'off',self.off()
        time.sleep(1)
        print 'switch',self.switch()
        self.close()

if __name__ == '__main__':
    import time
    import numpy as np
    v = Valve()
    v.test()
    v.close()
    
    
    
    