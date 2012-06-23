#!/usr/bin/env python
import time
import serial
import logging
from collections import defaultdict

''' begin constants '''
LF = chr(int('0A',16)) # line feed
CR = chr(int('0D',16)) # carriage return
ACK = chr(int('6',16)) # ACK
''' end constants '''

logger = logging.getLogger(__name__)

class GSIOC():
    max_retries = 10
    max_receive_string_size = 100
    max_null_count = 5
    
    def __init__(self, ser=None,com_port=1):
        if ser:
            self.ser = ser
        else:
            self.ser = serial.Serial(com_port-1, 19200, \
                                     parity=serial.PARITY_EVEN, \
                                     timeout=1)
        if self.ser:
            logger.info('serial connection established')
        else:
            logger.error('serial connection error')
        self.registered_devices = []        
        self.connected_device = None
        
    def close(self):
        self.ser.close()
        
    def send(self,x):
        return self.ser.write(x)

    def get_byte(self):
        return self.ser.read(1)

    def disconnect(self):
        self.send(chr(255))
        time.sleep(0.03) # devices have up to 30ms to disconnect

    def connect(self,device_id):
        if device_id not in self.registered_devices:
            logger.error('connect error, device not found')
            return False
        device_id_byte = chr(device_id+128) # formula for device id
        self.send(device_id_byte) 
        retval = self.get_byte()
        if retval != device_id_byte:
            logger.warning('connecting to %d, returned: %s' \
                           %(device_id, str(retval)))
            return False
        self.connected_device = device_id
        time.sleep(.02) # time for device to connect
        return True
    
    def establish_connection(self,device_id):
        for i in range(self.max_retries):            
            self.disconnect()
            if self.connect(device_id):
                return True
        return False
       
    def check_connection(self,device_id):
        if self.connected_device != device_id:
            if not self.establish_connection(device_id):
                logger.error('could not establish connection to %d' %device_id)
                return False
        return True
    
    def register_device(self,name,device_id):
        self.registered_devices.append(device_id)
        if self.establish_connection(device_id):
            logger.info('registered %s, device id: %d' \
                    %(name,device_id))
            return True
        logger.error('could not register %s, device id: %d'\
                     %(name,device_id))
        self.registered_devices.remove(device_id)
    
    def immediate(self,cmd):
        done = False
        count = 0
        null_count = 0
        retStr = ''
        self.send(cmd)
        while not done:
            if count > self.max_receive_string_size:
                logger.warning('max string size limit for cmd: %s' %cmd)
                break
            if null_count > self.max_null_count:
                logger.debug('max null count for cmd: %s' %cmd)
                retStr = ''
                break
            if count > 0:
                self.send(ACK)
            retval = self.get_byte()
            if retval != '':
                ordval = ord(retval)
                if (ordval >> 7) == 1:  # end of return string set high bit
                    retval = chr(ordval-128)
                    done = True
            else:
                logger.debug('cmd: %s, null retval' %cmd)
                null_count += 1
            retStr += retval
            count += 1
        return retStr

    def buffered(self, cmd):
        full_cmd = LF+cmd+CR
        for x in full_cmd:
            self.send(x)
            retval = self.get_byte()
            if retval != x:
                logger.debug('cmd: %s, expected: %c, received: %c' \
                               %(cmd,x,retval))
                return False
        return True
                
    def do_cmd(self,device_id,cmd_type,cmd):
        if not self.check_connection(device_id):
            return False
        for i in range(self.max_retries):
            if cmd_type == 'immediate':            
                retStr = self.immediate(cmd)
                if  ((retStr != '') and ('#' not in retStr)):
                    return retStr
                else:
                    logger.debug('cmd: %s, returned %s' %(cmd,retStr))
            elif cmd_type == 'buffered':
                if self.buffered(cmd):
                   return True
            time.sleep(.05)       
            self.establish_connection(device_id)
        logger.warning('%s command: %s to device %d failed' \
                       %(cmd_type,cmd,device_id))
        return False
               
class Device():
    def __init__(self,gsioc,device_id):
        self.gsioc = gsioc
        self.device_id = device_id
        self.name = self.__class__.__name__+'_'+str(self.device_id)
        self.gsioc.register_device(self.name,self.device_id)
    
    def immediate(self,cmd):
        return self.gsioc.do_cmd(self.device_id,'immediate',cmd)
    
    def buffered(self,cmd):
        return self.gsioc.do_cmd(self.device_id,'buffered',cmd)
    
    def master_reset(self):
        '''resets machine to powered up state '''
        if self.immediate('$') == '$':
            logger.debug('master reset successful')
            return True
        else:
            logger.warning('master reset unsuccessful')
            return False
        
    def request_module_identification(self):
        '''identifies the selected slave device'''
        retStr = self.immediate('%')
        if retStr:
            logger.debug('module identification: %s' %retStr)
            return retStr
        else:
            logger.warning('module identification failed')
            return False

class Value_Range():
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val
    
    def fix(self,val):
        if val < self.min_val:
            val = self.min_val
        elif val > self.max_val:
            val = self.max_val
        return val
    
    def check(self, val):
        if ((val < self.min_val) or (val > self.max_val)):
            return False
        else:
            return True

class Probe():
    def __init__(self, name, probe_type):
        self.name = name
        self.z_offset = 0.0 ## is this useful?
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.speed = 0.0
        self.type = probe_type
        self.has_tip = False
        
    def update_coords(self,x,y,z):
        if x:
            self.x = x
        if y:
            self.y = y
        if z:
            self.z = z
    
    def tip_loaded(self):
        self.has_tip = True
        self.z_offset = 44.0 #42.9
    
    def tip_unloaded(self):
        self.has_tip = False
        self.z_offset = 0.0
  
class Quad_Z_215(Device):
    error_messages = { 0: 'No error',\
                      15: 'NV-RAM checksum is invalid',\
                      16: 'X scale factor is invalid',\
                      17: 'Y scale factor is invalid',\
                      20: 'X motor position error',\
                      21: 'Y motor position error',\
                      22: 'Z motor position error',\
                      24: 'X target less than minimum X',\
                      25: 'X target more than maximum X',\
                      26: 'Y target less than minimum Y',\
                      27: 'Y target more than maximum Y',\
                      28: 'Z target less than minimum Z',\
                      29: 'Z target more than maximum Z',\
                      30: 'X encoder inactive',\
                      31: 'Y encoder inactive',\
                      32: 'Z position sensor inactive',\
                      33: 'Safety contact activated',\
                      34: 'X home phase is invalid',\
                      35: 'Y home phase is invalid',\
                      36: 'X and Y home phases are invalid',\
                      39: 'Stop button has been pressed',\
                      41: 'GSIOC communication error',\
                      42: 'Undefined GSIOC command',\
                      43: 'GSIOC command sequence incorrect',\
                      44: 'Cannot send commands, unit busy',\
                      55: 'Probe A motor position error',\
                      56: 'Probe B motor position error',\
                      57: 'Probe C motor position error',\
                      58: 'Probe D motor position error',\
                      59: 'Pitch motor position error'}
    xyz_extents = {'x': Value_Range(3.3,593.6),
                   'y': Value_Range(0.7,330.8),
                   'z': Value_Range(7.0,190.0)}
    width_extent = Value_Range(9.0,18.0)
    max_speed = 125000 # um/sec
    
    def __init__(self,gsioc,device_id,probe_types):
        Device.__init__(self, gsioc, device_id)
        self.motor_status = {'x': '', 'y': '', 'a': '', 'b': '', 'c': '', \
                             'd': '', 'w': 0.0}    
        self.update_motor_status()
        self.probe_names = ['A','B','C','D']
        self.probe_types = probe_types
        self.probes = []
        for i in range(4):
            self.probes.append(Probe(self.probe_names[i],self.probe_types[i]))
        for i in range(4):
            if self.probes[i].type == 'injection':
                self.probes[i].z_offset = -4.0
        try:
            self.update_probe_coordinates()
        except:
            self.home()
            self.update_probe_coordinates()
        self.probe_width = 0.0
        
    def read_home_phases_XY(self):
        '''
        reads home phases for X and Y motors. Returns "xxx/yyy"
        where: xxx - X motor phase; yyy - Y motor phase
        NOTE: I don't know what these numbers mean!
        '''
        retStr = self.immediate('A')
        if retStr:
            phase_x, phase_y = retStr.split('/')
            logger.debug('home phases X: %s, Y: %s' %(phase_x, phase_y))
            return phase_x,phase_y
        else:
            logger.warning('failed to read home phases of XY motors')
            return False
    
    def beep(self,f=2400,d=1):
        ''' causes 215 to beep. f=Hz, d=duration in tenths of seconds.'''
        if self.buffered('B'+str(f)+','+str(d)):
            logger.debug('beeped at %d Hz for %.1f sec' %(f,d/10.0))
            return True
        else:
            logger.warning('failed to beep')
            return False
        
    def current_error_code(self):
        '''
        reads the current error number. returns "nnn" which
        identifies the error number. If no error has occurred, returns 0
        '''
        retStr = self.immediate('e')
        if retStr:
            error_code = int(retStr)
            logger.debug('current error code = %d: %s' \
                         %(error_code,self.error_messages[error_code]))
            return error_code
        else:
            logger.warning('failed to retrieve current error code')
            return -1
        
    def set_motor_status(self, x,y,z):
        '''sets X,Y,Z motor status: 0 = disable, 1 = enable'''
        if self.buffered('E%d%d%d' %(x,y,z)):
            logger.debug('set XYZ motor status to %d%d%d' %(x,y,z))
            return True
        else:
            logger.warning('failed to set XYZ motor status')
            return False

    def relax_probes(self, n):
        '''relaxes the probe n = a,b,c, or d'''
        # what does this mean?
        if self.buffered('F'+n):
            logger.debug('relaxed probe %s' %n)
            return True
        else:
            logger.warning('failed to relax probe')
            return False
    
    def read_motor_status(self):
        '''
        read X,Y,Z motor status and width of probes. returns "xyabcdw":
        x = X motor; y = Y motor; a,b,c,d = Z motor on probes A,B,C,D;
        w = pitch. For each status: U = unpowered, P = powered, R = running,
        E = error.
        '''
        retStr = self.immediate('m')
        if retStr:
            logger.debug('read motor status %s' %retStr)
            return retStr
        else:
            logger.warning('failed to read motor status')
            return False

    def read_X_positions(self):
        '''reads probe X positions in integral units of 0.1mm '''
        retStr = self.immediate('X')
        if retStr:
            a,b,c,d = tuple([float(x)/10.0 for x in retStr.split(',')])        
            logger.debug('read X positions %.1f,%.1f,%.1f,%.1f' \
                         %(a,b,c,d))
            return a,b,c,d
        else:
            logger.warning('failed to read X positions')
            return False
    
    def read_Y_position(self):
        '''reads probes Y position in integral units of 0.1mm '''
        retStr = self.immediate('Y')
        if retStr:    
            y = float(retStr)/10.0
            logger.debug('read Y position %.1f' %y)
            return y
        else:
            logger.warning('failed to read y position')
            return False
        
    def read_Z_positions(self):
        '''reads probe Z positions in integral units of 0.1mm '''
        retStr = self.immediate('Z')
        if retStr:
            a,b,c,d = tuple([float(x)/10.0 for x in retStr.split(',')])        
            logger.debug('read Z positions %.1f,%.1f,%.1f,%.1f' \
                         %(a,b,c,d))
            return a,b,c,d
        else:
            logger.warning('failed to read Z positions')
            return False
    
    def read_probe_width(self):
        ''' reads probe width in integral until of 0.1mm '''
        retStr = self.immediate('w')
        if retStr:
            width = float(retStr)/10.0
            logger.debug('read probe width: %.1f' %width)
            return width
        else:
            logger.warning('failed reading probe width')
            return False
    
    def set_probe_width(self,width):
        width = self.width_extent.fix(width)
        int_width = int(width*10.0)
        self.move_cmd('w%d' %int_width)
        self.update_probe_width()
        self.update_probe_coordinates()
        #time.sleep(1)
        
    def read_probe_speed(self):
        ''' [a,b,c,d] in um/s'''
        retStr = self.immediate('O')
        if retStr:
            probe_speeds = map(int,retStr.split(','))
            logger.debug('read probe speeds: %s' %str(probe_speeds))
            return probe_speeds
        else:
            logger.warning('failed reading probe speeds')
            return False
        
    def set_probe_speed(self,velocities):
        ''' [a,b,c,d] in um/s'''
        cmd = 'O'+','.join(map(str,velocities))
        if self.buffered(cmd):
            logger.debug('set probe speeds: %s' %str(velocities))
        #time.sleep(1)
        
    def wait_until_not_moving(self, timeout=30.0,motion_polling_delay=0.2):
        t0 = time.time()
        moving = True
        while moving:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting until not moving')
                break
            self.update_motor_status()
            if 'R' not in self.motor_status.values():
                moving = False
            time.sleep(motion_polling_delay)
    
    def move_cmd(self,cmd):
        if self.buffered(cmd):
            self.wait_until_not_moving()
            return True
        else:
            logger.warning('failed to move: %s' %cmd)
            return False
            
    def home(self):
        '''moves XYZ to home position, homes all four Z-drives, and
           sets the X-pitch to 18mm'''
        if self.move_cmd('H'):
            logger.debug('homing command successful')
            return True
        else:
            logger.warning('failed to home')
            return False
            
    def move_xy(self,who,x,y,one_axis=True):
        '''
        combination of Xa, Xb, Xc, Xd commands to move probe to
        target x and y coordinates.
        '''
        x = self.xyz_extents['x'].fix(x)
        y = self.xyz_extents['y'].fix(y)
        int_x = int(x*10.0)
        int_y = int(y*10.0)
        if one_axis:
            int_current_y = int(self.probes[who].y*10.0)
            self.move_cmd('X%s%d/%d' %(self.probe_names[who].lower(),\
                                       int_x,int_current_y))
            self.move_cmd('X%s%d/%d' %(self.probe_names[who].lower(),\
                                       int_x,int_y))
        else:
            self.move_cmd('X%s%d/%d' %(self.probe_names[who].lower(),\
                                       int_x,int_y))
        
    def move_z(self,who,z):
        '''
        sets new Z-position. "Zsp" where s = selected probe(s),
        p = new position in integral units of 0.1mm. if s is not specified,
        the default is abcd.
        '''
        z = self.xyz_extents['z'].fix(z)
        int_z = int(z*10.0)
        self.move_cmd('Z%s%d' %(self.probe_names[who].lower(),int_z))
    
    def set_Z_heights(self, z_heights):
        '''
        sets Z-heights for all 4 probes, then moves to those heights at
        set probe speed. z_heights = [float]*4. If z = 0, then don't change.
        '''
        heights = []
        for z in z_heights:
            if z > 0.0:
                heights.append(self.xyz_extents['z'].fix(z))
            else:
                heights.append(0.0)
        h_str = [str(int(height*10.0)) for height in heights]
        for i,h in enumerate(h_str):
            if h == '0':
                h_str[i] = ''
        cmd = 'T'+','.join(h_str)
        if self.buffered(cmd):
            logger.debug('set Z heights: %s' %h_str)
            self.move_cmd('M')

    def update_motor_status(self):
        status = self.read_motor_status()
        if status:
            self.motor_status['x'] = status[0]
            self.motor_status['y'] = status[1]
            self.motor_status['a'] = status[2]
            self.motor_status['b'] = status[3]
            self.motor_status['c'] = status[4]
            self.motor_status['d'] = status[5]
            self.motor_status['w'] = status[6]

    def update_probe_coordinates(self):
        x_vals = self.read_X_positions()
        y_val = self.read_Y_position()
        z_vals = self.read_Z_positions()
        if (x_vals and y_val and z_vals):
            for i,probe in enumerate(self.probes):
                probe.update_coords(x_vals[i],y_val,z_vals[i])
        
    def update_probe_speeds(self):
        probe_speeds = self.read_probe_speed()
        if probe_speeds:
            for i,probe in enumerate(self.probes):
                probe.speed = probe_speeds[i]
    
    def update_probe_width(self):
        self.probe_width = self.read_probe_width()
        
class Probes():
    def __init__(self,arm):
        self.arm = arm
        self.probe_names = self.arm.probe_names
        self.probes = self.arm.probes
        
    def __getitem__(self, key):
        return self.probes[key]
                            
    def set_speed(self, speed_list):
        ''' sets probe speeds [vA,vB,vC,vD]. if 0, then unchanged '''
        velocities = []
        for i,probe in enumerate(self.probes):
            if speed_list[i] == 0:
                velocities.append(probe.speed)
            else:
                velocities.append(speed_list[i])
        self.arm.set_probe_speed(velocities)
        self.arm.update_probe_speeds()
        
    def move_xy(self,xy_list=[],mask=[],xy=(),one_axis=True):
        '''
        xy_list = [0,0,(x,y),0] - first tuple encountered is used
        or if mask and xy - first 1 in mask is chosen with xy
        '''
        if xy_list:        
            i,x,y = tuple([(i,)+xy for i,xy in enumerate(xy_list) if xy > 0][0])
            self.arm.move_xy(i,x,y,one_axis)
        elif mask and xy:
            self.arm.move_xy(mask.index(1),xy[0],xy[1],one_axis)
        self.arm.update_probe_coordinates()
    
    def move_z(self,z_list=[],mask=[],z=0,speed=0):
        '''
        z_list = [A,B,C,D]. A can be either a float or 0. If 0, not moved.
        if mask and z - z is applied to mask
        if speed is not defined, previous values are used
        if speed = max, max speed is applied to all moving probes
        if speed is a list - [vA,vB,vC,vD] velocities of each probe
        '''
        if ((mask and z) and (not z_list)):
            z_list = []        
            for i in mask:
                if i == 1:            
                    z_list.append(z)
                elif i == 0:
                    z_list.append(0)
        if isinstance(speed,list):
            self.set_speed(speed)
        else:
            if speed == 'max':
                speed = self.arm.max_speed
            speed_list = []
            for i,z in enumerate(z_list):
                if z == 0:
                    speed_list.append(self.probes[i].speed)
                else:
                    speed_list.append(speed)
            self.set_speed(speed_list)
        self.arm.set_Z_heights(z_list)
        self.arm.update_probe_coordinates()
        
    def load_tips(self, probe_mask, box=1, row=1, col=1,tip_size=1000):
        '''
        assume rack 234 is in position 2 loaded with 1-2 boxes of 200uL tips
        probe_mask = [1,1,1,1]  = A,B,C,D
        '''
        if(tip_size==1000): #meassure in microL
            x = 144.0 # for rack position 2
            z_retain, z_near, z_load = 168.0,105.0,97.0 #changed z_load from 85.0 (z_load=97 and z_retain=170 for 200microL) z)(z_load=72and z_retain=160  for 200microL)
            
            if box == 1:
                y = 64.0
            elif box == 2:
                y = 209.0
        else:
            x = 143.0 # for rack position 2
            z_retain, z_near, z_load = 160.0,80.0,62.0 #changed z_load from 85.0 (z_load=97 and z_retain=170 for 200microL) z)(z_load=72and z_retain=160  for 200microL)   
            if box == 1:
                y = 63.0
            elif box == 2:
                y = 208.5
                
           
        spacing = 9 # mm
        
     
        x = x + (9*(col-1))
        y = y + (9*(row-1))
        #self.move_z([z_retain]*4, speed='max')
        self.move_z(mask=probe_mask,z=z_retain  , speed=5000)
        self.arm.set_probe_width(spacing)
        self.move_xy(mask=probe_mask,xy=(x,y))
        self.move_z(mask=probe_mask,z=z_near,speed='max')
        self.move_z(mask=probe_mask,z=z_load,speed=5000)
        self.move_z(mask=probe_mask,z=z_near,speed=5000)
        self.move_z(mask=probe_mask,z=z_retain,speed='max')
        for i,probe in enumerate(self.probes):
            if probe_mask[i]:
                probe.tip_loaded()
        
    def eject_tips(self,probe_mask):
        ''' ejects to chute '''
        z_retain, z_eject = 160.0, 175.0
        spacing = 9
        self.move_z([z_retain]*4,speed='max')
        self.arm.set_probe_width(spacing)
        x,y = (607.0,301.1)
        self.move_xy([(x,y),0,0,0])
        self.move_z(mask=probe_mask,z=z_eject,speed='max')
        for i,probe in enumerate(self.probes):
            if probe_mask[i]:
                probe.tip_unloaded()
        
class Injection_Module_819(Device):
    error_messages = {  0: 'No error', \
                       10: 'No valve installed', \
                       12: 'Load position detection error', \
                       13: 'Inject position detection error' }
    
    def __init__(self,gsioc,device_id):
        Device.__init__(self, gsioc, device_id)        
        self.get_valve_status()
        
    def get_error(self):
        '''
        reads the current error number. returns "nnn" which
        identifies the error number. If no error has occurred, returns 0
        '''
        retStr = self.immediate('E')
        if retStr:
            error_code = int(retStr)
            logger.debug('current error code = %d: %s' \
                         %(error_code,self.error_messages[error_code]))
            return error_code
        else:
            logger.warning('failed to retrieve current error code')
            return -1

    def get_valve_status(self):
        ''' reads valve status '''
        retStr = self.immediate('V')
        if retStr:
            self.valve_status = retStr
            logger.debug('valve status: %s' %self.valve_status)
            return self.valve_status
        else:
            logger.warning('failed to read valve status')
            return False
        
    def total_valve_turns(self):
        ''' reads total number of valve turns'''
        retStr = self.immediate('M')
        if retStr:
            turns = int(retStr)
            logger.debug('total valve turns: %d' %turns)
            return turns
        else:
            logger.warning('failed to read total valve turns')
        return False
    
    def valve_switching_time(self):
        ''' reads valve switching time in milliseconds'''
        retStr = self.immediate('T')
        if retStr:
            switching_time = int(retStr.split()[0])
            logger.debug('valve switching time = %d ms' %switching_time)
            return switching_time
        else:
            logger.warning('failed to read valve switching time')
        return False
    
    def wait_until_not_moving(self, timeout=30.0,motion_polling_delay=0.5):
        t0 = time.time()
        moving = True
        while moving:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting until not moving')
                break
            self.get_valve_status()
            if self.valve_status != 'M':
                moving = False
            time.sleep(motion_polling_delay)
    
    def valve_inject(self):
        ''' set valve to inject '''
        if self.buffered('VI'):
            logger.debug('set valve to inject')
            self.wait_until_not_moving()
            return True
        else:
            logger.error('failed to set valve to inject')
            return False
            
    def valve_load(self):
        ''' set valve to load '''
        if self.buffered('VL'):
            logger.debug('valve set to load')
            self.wait_until_not_moving()
            return True
        else:
            logger.error('failed to set valve to load')
            return False

class ValveMate(Device):
    '''
    Gilson Valvemate with 8-port Hamilton valve
    Documentation suggests spacing commands by at least 1.8 seconds.
    '''
    error_messages = {0: 'No Error',\
                      10: 'NV-RAM checksum not matched',\
                      11: 'Missing motor step',\
                      12: 'Home position detection error',\
                      14: 'Illegal position command'}
    letter_map = dict(zip('ABCDEFGH',range(1,9,1)))
    
    def __init__(self, gsioc, device_id):
        Device.__init__(self, gsioc, device_id)
        self.get_valve_status()
        
    def get_error(self):
        ''' return error code '''
        retStr = self.immediate('E')
        if retStr:
            error_code = int(retStr)
            logger.debug('current error code = %d: %s' \
                         %(error_code,self.error_messages[error_code]))
            return error_code
        else:
            logger.warning('failed to retrieve current error code')
            return -1
    
    def home(self):
        if self.buffered('H'):
            logger.debug('moving valve to home position')
    
    def change_position(self,pos):
        if self.position == pos:
            logger.debug('valve already in position %d' %pos)
            return True
        if pos not in range(1,9,1):
            logger.error('invalid position')
            return False
        if self.buffered('%d' %pos):
            logger.debug('valve set to position %d' %pos)
            self.position = pos
            return True
        else:
            logger.error('failed to set valve position')
            return False
    
    def get_valve_status(self):
        retStr = self.immediate('P')
        if retStr:
            self.status = retStr[0]
            self.position = int(self.letter_map[retStr[1]])
            logger.debug('valve status: %s, position: %d'\
                         %(self.status,self.position))
            return self.status,self.position
        else:
            logger.warning('failed to retrieve valve status and position')
            return False
    

class Syringe():
    syringe_flow_extents = {250: 10, 500: 20, 5000: 100, 10000: 240}
    def __init__(self, pump, which, size):
        self.pump = pump
        self.which = which
        self.size = size
        self.rate = 0.0
        self.valve_status = ''
        self.syringe_status = ''
        self.volume = 0.0
        self.max_rate = self.syringe_flow_extents[self.size]
        
class Syringe_Pump_402(Device):
    def __init__(self,gsioc,device_id,left_syringe_volume,right_syringe_volume):
        self.device_id = device_id
        Device.__init__(self,gsioc,device_id)
        self.syringes = [Syringe(self,'L',left_syringe_volume),\
                         Syringe(self,'R',right_syringe_volume)]
        self.read_syringe_status()
        self.pump_valve_status()
        self.set_syringe_size('L',left_syringe_volume)
        self.set_syringe_size('R',right_syringe_volume)
        
    def read_syringe_status(self):
        '''
        reads syringe status. response format = fnnnnnngmmmmmm where
        f and g are left and right syringe status
        N = no errors, R = motor running, O = overload error,
        I = not initialized or being initialized, M = motor missing
        H = uncompleted motion
        W = waiting for other syringe
        nnnnnn and mmmmmm are syringe contents volume in microliters
        '''
        retStr = self.immediate('M')
        if retStr:
            left_status = retStr[0] 
            right_status = retStr[6]
            left_volume = float(retStr[1:6])
            right_volume = float(retStr[7:])
            logger.debug('syringe status and volume: L - (%s,%d), R - (%s,%d)'\
                         %(left_status,left_volume,right_status,right_volume))
            self.syringes[0].syringe_status = left_status
            self.syringes[0].volume = left_volume
            self.syringes[1].syringe_status = right_status
            self.syringes[1].volume = right_volume
            return (left_status,right_status),(left_volume,right_volume)
        else:
            logger.warning('failed to read syringe status')
            return False
        
    def pump_global_status(self):
        '''
        returns global status as "ab" where a is the command status buffer
        and b is the error flag status
        '''
        retStr = self.immediate('S')
        if retStr:
            command_buffer_status = int(retStr[0])
            error_flag_status = int(retStr[1])
            logger.debug('command buffer status: %d, error flag status: %d'\
                        %(command_buffer_status, error_flag_status))
            return command_buffer_status, error_flag_status        
        else:
            logger.warning('failed to read pump global status')
            return False
        
    def pump_valve_status(self):
        '''
        reads pump valve status as ab where a and b are left,right status
        R = valve to reservoir
        N = valve to needle
        X = valve running
        O = valve overload error
        M = valve absent
        '''
        retStr = self.immediate('V')
        if retStr:
            left_status = retStr[0]
            right_status = retStr[1]
            logger.debug('valve status: left - %s, right - %s' \
                         %(left_status,right_status))
            self.syringes[0].valve_status = left_status
            self.syringes[1].valve_status = right_status
            return left_status, right_status
        else:
            logger.warning('failed to read pump valve status')
            return False

    def wait_until_pump_buffer_empty(self, timeout=30.0,polling_delay=0.1):
        t0 = time.time()
        buffer_full = True
        while buffer_full:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting for pump buffer to empty')
                break
            command_buffer_status, error_flag_status = self.pump_global_status()
            if command_buffer_status == 0:
                buffer_full = False
            time.sleep(polling_delay)                

    def buffered(self,cmd):
        retval = self.gsioc.do_cmd(self.device_id,'buffered',cmd)
        self.wait_until_pump_buffer_empty()
        return retval
        
    def aspirate_volume(self,which,volume):
        ''' set aspiration without initiating liquid flow, which = L or R '''
        if self.buffered('A%s%.1f' %(which,volume)):
            logger.debug('set %s syringe to aspirate %.1f uL' %(which,volume))
            return True
        else:
            logger.warning('failed to set aspiration volume')
            return False
    
    def dispense_volume(self,which,volume):
        ''' set dispense without initiating liquid flow, which = L or R '''
        if self.buffered('D%s%d' %(which,volume)):
            logger.debug('set %s syringe to dispense %.1f uL' %(which,volume))
            return True
        else:
            logger.warning('failed to set dispense volume')
            return False
        
    def set_syringe_motor_force(self, which, amplitude):
        # amplitude - 0 = 0%, 1 = 25%, 2 = 37.5%, 3 = 50%, 4 = 75%, 5 = 100%
        if self.buffered('F%s%d' %(which,amplitude)):
            logger.debug('set syringe motor force to: %d' %amplitude)
            return True
        else:
            logger.warning('failed to set syringe motor force')
            return False
    
    def halt_syringe_motors(self,which):
        ''' halts syringe motors, which = L,R,B'''
        if self.buffered('H%s' %which):
            logger.debug('halting syringe motors: %s' %which)
            return True
        else:
            logger.warning('failed to halt syringe motors')
            return False
    
    def initialize_syringe(self,which):
        ''' initializes syringe, which = L,R,B'''
        if self.buffered('O%s' %which):
            logger.debug('initializing syringe: %s' %which)
            return True
        else:
            logger.warning('failed to initialize syringe %s' %which)
            return False
    
    def set_syringe_size(self,which,size):
        ''' set syringe size. which = L,R,B. size = syringe volume in uL '''
        if self.buffered('P%s%d' %(which,size)):
            logger.debug('set syringe %s to size %d' %(which,size))
            return True
        else:
            logger.warning('failed to set syringe size')
            return False
            
    def set_syringe_flow(self, which, flow):
        ''' set syringe flow rate. which = L,R. flow = ml/min '''
        if self.buffered('S%s%.3f' %(which,flow)):
            logger.debug('syringe %s set to %.3f ml/min' %(which,flow))
            if which == 'L':
                self.syringes[0].rate = flow
            elif which == 'R':
                self.syringes[1].rate = flow
            return True
        else:
            logger.warning('failed to set syringe flow')
            return False
        
    def start_syringe(self,which):
        ''' start syringe, which = L,R,B'''
        if self.buffered('B%s' %which):
            logger.debug('syringe %s started' %which)
            return True
        else:
            logger.warning('failed to start syringe')
            return False
            
    def set_syringe_valve(self, which, position):
        ''' valve control. which = L,R. position: R = reservoir, N = needle'''
        if self.buffered('V%s%s' %(which,position)):
            logger.debug('syringe %s valve set to %s' %(which,position))
            return True
        else:
            logger.warning('failed to set syringe valve')
            return False
            
class Syringes():
    def __init__(self, pumps, probe_mapping):
        self.syringes = []        
        self.pumps = pumps
        for pump_idx,syringe_idx in probe_mapping:
            self.syringes.append(self.pumps[pump_idx].syringes[syringe_idx])
                     
    def which(self, syringe_mask):
        which_syringes = defaultdict(list)
        for i,mask in enumerate(syringe_mask):
            if mask == 1:
                syringe = self.syringes[i]
                which_syringes[syringe.pump].append(syringe.which)
        for pump in which_syringes:
            which_syringes[pump] = ''.join(which_syringes[pump])
            if which_syringes[pump] == 'LR':
                which_syringes[pump] = 'B'
        return zip(which_syringes.keys(),which_syringes.values())
    
    def parse_volumes(self, volumes):
        if volumes == 'max':
            volumes = [float(syringe.size) for syringe in self.syringes]
        elif isinstance(volumes,float):
            volumes = [volumes]*len(self.syringes)
        return volumes
    
    def parse_valves(self,valves):
        if isinstance(valves,str):
            valves = [valves]*len(self.syringes)
        return valves
    
    def parse_rates(self, rates):
        if rates == 'max':
            rates = [float(syringe.max_rate) for syringe in self.syringes]
        elif isinstance(rates,float):
            rates = [rates]*len(self.syringes)
        return rates

    def wait_until_not_initializing(self,mask,timeout=30.0,polling_delay=0.2):
        which_pumps_and_syringes = self.which(mask)
        which_pumps = [a for a,b in which_pumps_and_syringes]
        which_syringes = [b for a,b in which_pumps_and_syringes]
        t0 = time.time()
        moving = True
        while moving:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting for syringe to stop moving')
                break
            for pump in which_pumps:
                pump.read_syringe_status()
            syringe_status = [syringe.syringe_status for i,syringe \
                              in enumerate(self.syringes) if mask[i] == 1]
            if 'I' not in syringe_status:
                moving = False
            else:
                time.sleep(polling_delay)
            
    def initialize(self, syringe_mask):
        for pump,syringe in self.which(syringe_mask):
            pump.initialize_syringe(syringe)
        self.wait_until_not_initializing(syringe_mask)
        
    def wait_until_valve_stops(self,mask,timeout=30.0,polling_delay=0.1):
        which_pumps_and_syringes = self.which(mask)
        which_pumps = [a for a,b in which_pumps_and_syringes]
        which_syringes = [b for a,b in which_pumps_and_syringes]
        t0 = time.time()
        moving = True
        while moving:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting for syringe valve to stop')
                break
            for pump in which_pumps:
                pump.pump_valve_status()
            valve_status = [syringe.valve_status for i,syringe \
                            in enumerate(self.syringes) if mask[i] == 1]
            if 'X' not in valve_status:
                moving = False
            else:
                time.sleep(polling_delay)
    
    def wait_until_not_moving(self,mask,timeout=120.0,polling_delay=0.2):
        which_pumps_and_syringes = self.which(mask)
        which_pumps = [a for a,b in which_pumps_and_syringes]
        which_syringes = [b for a,b in which_pumps_and_syringes]
        t0 = time.time()
        moving = True
        while moving:
            if (time.time()-t0) > timeout:
                logger.error('timeout in waiting for syringe to stop moving')
                break
            for pump in which_pumps:
                pump.read_syringe_status()
            syringe_status = [syringe.syringe_status for i,syringe \
                              in enumerate(self.syringes) if mask[i] == 1]
            if 'R' not in syringe_status:
                moving = False
            else:
                time.sleep(polling_delay)
            
    def aspirate(self,syringe_mask,volumes,valves,rates):
        volumes = self.parse_volumes(volumes)
        rates = self.parse_rates(rates)
        valves = self.parse_valves(valves)
        which_idx = [i for i,mask in enumerate(syringe_mask) if mask == 1]
        for idx in which_idx:
            syringe = self.syringes[idx]
            if syringe.valve_status != valves[idx]:
                syringe.pump.set_syringe_valve(syringe.which,valves[idx])
        self.wait_until_valve_stops(syringe_mask)
        for idx in which_idx:
            syringe = self.syringes[idx]
            if syringe.rate != rates[idx]:
                syringe.pump.set_syringe_flow(syringe.which,rates[idx])
            syringe.pump.aspirate_volume(syringe.which,volumes[idx])
        for pump,syringe in self.which(syringe_mask):
            pump.start_syringe(syringe)
        self.wait_until_not_moving(syringe_mask)
        
    def dispense(self,syringe_mask,volumes,rates):
        volumes = self.parse_volumes(volumes)
        rates = self.parse_rates(rates)
        which_idx = [i for i,mask in enumerate(syringe_mask) if mask == 1]
        for idx in which_idx:
            syringe = self.syringes[idx]
            if syringe.valve_status != 'N':
                syringe.pump.set_syringe_valve(syringe.which,'N')
        self.wait_until_valve_stops(syringe_mask)
        for idx in which_idx:
            syringe = self.syringes[idx]
            if syringe.rate != rates[idx]:
                syringe.pump.set_syringe_flow(syringe.which,rates[idx])        
            syringe.pump.dispense_volume(syringe.which,volumes[idx])
        for pump,syringe in self.which(syringe_mask):
            pump.start_syringe(syringe)
        self.wait_until_not_moving(syringe_mask)
        
    def prime(self,syringe_mask,n=1):
        for i in range(n):
            logger.info('priming syringe, n = %d of %d' %(i,n))
            self.aspirate(syringe_mask,'max',['R']*4,'max')
            self.dispense(syringe_mask,'max','max')
    
    def mix(self,syringe_mask,volumes,rates,n=3):
        for i in range(n):
            self.aspirate(syringe_mask,volumes,'N',rates)
            self.dispense(syringe_mask,volumes,rates)
        
class Gilson_System():
    def __init__(self,com_port=1):
        self.gsioc = GSIOC(com_port=com_port)
        
    def add_Quad_Z_215(self, device_id, probe_types):
        self.probes = Probes(Quad_Z_215(self.gsioc,device_id,probe_types))
        self.arm = self.probes.arm
    
    def add_single_port_injector(self,device_id=29):
        self.injector = Injection_Module_819(self.gsioc,device_id)
    
    def add_four_port_injector(self,device_id=28):
        self.injector = Injection_Module_849(self.gsioc,device_id)
        
    def add_valvemate(self,device_id=36):
        self.valvemate = ValveMate(self.gsioc,36)
        
    def add_syringes(self, pump1, pump2, \
                     probe_mapping =[(0,0), (0,1), (1,0), (1,1)]):
        self.syringes = Syringes([Syringe_Pump_402(self.gsioc,\
                                   pump1['device_id'], pump1['left_volume'],\
                                   pump1['right_volume']), \
                                  Syringe_Pump_402(self.gsioc,\
                                   pump2['device_id'], pump2['left_volume'],\
                                   pump2['right_volume'])],\
                                 probe_mapping)
        
    def close(self):
        self.gsioc.close()
    
    def initialize(self,arm=False,injector=False,syringes=False):
        if arm:
            self.arm.home()
        if injector:
            self.injector.valve_load()
        if syringes:
            self.syringes.initialize([1,1,1,1])
    
    def transfer_to_sample_loop(self,coords,volume,rate=1.0,extra=0.0):
        self.probes.move_z([180.0]*4,speed='max')
        mask = [1,0,0,0]
        x,y,z = coords
        self.probes.move_xy(mask=mask,xy=(x,y))
        self.probes.move_z(mask=mask,z=z,speed=10000)
        self.syringes.aspirate(mask,volume+extra,'N',rate)
        self.probes.move_z(mask=mask,z=180.0,speed='max')
        self.probes.move_xy(mask=mask,xy=(544.0,4.3))
        self.probes.move_z(mask=mask,z=80.0,speed='max')
        self.probes.move_z(mask=mask,z=69.0,speed=2000)
        self.injector.valve_load()
        self.syringes.dispense(mask,volume,rate)
        self.injector.valve_inject()
        injection_time = time.time()
        
        self.syringes.dispense(mask,extra,rate)
        for i in range(5):
            self.syringes.aspirate(mask,150.0,'R','max')
            self.syringes.dispense(mask,150.0,'max')
        self.probes.move_z(mask=mask,z=80.0,speed=2000)
        self.probes.move_z(mask=mask,z=180.0,speed='max')
        return injection_time
    
    def prime_syringes(self, n=1):
        self.probes.move_z([180.0]*4,speed='max')
        mask = [1,1,1,1]
        self.probes.move_xy(mask=mask,xy=(20,50))
        self.arm.set_probe_width(9.0)
        self.syringes.initialize(mask)
        self.syringes.prime(mask,n=n)
    #delete     
    def move_volume(self,volume,x,y,z):
        volume=volume*1.03
        self.syringes.aspirate([0,0,1,0],10.,'N','max')
        #self.probes.load_tips([0,0,1,0],box=2,row=12,col=1  ,tip_size=200)
        self.probes.move_xy(mask=[0,0,1,0],xy=(310,185))
        
        
        self.probes.move_z(mask=[0,0,1,0],z=135,speed='max')
        self.probes.move_z(mask=[0,0,1,0],z=100,speed=7000)
        self.syringes.aspirate([1,0,0,0],float(volume),'N',8.0)
        self.probes.move_z(mask=[0,0,1,0],z=130,speed=7000)
        self.syringes.aspirate([1,0,0,0],12.0,'N',5.0)
        self.probes.move_z(mask=[0,0,1,0],z=160,speed='max')

        #move 2nd well
        self.probes.move_xy(mask=[0,0,1,0],xy=(x,y))
        self.probes.move_z(mask=[0,0,1,0],z=150,speed=9000)
        self.probes.move_z(mask=[0,0,1,0],z=z,speed=7000)
        self.syringes.dispense([1,0,0,0],10.0,50.0)
        self.syringes.dispense([1,0,0,0],float(volume),10.0)
        self.syringes.dispense([1,0,0,0],10.0,10.0)
        self.syringes.dispense([1,0,0,0],2.0,'max')
        self.probes.move_z(mask=[0,0,1,0],z=160,speed='max')
        
        
    #delete2
    def move_volume_tip(self,volume,x,y,z):
        volume=volume*1.07
        #self.probes.load_tips([0,1,0,0],box=1,row=12,col=1,tip_size=1000)
        self.probes.move_z(mask=[0,1,0,0],z=168,speed='max')
        #1rst well
        self.probes.move_xy(mask=[0,1,0,0],xy=(281,186))
        self.syringes.aspirate([0,0,1,0],20.,'N','max')
        
        self.probes.move_z(mask=[0,1,0,0],z=150,speed='max')
        self.probes.move_z(mask=[0,1,0,0],z=125,speed=5000)
        self.syringes.aspirate([0,0,1,0],float(volume),'N',5.0)
        self.probes.move_z(mask=[0,1,0,0],z=150,speed=5000)
        self.syringes.aspirate([0,0,1,0],12.0,'N',10.0)
        self.probes.move_z(mask=[0,1,0,0],z=168,speed=5000)
        

        #move 2nd well
        self.probes.move_xy(mask=[0,1,0,0],xy=(x,y))
        self.probes.move_z(mask=[0,1,0,0],z=z,speed=5000)
        self.syringes.dispense([0,0,1,0],10.0,'max')
        self.syringes.dispense([0,0,1,0],float(volume),10.0)
        self.syringes.dispense([0,0,1,0],2.0,'max')
        self.syringes.dispense([0,0,1,0],20.0,'max')
        self.probes.move_z(mask=[0,1,0,0],z=167,speed='max')
        
    def move_volume_from_well(self,volume,x_start,y_start,z_start,x_dest,y_dest,z_dest):
        volume=volume*1.03
        self.syringes.aspirate([0,0,1,0],10.,'N','max')
        #self.probes.load_tips([0,0,1,0],box=2,row=12,col=1  ,tip_size=200)
        self.probes.move_xy(mask=[0,0,1,0],xy=(x_start,y_start))
        
        
        self.probes.move_z(mask=[0,0,1,0],z=145,speed='max')
        self.probes.move_z(mask=[0,0,1,0],z=z_start,speed=5000)
        self.syringes.aspirate([1,0,0,0],float(volume),'N',8.0)
        self.probes.move_z(mask=[0,0,1,0],z=140,speed=5000)
        self.syringes.aspirate([1,0,0,0],12.0,'N',5.0)
        self.probes.move_z(mask=[0,0,1,0],z=160,speed='max')

        #move 2nd well
        self.probes.move_xy(mask=[0,0,1,0],xy=(x_dest,y_dest))
        self.probes.move_z(mask=[0,0,1,0],z=150,speed=9000)
        self.probes.move_z(mask=[0,0,1,0],z=z_dest,speed=7000)
        self.syringes.dispense([1,0,0,0],10.0,50.0)
        self.syringes.dispense([1,0,0,0],float(volume),10.0)
        self.syringes.dispense([1,0,0,0],10.0,10.0)
        self.syringes.dispense([1,0,0,0],2.0,5.0)
        self.probes.move_z(mask=[0,0,1,0],z=160,speed='max')
        



        
        
     
    
class Liquid_Container():
    def __init__(self,lh,x,y,bottom,top):
        self.x = x
        self.y = y
        self.bottom = bottom
        self.top = top

    def move_to_container_xy(self,mask):
        self.lh.probes.move_z([180.0]*4,speed='max')
        self.lh.probes.move_xy(mask=mask,xy=(self.x,self.y))
        
    def get_adjusted_z(self,mask):
        idx = mask.index(1)
        z_offset = self.lh.probes[idx].z_offset
        bottom,top = self.bottom+z_offset, self.top+z_offset
        return bottom,top

    def aspirate(self,mask,volume,rate):
        self.move_to_container_xy(self,mask)        
        adj_bottom, adj_top = self.get_adjusted_z(mask)
        self.lh.probes.move_z(mask=mask,z=adj_top,speed='max')
        self.lh.syringes.aspirate(mask,10.0,'N',1.0)
        self.lh.probes.move_z(mask=mask,z=adj_bottom,speed=5000)
        self.lh.syringes.aspirate(mask,volume,'N',rate)
        self.lh.probes.move_z(mask=mask,z=adj_top,speed=5000)
        self.lh.probes.move_z([180.0]*4,speed='max')
    
    def dispense(self,mask,volume,rate):
        self.move_to_container_xy(mask)
        adj_bottom, adj_top = self.get_adjusted_z(mask)
        self.lh.probes.move_z(mask=mask,z=adj_top,speed='max')
        self.lh.probes.move_z(mask=mask,z=adj_bottom,speed=5000)
        self.lh.syringes.dispense(mask,volume,rate)
        self.lh.syringes.dispense(mask,10.0,'max')
        self.lh.probes.move_z(mask=mask,z=adj_top,speed=5000)
        self.lh.probes.move_z([180.0]*4,speed='max')
        
    def inject(self,volume,rate=1.0):
        offset = self.lh.probes[0].z_offset
        t = self.lh.transfer_to_sample_loop((self.x,self.y,\
                                             self.bottom+offset),\
                                             volume,rate=rate)
    
    def mix(self,mask,volume,rate=1.0,n=3):
        self.move_to_container_xy(self,mask)        
        adj_bottom, adj_top = self.get_adjusted_z(mask)
        self.lh.probes.move_z(mask=mask,z=adj_top,speed='max')
        self.lh.probes.move_z(mask=mask,z=adj_bottom,speed=5000)
        self.lh.syringes.mix(mask,volume,rate,n)
        self.lh.probes.move_z(mask=mask,z=adj_top,speed=5000)
        self.lh.probes.move_z([180.0]*4,speed='max')
        
class Eppendorf_Tube():
    def __init__(self,lh,x,y,bottom):
        Liquid_Container.__init__(self,lh,x,y,bottom,0.0)
        self.top = bottom + 39.0
        
class Well(Liquid_Container):
    def __init__(self,lh,x,y,bottom,top,row,col):
        Liquid_Container.__init__(self,lh,x,y,bottom,top)
        self.row = row
        self.col = col
        self.name = row+col

class Plate_96_Well():
    rows = 8
    columns = 12        
    colNames = map(str,range(1,columns+1,1))
    rowNames = [x for x in 'ABCDEFGH']
    wellNames = [row+col for row in rowNames for col in colNames]
    well_spacing = 9.0
    
    def __init__(self,lh,x_first,y_first,bottom):
        ''' x,y,z_bottom is for first well '''
        self.lh = lh
        self.x = x_first
        self.y = y_first
        self.bottom = bottom
        self.top = bottom + 10.0
        self.wells = []
        for i in range(self.rows):
            for j in range(self.columns):
                x = self.x - (i*self.well_spacing)
                y = self.y + (j*self.well_spacing)
                self.wells.append(Well(self.lh,x,y,self.bottom,self.top,\
                                       self.rowNames[i],self.colNames[j]))
    
    def wellName(self, wellNumber):
        return self.wellNames[wellNumber]
    
    def __getitem__(self,well_name):
        idx = self.wellNames.index(well_name)
        return self.wells[idx]
    
    def get_adjusted_z(self,well_names):
        wells_z_bottom = []
        wells_z_top = []
        x,y = 0,0
        mask = []
        for i,well_name in enumerate(well_names):
            if well_name:
                if not x:
                    x,y = self[well_name].x,self[well_name].y
                offset = self.lh.probes[i].z_offset
                z = self[well_name].bottom
                wells_z_bottom.append(z+offset)
                z = self[well_name].top
                wells_z_top.append(z+offset)
                mask.append(1)
            else:
                wells_z_bottom.append(0)
                wells_z_top.append(0)
                mask.append(0)
        return mask,x,y,wells_z_top,wells_z_bottom
    
    def aspirate(self,well_names,volumes,rate):
        mask,x,y,wells_z_top,wells_z_bottom = self.get_adjusted_z(well_names)
        self.lh.probes.move_z([180.0]*4,speed='max')
        if self.lh.arm.probe_width != self.well_spacing:
            self.lh.arm.set_probe_width(self.well_spacing)
        self.lh.probes.move_xy(mask=mask,xy=(x,y))
        self.lh.probes.move_z(wells_z_top,speed='max')
        self.lh.syringes.aspirate(mask,10.0,'N',1.0)
        self.lh.probes.move_z(wells_z_bottom,speed=5000)
        self.lh.syringes.aspirate(mask,volumes,'N',rate)
        self.lh.probes.move_z(wells_z_top,speed=5000)
        self.lh.probes.move_z([180.0]*4,speed='max')
        
    def dispense(self,well_names,volumes,rate):
        mask,x,y,wells_z_top,wells_z_bottom = self.get_adjusted_z(well_names)
        self.lh.probes.move_z([180.0]*4,speed='max')
        if self.lh.arm.probe_width != self.well_spacing:
            self.lh.arm.set_probe_width(self.well_spacing)
        self.lh.probes.move_xy(mask=mask,xy=(x,y))
        self.lh.probes.move_z(wells_z_top,speed='max')
        self.lh.probes.move_z(wells_z_bottom,speed=5000)
        self.lh.syringes.dispense(mask,volumes,rate)
        self.lh.syringes.dispense(mask,10.0,'max')
        self.lh.probes.move_z(wells_z_top,speed=5000)
        self.lh.probes.move_z([180.0]*4,speed='max')
    
    def inject(self,well_name,volume,rate=1.0,extra=0.0):
        well = self[well_name]
        offset = self.lh.probes[0].z_offset
        t = self.lh.transfer_to_sample_loop((well.x,well.y,\
                                             well.bottom+offset),\
                                             volume,rate=rate,extra=extra)
        return t

    
if __name__ == '__main__':
    import sys
    logging.basicConfig(level=logging.DEBUG)
    probe_types = ['injection','2507253','2507253','2507253']
    syringe_pump_1 = {'device_id':0, 'left_volume': 250.0, 'right_volume': 5000}
    syringe_pump_2 = {'device_id':1, 'left_volume': 5000.0, 'right_volume': 500}
    lh = Gilson_System(com_port = 1)
    lh.add_Quad_Z_215(22,probe_types)
    lh.add_syringes(syringe_pump_1,syringe_pump_2)
    lh.syringes.initialize([1,1,1,1])

   