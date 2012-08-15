from models_XPS import *
from models_PM100D import *
from scipy.optimize.minpack import curve_fit
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import scipy.stats.mstats as st
import scipy.signal as sig


class PolazrizationExperiment():
    def __init__(self):   
        self.input_pol_stage=Polarization(group='SPINDLE',positioner='INPUT_POLARIZATION')   #to be modified
        self.output_pol_stage=Polarization(group='SPINDLE2',positioner='OUTPUT_POLARIZATION')  #to be modified
        self.pm=PM100D()
        self.power_array=[]
        self.stop=False
        
        
    def scan(self,input_pol_start,input_pol_end,input_pol_step,output_pol_start,output_pol_end,output_pol_step,num_samples=float('inf')):
        
        self.stop=False
        self.power_array=[]
        
        #move to initial positions
        self.input_pol_stage.moveTo(input_pol_start)
        self.output_pol_stage.moveTo(output_pol_start)
        
        print "---------------------------------------------------------"
        print "input_pol_start:  "+ str(input_pol_start)
        print "input_pol_end:  "+ str(input_pol_end)
        print "input_pol_step:  "+ str(input_pol_step)
        print "output_pol_start:  "+ str(output_pol_start)
        print "output_pol_end:  "+ str(output_pol_end)
        print "output_pol_step:  "+ str(output_pol_step)
        print "---------------------------------------------------------"
        

        

        input_current_angle=input_pol_start  #set current angle to start angel
        in_iteration=0
        
        while (round(input_current_angle+(in_iteration*360))<=input_pol_end):

            print "----------------------------------------------------------"
            print "input angle:  "+ str(round(input_current_angle+(in_iteration*360)))
            print "----------------------------------------------------------"
            

            input_current_angle=round(self.input_pol_stage.getPosition()+input_pol_step)
            
            if(input_current_angle>=360):
                input_current_angle=input_current_angle%360
                in_iteration+=1
                
            self.input_pol_stage.moveTo(input_current_angle)
            
            # spin output polazrization stage
            self.power_array=self.spin_and_capture(output_pol_start
                                                   ,output_pol_end,velocity=80
                                                    ,num_samples=num_samples)
        return  self.power_array
    
    
    def spin_and_capture(self,start_angel,end_angel,velocity=100,acc=500
                         ,num_samples=float('inf')):
        
        self.output_pol_stage.moveTo(float(start_angel))
        self.output_pol_stage.spin(float(velocity),float(acc),wait=False)
        
        i=0
        while(self.output_pol_stage.getPosition()<end_angel):

            if(i>num_samples-1): #change
                print 'spin_and_capture: Too many data points collected, exiting Scan'
            else:
                self.power_array.append( [self.output_pol_stage.getPosition(),self.pm.power()])
                i+=1

        if not (math.isinf(num_samples)):
            while(num_samples>len(self.power_array)):
                self.power_array.append([None,None])
                print 'spin_and_capture: Appending None to fit data array shape'
                
        while(self.output_pol_stage.getPosition()>end_angel):
            pass     
        
        return self.power_array
    
    
    def stopScan(self):
        self.stop=True


    def scan_pol_data_hdf5(self,numImages):
        i=0
        a=[]
        print 'Scanning angels '
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
        
        theta = np.linspace(0,359,numImages)
        theta = np.round(theta)
        
        img_arr = np.array([])
        i=0
        max_samples=0
        for angle in theta:
            if i==0 :
             
              arr=self.scan(angle,angle,1,0,357,1)
              max_samples=len(arr)
              img_arr = np.empty((max_samples,2,numImages),'f')
              
            else:
              arr=self.scan(angle,angle,1,0,357,1,num_samples=max_samples)
              
            print len(arr)
            print img_arr.shape
            
            img_arr[:,:,i]=arr
            i=i+1

        sub_group.create_dataset('pol_arr',data=img_arr)
    
        f.close()
        os.chdir('..')
        self.output_pol_stage.stop() 
        return  img_arr
    
def get_sim_data(filepath,array="all"):
    
    os.chdir(filepath)# cd to directory
    f=h5py.File('sim_data.hdf5','r')
    
    if(array=='all'):
        amps_arr=f['amps']['amps_arr']
        bgs_arr=f['bgs']['bgs_arr']
        phis_arr=f['phis']['phis_arr']

        return amps_arr,phis_arr,bgs_arr
    else:
        data_arr=np.copy(f[array][array+'_arr'])
        f.close()
        return np.array(data_arr)
        
def get_exp_data(plot=False):#change: add filepath
    
    os.chdir('C:\Users\LAB\Documents\Subhi-tests\plasmonico_interface\devices\hdf5')
    
    f1 = h5py.File('pol_scan.hdf5', 'r')
    pol_arr=f1['359']['slow']['pol_arr']
    arr=pol_arr[()]
    f1.close()

    popt=[]	
    pcov=[]

    d3_aray=len(arr[0,0,:]) #3d dimension of array (number of input angels sampled)
    nan_arr=[]

    for i in range(d3_aray):
        x=arr[:,0,i]
        y= arr[:,1,i]

        x=x[~np.isnan(x)]#remove nan values from array
        y=y[~np.isnan(y)]#remove nan values from array

        p0 = np.array([np.max(y)-np.min(y), 60., np.min(y)])    
        p ,cov =fitpol(x,y,p0)
   
        popt.append(p)
        pcov.append(cov)
        nan_arr.append(float(i))

    popt=np.array(popt)
    pcov=np.array(pcov)

    amp=popt[:,0]
    phi=popt[:,1]
    bg=popt[:,2]

    if plot:
        angels=np.linspace(0,359,d3_aray)
        plot_parameters(amp,phi,bg,angels)

    return amp,phi,bg,angels


def plot_parameters(amp,phi,bg,angels):
    
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
    

def polarized_intensity(x, amp, phi, bg):
    y = np.abs(amp)*(np.cos((x - phi)*np.pi/180.))**2 + bg
    return y

def fitpol(x,y, guess=np.array([1, 90., 0.])):
    p, cov = curve_fit(polarized_intensity, x, y, p0=guess, Dfun=None, maxfev=500000,epsfcn=1.0e-9)
    if p[0]<0:
        p[0]*=-1.0
    while p[1]>180.0:
        p[1]-=180.0 
    while p[1]<0.0:
        p[1]+=180.0

    a=np.isinf(cov)
    if(a.all()):
        print 'Failed to fit a function'

    return p,cov

class AnalyizePol():
    def __init__(self):
        
        #Simulation Amplitude,Phase and BackGround(offset) arrays
        amps,phis,bgs=get_sim_data('C:\Users\LAB\Documents\Subhi-tests\plasmonico_interface\devices\hdf5')

        self.sim_amps=amps
        self.sim_phis=phis
        self.sim_bgs=bgs

        #get experimental data
        exp_amps,exp_phis,exp_bgs,angels=get_exp_data()
        self.angels=angels
        self.exp_amps=exp_amps
        self.exp_phis=exp_phis
        self.exp_bgs=exp_bgs
        
        #removing extra data point (hdf5 need to be modified to avoid this)
        amps=np.delete(amps,359,1)
        phis=np.delete(phis,359,1)
        bgs=np.delete(bgs,359,1)


    def adjustPhase(self,observed,expected,plot=False):
        
        #fit observed and experimental 
        p_o=fitpol(np.linspace(0,358,359),observed)
        p_e=fitpol(np.linspace(0,358,359),expected)
        
        delta=int(round((p_e[0][1])-(p_o[0][1])))%180
        print 'Phase adjusted by:'+str(delta)

        #roll values in array to adjust for phase
        self.exp_amps=np.roll(self.exp_amps,delta)
        self.exp_phis=np.roll(self.exp_phis,delta)
        self.exp_bgs=np.roll(self.exp_bgs,delta)
        
        if(plot==True):
            angels=np.linspace(0,358,359)
            plot_parameters(self.exp_amps,self.exp_phis,self.exp_bgs,angels)


    def corrolateAmps(self):
        cor=[]
        self.adjustPhase(self.exp_phis,self.sim_phis[0,0:359])
        
        #TODO: fix sim data to avoid using "-2" to ignore 2 thast 2 extra data rows 
        for i in range(len(self.sim_amps)-2):

            # adjust for amp magnitude difference between simulation and exp results
            bg_observed=self.exp_bgs
            bg_expected=self.sim_bgs[i,0:359]
            max_sim_bg=bg_expected.max()
            max_exp_bg=bg_observed.max()
            bg_observed=(max_sim_bg/max_exp_bg)*bg_observed 

            # adjust for amp magnitude difference between simulation and exp results
            amp_observed=self.exp_amps
            amp_expected=self.sim_amps[i,0:359]
            max_sim_amp=amp_expected.max()
            max_exp_amp=amp_observed.max()
            amp_observed=(max_sim_amp/max_exp_amp)*amp_observed 

            
            amp_chi=st.chisquare(amp_expected,amp_observed)#amp chisqaure
            bg_chi=st.chisquare(bg_expected,bg_observed) #bg chisqaure

            #TODO: fix 
            cor.append(amp_chi+bg_chi) # append values amp and bg to array

        cor=np.array(cor)# cast to numpy array

        return cor[:,0].argmin() # get location of minumuim chisquare in array (angle)
        
        
        

'''
 if(i==45):
     fig = plt.figure()
     ax = fig.add_subplot(111)
     ax.plot(np.linspace(0,358,359),amp_observed,'b-',np.linspace(0,358,359),amp_expected,'r-')
     plt.show()
 '''     
        
'''
angels=np.linspace(0,358,359)
fig = plt.figure()
ax1 = fig.add_subplot(311)
ax1.plot(angels,self.exp_phis,'ro',angels,expected,'b-')
plt.show
'''
'''
    def scan_out_pol(self,output_pol_start,output_pol_end,output_pol_step,power_array=[],in_iteration=0,out_iteration=0):
        self.output_pol_stage.moveTo(output_pol_start)
        output_curr_angle=output_pol_start
        
        if(output_pol_start==output_pol_end and output_pol_step==0):
            powerReading= (self.pm.power())
            self.power_array.append(([self.input_pol_stage.getPosition()+(in_iteration*360),powerReading]))
           
            #self.power_array.append(powerReading)
            #self.output_angles.append(self.input_pol_stage.getPosition())
            
            return self.power_array,self.output_angles
        
        while((output_curr_angle+(out_iteration*360))<=output_pol_end):
            if(self.stop):
                return self.power_array
            #capture data
            powerReading= (self.pm.power())
            self.power_array.append([self.output_pol_stage.getPosition()+(out_iteration*360),powerReading])
            out_angle=round((self.output_pol_stage.getPosition()+output_pol_step))  
            if(output_curr_angle>output_pol_end):
                break
            if(out_angle>=360):
                out_angle=out_angle%360
                out_iteration+=1
            self.output_pol_stage.moveTo(out_angle)
            output_curr_angle=out_angle
        return (self.power_array,out_iteration)
        '''




    