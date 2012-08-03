from models_XPS import *
from models_PM100D import *
from scipy.optimize.minpack import curve_fit
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt

class PolazrizationExperiment():


    def __init__(self):   
        self.input_pol_stage=Polarization(group='GROUP1',positioner='POSITIONER')   #to be modified
        self.output_pol_stage=Polarization(group='GROUP2',positioner='POSITIONER')  #to be modified
        self.pm=PM100D()
        
        self.power_array=np.array([])
        
        self.stop=False
    def scan(self,input_pol_start,input_pol_end,input_pol_step,output_pol_start,output_pol_end,output_pol_step):
        self.stop=False
        
        self.power_array=[]
        self.output_angles=[]
        print "---------------------------------------------------------"
        print "input_pol_start:  "+ str(input_pol_start)
        print "input_pol_end:  "+ str(input_pol_end)
        print "input_pol_step:  "+ str(input_pol_step)
        print "output_pol_start:  "+ str(output_pol_start)
        print "output_pol_end:  "+ str(output_pol_end)
        print "output_pol_step:  "+ str(output_pol_step)

        print "---------------------------------------------------------"
        
        self.input_pol_stage.moveTo(input_pol_start)
        self.output_pol_stage.moveTo(output_pol_start)
        

        
        input_angle=input_pol_start  #use current position instead
        in_iteration=0
        out_iteration=0
        
       
        while (round(input_angle+(in_iteration*360))<=input_pol_end):
            ''''
            print "(((((((((((((((((((((((((((((((((((((((((((((((((((((((((("
            print "input angle:  "+ str(round(input_angle+(in_iteration*360)))
            print "(("+str(in_iteration)
            print "input_pol_end:  "+ str(input_pol_end)
            print "(((((((((((((((((((((((((((((((((((((((((((((((((((((((((("
            '''''
            if(self.stop):
                return self.power_array,self.output_angles
            


            input_angle=self.input_pol_stage.getPosition()
            in_angle=round(self.input_pol_stage.getPosition()+input_pol_step)
            input_angle=in_angle
            
            if(in_angle>=360):
                in_angle=in_angle%360
                in_iteration+=1
                 
            self.input_pol_stage.moveTo(in_angle)
            
            
            #print "Current Input angle: "+str(input_angle)
            
            self.power_array,out_iteration=self.scan_out_pol(output_pol_start,output_pol_end,output_pol_step,self.power_array,in_iteration,out_iteration)
            
        return  self.power_array
    
    def scan_out_pol(self,output_pol_start,output_pol_end,output_pol_step,power_array=[],in_iteration=0,out_iteration=0):
        
        
        
        
        self.output_pol_stage.moveTo(output_pol_start)
        output_curr_angle=output_pol_start
        
        
        if(output_pol_start==output_pol_end and output_pol_step==0):
            powerReading= (self.pm.power())
            self.power_array.append(([self.input_pol_stage.getPosition()+(in_iteration*360),powerReading]))
            '''
            self.power_array.append(powerReading)
            self.output_angles.append(self.input_pol_stage.getPosition())
            '''
            return self.power_array,self.output_angles
        
        while((output_curr_angle+(out_iteration*360))<=output_pol_end):
            if(self.stop):
                return self.power_array
            '''
            print "========================================================="
            print "output angle:  "+ str((output_curr_angle+(out_iteration*360)))
            print "=="+str(out_iteration)
            print "output_pol_end:  "+ str(output_pol_end)
            print "========================================================="
            '''
            #capture data
            powerReading= (self.pm.power())
            self.power_array.append([self.output_pol_stage.getPosition()+(out_iteration*360),powerReading])
            
            '''
            self.power_array.append(powerReading)
            self.output_angles.append(self.output_pol_stage.getPosition())
            '''
            
            print powerReading
            
            out_angle=round((self.output_pol_stage.getPosition()+output_pol_step))
            
            if(output_curr_angle>output_pol_end):
                break
            if(out_angle>=360):
                
                out_angle=out_angle%360
                out_iteration+=1
                
            
            self.output_pol_stage.moveTo(out_angle)
            output_curr_angle=out_angle
        return (self.power_array,out_iteration)
    def stopScan(self):
        self.stop=True
        
    def getAngelsArray(self):
        arr=[]
        for i in range(len(self.power_array)):
            arr.append(self.power_array[i][0])
        return arr
    def getPowersArray(self):
        arr=[]
        for i in range(len(self.power_array)):
            arr.append(self.power_array[i][1])
        return arr
            
        
        
        
    def polarized_intensity(self,x, amp, phi, bg):

        y = np.abs(amp)*(np.cos((x - phi)*np.pi/180.))**2 + bg
        return y

    def fitpol(self,x,y, guess=np.array([1, 90., 0.])):

        p, cov = curve_fit(self.polarized_intensity, x, y, p0=guess, Dfun=None, maxfev=5000,epsfcn=1.0e-7)
        if p[0]<0:
            p[0]*=-1.0
        while p[1]>180.0:
            p[1]-=180.0 
        while p[1]<0.0:
            p[1]+=180.0
            
        
        a=np.isinf(cov)
        if(a.all()):
            print 'Failed to fit function'
        
        return p,cov
    def scan_pol_data_hdf5(self,numImages):
        i=0
        a=[]
        print 'Scanning exposure range'
        
        newpath = 'hdf5'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        os.chdir(newpath)
  
        f=h5py.File('pol_scan.hdf5')
        
        try:
            group=f[str(numImages)]
        except :
            group=f.create_group(str(numImages))
 
        timestr=str(time.ctime())
        timestamp = timestr
        timestamp=timestamp.replace(':', ' ')
        sub_group=group.create_group(timestamp)
        
        theta = np.linspace(0,360,numImages)
        
        img_arr = np.empty((180,2,numImages),'f')
        i=0
        for angle in theta:
            print"**********" +str(i)
            arr=self.scan(angle,angle,1,0,359,2)
            print arr
            img_arr[:,:,i] = arr
            i=i+1

        sub_group.create_dataset('pol_arr',data=img_arr)
    
        f.close()
        os.chdir('..')
        return  i
    
    def get_sim_data(self,filepath):
        
        
        os.chdir(filepath)# cd to directory
        
        f=h5py.File('pol_scan.hdf5','r')
        
        group=f['pol_scan']




'''

os.chdir('C:\Users\LAB\Documents\Subhi-tests\plasmonico_interface\devices\hdf5')

f1 = h5py.File('myfile.hdf5', 'r')
pol_arr=f1['pol_scan']['scan']['pol_arr']

arr=pol_arr[()]
f1.close()

os.chdir('..')

from models_Polarization_Experiment import *
pm=PolazrizationExperiment()
popt=[]	
pcov=[]
for i in range(41):
    x=arr[:,0,i]
    y= arr[:,1,i]
    p0 = np.array([np.max(y)-np.min(y), 53., np.min(y)])
    p ,cov =pm.fitpol(x,y,p0)
    popt.append(p)
    pcov.append(cov)


angels=np.linspace(0,360,41)

popt=np.array(popt)
pcov=np.array(pcov)




amp=popt[:,0]
phi=popt[:,1]
bg=popt[:,2]

fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

ax1.plot(angels,amp)
ax2.plot(angels,phi)
ax3.plot(angels,bg)

ax1.set_xlim(0,360)
ax2.set_xlim(0,360)
ax3.set_xlim(0,360)

plt.show()  
'''


    