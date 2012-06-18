


### CONSTANTS
MI_MAX_CAMERAS = 50
MI_MAX_REGS = 400
MI_APTINA_VID = 0x20FB
MI_MICRON_VID = 0x0634
MI_MICRON_PCI_VID = 0x1344
MI_MAX_STRING = 256

## enum mi_error_code
#Generic return codes
MI_CAMERA_SUCCESS          = 0x00         #Success value for midlib routines
MI_CAMERA_ERROR            = 0x01         #General failure for midlib routines
#Grabframe return codes
MI_GRAB_FRAME_ERROR        = 0x03         #General failure for grab frame routine
MI_NOT_ENOUGH_DATA_ERROR   = 0x04         #Grab frame failed to return enough data
MI_EOF_MARKER_ERROR        = 0x05         #EOF packet not found in grab frame dat
MI_BUFFER_SIZE_ERROR       = 0x06         #GrabFrame buffer is too small
#mi_OpenCameras return codes
MI_SENSOR_FILE_PARSE_ERROR = 0x07         #There was an error parsing the sdat file
MI_SENSOR_DOES_NOT_MATCH   = 0x08         #Cannot find sdat file which matches sensor
MI_SENSOR_NOT_INITIALIZED  = 0x09         #The sensor structure has not been initialized (call updateFrame)
MI_SENSOR_NOT_SUPPORTED    = 0x0A         #The sensor is no longer supported
#I2C return codes
MI_I2C_BIT_ERROR           = 0x0B         #I2C bit error  
MI_I2C_NACK_ERROR          = 0x0C         #I2C NAC error
MI_I2C_TIMEOUT             = 0x0D         #I2C time out error
MI_CAMERA_TIMEOUT          = 0x0E      
MI_CAMERA_NOT_SUPPORTED    = 0x10         #The function call is not supported

#return codes for parsing sdat file
MI_PARSE_SUCCESS           = 0x20         #Parsing was successful
MI_DUPLICATE_DESC_ERROR    = 0x21         #Duplicate unique descriptor was found
MI_PARSE_FILE_ERROR        = 0x22         #Unable to open sensor data file
MI_PARSE_REG_ERROR         = 0x23         #Error parsing the register descriptors
MI_UKNOWN_SECTION_ERROR    = 0x24         #Unknown Section found in sensor data file
MI_CHIP_DESC_ERROR         = 0x25         #Error parsing the chip descriptor section
MI_PARSE_ADDR_SPACE_ERROR  = 0x26         #Error parsing the address space section
#Error codes for loading INI presets 
MI_INI_SUCCESS             = 0x100        #INI Preset is loaded successfully
MI_INI_KEY_NOT_SUPPORTED   = 0x101        #Key is not supported - will be ignored
MI_INI_LOAD_ERROR          = 0x102        #Error loading INI preset
MI_INI_POLLREG_TIMEOUT     = 0x103        #time out in POLLREG/POLL_VAR/POLL_FIELD command
MI_INI_HANDLED_SUCCESS     = 0x104        #transport handled the command, success
MI_INI_HANDLED_ERROR       = 0x105        #transport handled the command, with error
MI_INI_NOT_HANDLED         = 0x106        #transport did not handle the command
## end enum mi_error_code

## enum mi_image_types
MI_UNKNOWN_IMAGE_TYPE = 0 
MI_BAYER_8 = 1
MI_BAYER_10 = 2
MI_BAYER_8_ZOOM = 3
MI_BAYER_10_ZOOM = 4
MI_YCBCR = 5
MI_RGB565 = 6
MI_RGB555 = 7
MI_RGB444X = 8
MI_RGBX444 = 9
MI_RGB24 = 10
MI_RGB32 = 11
MI_BAYER_12 = 12
MI_BAYER_S12 = 13  # Signed 16-bit, 0-4095 nominal value range,
                   # intermediate image format used in software colorpipe
MI_RGB48 = 14       # R, G, B, 0-65535
MI_JPEG = 15
MI_BAYER_STEREO = 16  #  each 16-bit pixel is 8-bit left pixel and 8-bit right pixel
MI_PNG = 17
MI_BGRG = 18      # Like YCbCr but with Y->G Cb->B and Cr->R to make an RGB format
MI_YUV420 = 19    # Like YCbCr, but even (numbering from 0) rows are Y-only
MI_BAYER_14 = 20
MI_BAYER_12_HDR = 21  # Compressed HiDy on A-1000ERS
MI_BAYER_14_HDR = 22  # Compressed HiDy on A-1000ERS
MI_BAYER_20 =23
MI_RGB332 = 24
MI_M420 = 25     # Like YCbCr, but even rows are Y-only and odd rows are YYYY...CbCrCbCr...
MI_BAYER_10_IHDR = 26  #  Interlaced HiDy (A-8150, etc.)
MI_JPEG_SPEEDTAGS = 27  # JPEG with Scalado SpeedTags
## end enum mi_image_types

## enum mi_product_ids
MI_UNKNOWN_PRODUCT = 0
MI_BIGDOG    = 0x1002
MI_DEMO_1    = 0x1003
MI_DEMO_1A   = 0x1004
MI_WEBCAM    = 0x1006
MI_DEMO_2    = 0x1007
MI_DEV_2     = 0x1008
MI_MIGMATE   = 0x1009
MI_PCCAM     = 0x100A
MI_MIDES     = 0x100B
MI_MIDES_XL  = 0x100C
MI_DEMO_2X   = 0x100D
MI_CLINK_1   = 0x5555           # Camera Link product ID
MI_CARDCAM_1 = 0xD100
## end enum mi_product_ids

## enum mi_modes
MI_ERROR_CHECK_MODE = 0
MI_REG_ADDR_SIZE = 1
MI_REG_DATA_SIZE = 2
MI_USE_REG_CACHE = 3
MI_SW_UNSWIZZLE_MODE = 4
MI_UNSWIZZLE_MODE = 5
MI_SW_UNSWIZZLE_DEFAULT = 6
MI_DATA_IS_SWIZZLED = 7   
MI_READ_SYNC = 8
MI_WRITE_SYNC = 9
MI_CONTINUOUS_READ = 10
MI_ERROR_LOG_TYPE = 11
MI_SPOOF_SIZE = 12
MI_SPOOF_SUPPORTED = 13
MI_HW_BUFFERING = 14
MI_OUTPUT_CLOCK_FREQ = 15
MI_ALLOW_FAR_ACCESS = 16
MI_PIXCLK_POLARITY = 17
MI_SENSOR_POWER = 18
MI_SENSOR_RESET = 19
MI_SHIP_SPEED = 20
#  XDMA state
MI_DIRECT_VAR_ACCESS = 21
MI_XDMA_LOGICAL = 22
MI_XDMA_PHY_A15 = 23
MI_XDMA_PHY_REGION = 24
MI_HW_FRAME_COUNT = 25
MI_HIDY = 26
MI_COMPRESSED_LENGTH = 27
MI_SENSOR_SHUTDOWN = 28
#  ICPHD 'XDMA' state
MI_XDMA_ADV_BASE = 29
MI_PIXCLK_FREQ = 30
MI_SIMUL_REG_FRAMEGRAB = 31
MI_DETECT_FRAME_SIZE = 32
#  Current bitsperclock and clocksperpixel settings
#  Read-only, use mi_updateFrameSize() to set
MI_BITS_PER_CLOCK = 33
MI_CLOCKS_PER_PIXEL = 34
# Image data receiver parameters (CCP, MIPI, HiSPi, etc.)
MI_RX_TYPE = 35              #  mi_rx_types
MI_RX_LANES = 36
MI_RX_BIT_DEPTH = 37
MI_RX_MODE = 38              #  mi_rx_modes
MI_RX_CLASS = 39
MI_RX_SYNC_CODE = 40
MI_RX_EMBEDDED_DATA = 41
MI_RX_VIRTUAL_CHANNEL = 42
MI_RX_MSB_FIRST = 43
#  HDMI output
MI_HDMI_MODE = 44
MI_EIS = 45  # electronic image stabilization (ICP-HD + HDMI Demo)
#  Capture to demo board RAM
MI_MEM_CAPTURE = 46           # set number of frames to capture
MI_MEM_CAPTURE_PROGRESS = 47  # frames stored do far, read-only
MI_MEM_CAPTURE_MB = 48        # available RAM in MB, read-only
#  Stereo
MI_STEREO_MODE = 49          #  mi_stereo_modes
## end enum mi_modes
MI_SWIZZLE_MODE = MI_SW_UNSWIZZLE_MODE
MI_SWIZZLE_DEFAULT = MI_SW_UNSWIZZLE_DEFAULT

## enum mi_unswizzle_modes
MI_NO_UNSWIZZLE = 0
MI_HW_UNSWIZZLE = 1
MI_SW_UNSWIZZLE = 2
MI_ANY_UNSWIZZLE = 3
## end enum mi_unswizzle_modes

## enum mi_rx_types
MI_RX_UNKNOWN = -1
MI_RX_DISABLED = 0
MI_RX_PARALLEL = 2 # unclear becasue previous two were defined
MI_RX_CCP = 3
MI_RX_MIPI = 4
MI_RX_HISPI = 5
## end enum mi_rx_types

## enum mi_rx_modes
MI_RX_HISPI_S = 0
MI_RX_HISPI_SPS = 1
MI_RX_HISPI_SPP = 2
MI_RX_HISPI_DSLR = 3
## end enum mi_rx_modes

## enum mi_hdmi_modes
MI_HDMI_OFF      = 0
MI_HDMI_1080p60 = 1 # again unclear about numbering
MI_HDMI_720p60 = 2
## end enum mi_hdmi_modes

# enum mi_stereo_modes
MI_STEREO_LEFT = 0 # or monocular
MI_STEREO_RIGHT = 1
MI_STEREO_ROWWISE = 2
MI_STEREO_BLEND = 3
## end enum mi_stereo_modes

## enum mi_sync_types
MI_SYNC_ASAP = 0
MI_VERT_BLANK = 1
MI_NOT_VERT_BLANK = 2
## end enum mi_sync_types

## enum mi_reg_accessibility
MI_RW_READONLY = 0
MI_RW_READWRITE = 1
MI_RW_WRITEONLY = 2
## end enum mi_reg_accessibility

## enum mi_addr_type
MI_REG_ADDR = 0
MI_MCU_ADDR = 1 #  MCU driver variable (MCU logical addressing)
MI_SFR_ADDR = 2 #  MCU special function reg (MCU absolute addressing)
MI_IND_ADDR = 3 #  Indirect access to sensor regs on stereo board
MI_FAR1_REG_ADDR = 4 #  Registers on 1st sensor on far bus
MI_FAR1_MCU_ADDR = 5 #  MCU driver variable on 1st sensor on far bus
MI_FAR1_SFR_ADDR = 6 #  SFR on 1st sensor on far bus
MI_FAR2_REG_ADDR = 7 #  Registers on 2nd sensor on far bus
MI_FAR2_MCU_ADDR = 8 #  MCU driver variable on 2nd sensor on far bus
MI_FAR2_SFR_ADDR = 9 # SFR on 2nd sensor on far bus
## end enum mi_addr_type
### end CONSTANTS

import sys, time
import numpy as np
import ctypes
import Image
import os
import matplotlib.pyplot as plt
import h5py


import ctypes.util
from ctypes import (c_char_p, c_void_p, Structure, POINTER, byref)

PACKBITS = 8  # struct alignment

mi_u8 = ctypes.c_ubyte
mi_u16 = ctypes.c_ushort
mi_u32 = ctypes.c_uint
mi_s8 = ctypes.c_char
mi_s16 = ctypes.c_short
mi_s32 = ctypes.c_int
mi_enum = mi_s32
mi_string = ctypes.c_char * MI_MAX_STRING
mi_intptr = ctypes.c_longlong #if WIN64, do int otherwise

lib = ctypes.util.find_library('midlib2')
dll = ctypes.cdll.LoadLibrary(lib)

class mi_bitfield_t (Structure):
    _pack_ = 8
mi_bitfield_t._fields_ = [
    ('id', mi_string),
    ('bitmask', mi_u32),
    ('rw', mi_s32),
    ('desc', mi_string),
    ('detail', mi_string),
    ('datatype', mi_enum), # mi_data_types
    ('minimum', mi_u32),
    ('maximum', mi_u32),
    ('confidential', mi_s32)
    ]

class mi_addr_space_val_t (Structure):
    _pack_ = 8
mi_addr_space_val_t._fields_ = [
    ('ID', mi_string),
    ('name', mi_string),
    ('val', mi_u32),
    ('type', mi_enum), # mi_addr_type
    ('far_base', mi_u32),
    ('far_addr_size', mi_s32),
    ('far_data_size', mi_s32)
    ]

class mi_reg_data_t (Structure):
    _pack_ = 8
mi_reg_data_t._fields_ = [
    ('unique_desc', mi_string),
    ('reg_addr', mi_u32),
    ('reg_space', mi_u32),
    ('bitmask', mi_u32),
    ('default_val', mi_u32),
    ('rw', mi_s32),
    ('reg_desc', mi_string),
    ('detail', mi_string),
    ('num_bitfields', mi_s32),
    ('bitfield', POINTER(mi_bitfield_t)),
    ('addr_span', mi_s32),
    ('addr_space', POINTER(mi_addr_space_val_t)),
    ('datatype', mi_enum), # mi_data_types
    ('minimum', mi_u32),
    ('maximum', mi_u32),
    ('volat', mi_s32),
    ('confidential', mi_s32)
    ]

class mi_addr_space_t(Structure):
    _pack_ = 8
mi_addr_space_t._fields_ = [
    ('reg_addr', mi_u32),
    ('num_vals', mi_s32),
    ('addr_space_val', POINTER(mi_addr_space_val_t)),
    ('far1_reg_addr', mi_u32),
    ('far2_reg_addr', mi_u32)
    ]

class mi_long_desc_t(Structure):
    _pack_ = 8
mi_long_desc_t._fields_ = [
    ('regName', c_char_p),
    ('bitfieldName', c_char_p),
    ('longDesc', c_char_p)
    ]

class mi_sensor_t(Structure):
    _pack_ = 8
mi_sensor_t._fields_ = [
    ('sensorName', mi_string),
    ('sensorType', mi_enum), # mi_sensor_types
    ('fullWidth', mi_u32),
    ('fullHeight', mi_u32),
    ('width', mi_u32),
    ('height', mi_u32),
    ('zoomFactor', mi_u32),
    ('pixelBytes', mi_u32),
    ('pixelBits', mi_u32),
    ('bufferSize', mi_u32),
    ('imageType', mi_enum), # mi_image_types
    ('shipAddr', mi_u32),
    ('reg_addr_size', mi_s32),
    ('num_regs', mi_s32),
    ('regs', POINTER(mi_reg_data_t)), 
    ('addr_space',POINTER(mi_addr_space_t)), 
    ('sensorFileName', mi_string),
    ('sensorVersion', mi_u32),
    ('partNumber', mi_string),
    ('versionName', mi_string),
    ('far1_sensor', POINTER(mi_sensor_t)),   # struct _mi_sensor_t *
    ('far2_sensor', POINTER(mi_sensor_t)),   # struct _mi_sensor_t *
    ('num_long_desc', mi_s32),
    ('long_desc', POINTER(mi_long_desc_t))
    ]

class mi_chip_t(Structure):
    _pack_ = 8
mi_chip_t._fields_ = [
    ('chipName', mi_string),
    ('baseAddr', mi_u32),
    ('serial_addr_size', mi_s32),
    ('serial_data_size', mi_s32),
    ('num_regs', mi_s32),
    ('regs', POINTER(mi_reg_data_t))
    ]

class mi_frame_data_t(Structure):
    _pack_ = 8
mi_frame_data_t._fields_ = [
    ('frameNumber', mi_u32),
    ('bytesRequested', mi_u32),
    ('bytesReturned', mi_u32),  
    ('numRegsReturned', mi_u32),
    ('regValsReturned', mi_u32 * MI_MAX_REGS),
    ('imageBytesReturned', mi_u32)
    ]
    
class mi_camera_t(Structure):
    _pack_ = 8
    pass
mi_camera_t._fields_ = [
        ('productID', mi_enum), # mi_product_ids
        ('productVersion', mi_u32),
        ('productName', mi_string),
        ('firmwareVersion', mi_u32),
        ('transportName', mi_string),
        ('transportType', mi_u32),
        ('context', c_void_p), # void *
        ('sensor', POINTER(mi_sensor_t)), # mi_sensor_t *
        ('num_chips', mi_s32),
        ('chip', POINTER(mi_chip_t)) # mi_chip_t*
        ]

camera_p  = POINTER(mi_camera_t)

from struct import unpack

class Camera():
    def __init__(self, camera_board = 'APTINA_DEMO'):
        print 'Initializing Sensor Camera...'
        #sensor_data_file = 'c:\Aptina Imaging\sensor_data\MT9V022-REV3.xsdat'
        sensor_data_file = 'c:\Aptina Imaging\sensor_data\MT9V022-REV3.xsdat'
        #inifile = 'c:\Aptina Imaging\apps_data\MT9VO22-REV3.ini'
        cameras = (camera_p * MI_MAX_CAMERAS)()
        nNumCameras = mi_s32()
        retValue = dll.mi_OpenCameras(byref(cameras),byref(nNumCameras),sensor_data_file)
        if not ((nNumCameras.value == 1) and (retValue == MI_CAMERA_SUCCESS)):
            print 'ERROR initializing Aptina Camera'
            sys.exit()
        self.camera = cameras[0].contents
        self.sensor = self.camera.sensor.contents    
        self.camera_p = ctypes.pointer(self.camera)
        print 'start Transport...'
        retValue = dll.mi_startTransport(self.camera_p)
        if retValue == MI_CAMERA_ERROR:
            print 'ERROR Aptina Camera - start Transport'
            sys.exit()
        retValue = dll.mi_LoadINIPreset(self.camera_p,'','')
        if retValue != MI_INI_SUCCESS:
            print 'ERROR Aptina Camera - loading default preset'
            sys.exit()  
        retValue = dll.mi_LoadINIPreset(self.camera_p,'','auto_disabled')
        if retValue != MI_INI_SUCCESS:
            print 'ERROR Aptina Camera - loading auto_disabled preset'
            sys.exit()  
        self.pixel_type = np.dtype('u%d' %self.sensor.pixelBytes)
        self.bufferSize = self.sensor.bufferSize / self.sensor.pixelBytes
        self.imageBuffer = np.zeros(self.bufferSize,dtype=self.pixel_type)
        self.width = self.sensor.width
        self.height = self.sensor.height
        self.size = self.width * self.height
        self.ae = Auto_Exposure(self)
        #camera_board = 'IPC_v1.3'
        if camera_board == 'IPC_v1.3':
            ## set to SW unswizzle mode - required for IPC headboard v1.3
            dll.mi_setMode(self.camera_p, MI_SW_UNSWIZZLE_MODE, 1)
    def getImage(self):
        r = dll.mi_grabFrame(self.camera_p,self.imageBuffer.ctypes.data, 
                             self.sensor.bufferSize)
        if (r != MI_CAMERA_SUCCESS):
            if (r == MI_GRAB_FRAME_ERROR):
                print 'General failure for grab frame routine'
            elif (r == MI_NOT_ENOUGH_DATA_ERROR):
                print 'Grab frame failed to return enough data'
            elif (r == MI_EOF_MARKER_ERROR):
                print 'EOF packet not found in grab frame dat'
            elif (r == MI_BUFFER_SIZE_ERROR):
                print 'GrabFrame buffer is too small'
        im = self.imageBuffer[:self.size].reshape((self.height,self.width))        
        #return time.time(), im
        return np.copy(im)
    
    
        
    def getImage_exp(self,x):
        self.ae.off            #disable auto-exposure
        self.ae.set_exposure(x); #set exposure value to input
        time.sleep(0.3)   
        return np.copy(self.getImage())     #capture image
    
    def getSerialD():
        0
    

    def scan_fixed_exposure(self,numImages,exposure):
        i=0
        a=[]
        print 'Scanning exposure range'
        timestr=str(time.ctime())
        newpath = 'Fixed_Exposure'+timestr
        newpath=newpath.replace(':', ' ')
        os.makedirs(newpath)
        os.chdir(newpath)
        while  (i<numImages) :
            i=i+1
            a=self.getImage_exp(exposure)
            print i
            print '##############################'
            plt.imshow(a) #Needs to be in row,col order
            plt.savefig('fig'+str(i)+'.png')

    
        os.chdir('..')
        return  i
    
    def scan_fixed_exposure_hdf5(self,numImages,exposure):
        i=0
        a=[]
        print 'Scanning exposure range'
        
        newpath = 'hdf5'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        os.chdir(newpath)
  
        f=h5py.File('myfile.hdf5')
        
      
        try:
            group=f['Fixed_Exposure_Scan']
        except :
            group=f.create_group('Fixed_Exposure_Scan')
 
        timestr=str(time.ctime())
        timestamp = timestr
        timestamp=timestamp.replace(':', ' ')
        sub_group=group.create_group(timestamp)
        
        
        
        img_arr = np.empty((480,752,numImages),'uint16')
        for i in range(numImages):
            img_arr[:,:,i] = self.getImage_exp(exposure)

        sub_group.create_dataset('img_arr',data=img_arr)
    
        f.close()
        os.chdir('..')
        return  i
    
        
        
    
    def scan_exposure_range(self):
        i=0
        a=[]
        print 'Scanning exposure range'
        
        
        while not (np.all(a==1023)) :
            i=i+1
            a=self.getImage_exp(i)
            print i
            print '##############################'
            plt.imshow(a) #Needs to be in row,col order
            plt.savefig('fig'+str(i)+'.png')

        return  i

    
    
    def set_binning(self,column=True,row=True):
        if column:
            self.writeRegister('READ_MODE_REG','BIN_COL',1)
        else:
            self.writeRegister('READ_MODE_REG','BIN_COL',0)
        if row:
            self.writeRegister('READ_MODE_REG','BIN_ROW',1)
        else:
            self.writeRegister('READ_MODE_REG','BIN_ROW',0)
    def set_window(self,x0,y0,dx,dy):
        '''
          initial camera state: x0,y0,dx,dy = (1,4,752,480)
          HORZ_BLANK_REG = 94
          #VERT_BLANK_REG = 45
        '''
        self.writeRegister('COL_WINDOW_START_REG','',x0)
        self.writeRegister('ROW_WINDOW_START_REG','',y0+3) # account for ref rows?
        self.writeRegister('COL_WINDOW_SIZE_REG','',dx)
        self.writeRegister('ROW_WINDOW_SIZE_REG','',dy)
        self.writeRegister('HORZ_BLANK_REG','',752-dx+94)
        #self.writeRegister('VERT_BLANK_REG','',480-dy+45)
        nBitsPerClock = mi_u32(0)
        nClocksPerPixel = mi_u32(0)
        retValue = dll.mi_updateFrameSize(self.camera_p,mi_u32(dx),mi_u32(dy),\
                                          nBitsPerClock,nClocksPerPixel)
        self.width = self.sensor.width
        self.height = self.sensor.height
        self.size = self.width * self.height
    def close(self):
        retValue = dll.mi_stopTransport(byref(self.camera))
        print 'Stop Transport = ', retValue    
        #retValue = dll.mi_CloseCameras()
        #print 'Close Cameras', retValue
    def test_fps(self, min_frames, max_frames, step_frames):
        def fps(n):
            a = [(time.time(),self.getImage())[0] for i in range(n)]
            try:
                return n/(a[-1]-a[0])
            except:
                return 0.00
        a = [(i,fps(i)) for i in range(min_frames,max_frames,step_frames)]
        print 'frames\tfps'
        for item in a:
            print '%5d\t%5.2f' %(item[0],item[1])
    def get_exposure(self):
        return self.readRegister('AEC_EXPOSURE','')
    def get_bin(self):
        return self.readRegister('CURRENT_BIN','')
    def set_integration_time(self, x):
        '''
        actual total integration time (in milliseconds) = 
             ((num rows of integration) * (row time)) + overhead
        row time = (COL_WINDOW_SIZE_REG + HORZ_BLANK_REG) master clock periods
        overhead = (COL_WINDOW_SIZE_REG + HORZ_BLANK_REG - 255) periods
        '''
        col_window_size = self.readRegister('COL_WINDOW_SIZE_REG','')
        horz_blank = self.readRegister('HORZ_BLANK_REG','')
        pixel_clock = 26.66e6 # from manual
        #pixel_clock = 27.126e6 # from DevWare?
        row_time = (col_window_size + horz_blank)/pixel_clock
        overhead = (col_window_size + horz_blank - 255)/pixel_clock
        integration_rows = int(np.floor(((x/1000.0)-overhead)/row_time))
        if integration_rows < 0:
            print 'integration time too small - setting minimum...(0.023msec)'
            integration_rows = 0
        self.writeRegister('INTEG_TIME_REG','',integration_rows)
        for i in range(3):
            self.getImage()
        return integration_rows        
    def get_integration_time(self):
        col_window_size = self.readRegister('COL_WINDOW_SIZE_REG','')
        horz_blank = self.readRegister('HORZ_BLANK_REG','')
        pixel_clock = 26.66e6   # from manual
        #pixel_clock = 27.126e6 # from DevWare
        row_time = (col_window_size + horz_blank)/pixel_clock
        overhead = (col_window_size + horz_blank - 255)/pixel_clock
        integration_rows = self.readRegister('INTEG_TIME_REG','')    
        integration_time = ((integration_rows*row_time)+overhead)
        return (integration_time * 1000.0)
    def readRegister(self, regStr, bitStr):
        x = mi_u32(0)
        dll.mi_ReadSensorRegStr(self.camera_p, regStr, bitStr, byref(x))
        return x.value
    def writeRegister(self, regStr, bitStr, x):
        retValue = dll.mi_WriteSensorRegStr(self.camera_p,regStr,bitStr,mi_u32(x))
        return retValue
    ### diagnostic
    def diagnostics(self):
        MI_ALL_ERRORS = 9
        dll.mi_OpenErrorLog(MI_ALL_ERRORS, 'c:\Users\LAB\Desktop\meow')
        print 'current SHiP base address: ',self.sensor.shipAddr
        retValue = dll.mi_DetectSensorBaseAddr(self.camera_p)
        if retValue == MI_CAMERA_ERROR:
            print 'DetectSensorBaseAddr: general error'
        elif retValue == MI_CAMERA_SUCCESS:
            print 'detected SHiP base address: ',self.sensor.shipAddr
        
        print 'current part number:', unpack('B',self.sensor.partNumber)
        dll.mi_DetectPartNumber(self.camera_p)
        print 'detected part number: ',unpack('B',self.sensor.partNumber)
        
        val = mi_u32(0)
        retVal = dll.mi_getMode(self.camera_p, MI_PIXCLK_FREQ, byref(val))
        if retVal == MI_CAMERA_ERROR:
            print 'getMode MI_PIXCLK_FREQ error'
        print 'detected PIXCLK: ',val.value,'Hz'
   
        val = mi_u32(0)   
        retVal = dll.mi_getMode(self.camera_p, MI_DETECT_FRAME_SIZE, byref(val))
        if retVal == MI_CAMERA_ERROR:
            print 'getMode MI_DETECT_FRAME_SIZE error'
        print 'frame size: ',val.value
   
        val = mi_u32(0)
        retVal = dll.mi_getMode(self.camera_p, MI_BITS_PER_CLOCK, byref(val))
        if retVal == MI_CAMERA_ERROR:
            print 'getMode MI_BITS_PER_CLOCK error'
        print 'bits per clock: ',val.value
   
        val = mi_u32(0)
        retVal = dll.mi_getMode(self.camera_p, MI_CLOCKS_PER_PIXEL, byref(val))
        if retVal == MI_CAMERA_ERROR:
            print 'getMode MI_CLOCKS_PER_PIXEL error'
        print 'clocks_per_pixel',val.value
        
        a = self.getImage()
        dll.mi_CloseErrorLog()
        
    def reset_sensor(self):
        retVal = dll.mi_setMode(self.camera_p, MI_SENSOR_RESET, mi_u32(1))
        if retVal == MI_CAMERA_ERROR:
            print 'setMode MI_SENSOR_RESET error'
            
class Auto_Exposure():
    def __init__(self, cam):
        self.cam = cam
        self.cam.writeRegister('EXP_LPF','',0)      # delta exposure time between frames
        self.cam.writeRegister('EXP_SKIP_FRM','',0) # #frames to skip before updating exposure
    def on(self):
        self.cam.writeRegister('AEC_ENABLE','',1)   # enable auto exposure
    def off(self):
        self.cam.writeRegister('AEC_ENABLE','',0)   # disable auto exposure
    def set_exposure(self,x):
        self.cam.writeRegister('INTEG_TIME_REG','',x)
    def set_max_exposure(self,x):
        self.cam.writeRegister('MAX_EXPOSURE','',x)
    def set_pixel_count(self,x):
        self.cam.writeRegister('PIXEL_COUNT','',x)
    def set_desired_bin(self,x):        
        self.cam.writeRegister('DESIRED_BIN','',x)
    def set_bin_diff_threshold(self,x):
        self.cam.writeRegister('BIN_DIFF_THRESHOLD','',x)
    def set_tile_spacing(self,x,y):
        ''' len 5 array for each. First 4 specifiy tile start, last is tile end'''
        for i in range(6):
            self.cam.writeRegister('X%d_SLASH5' %i,'',x[i])
            self.cam.writeRegister('Y%d_SLASH5' %i,'',y[i])
    def set_regular_tile_spacing(self):
        for i,x in enumerate(np.linspace(0,self.cam.width,6).astype(np.int)):
            self.cam.writeRegister('X%d_SLASH5' %i,'',x)
        for i,y in enumerate(np.linspace(0,self.cam.height,5).astype(np.int)):
            self.cam.writeRegister('Y%d_SLASH5' %i,'',y)
    def set_tile_weight(self,x,y,weight):
        self.cam.writeRegister('TILE_X%d_Y%d' %(x,y),'USE_TEST_DATA',weight)

if __name__ == '__main__':   
    cam = Camera(camera_board='IPC_v1.3')
    cam.diagnostics()
    #cam.test_fps(10,60,10)
    cam.close()
    '''
    import matplotlib.cm as cm
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import time
    cam = Camera()
    cam.set_window(340,100,200,200)
    cam.set_integration_time(5)
    '''
    '''
    cam.set_binning(column=True,row=True)
    im = cam.getImage()
    plt.imshow(im)
    plt.show()
    cam.set_binning(column=False,row=False)
    im = cam.getImage()
    plt.imshow(im)
    plt.show()
    cam.close()
    '''
