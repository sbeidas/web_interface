from models_XPS import *
from models_PM100D import *



class PolazrizationExperiment():


    def __init__(self):   
        self.input_pol_stage=Polarization(group='GROUP1',positioner='POSITIONER')   #to be modified
        self.output_pol_stage=Polarization(group='GROUP2',positioner='POSITIONER')  #to be modified
        self.power_array=[]
        self.output_angles=[]
        self.pm=PM100D()
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
            
            print "(((((((((((((((((((((((((((((((((((((((((((((((((((((((((("
            print "input angle:  "+ str(round(input_angle+(in_iteration*360)))
            print "(("+str(in_iteration)
            print "input_pol_end:  "+ str(input_pol_end)
            print "(((((((((((((((((((((((((((((((((((((((((((((((((((((((((("
            
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
            
            self.power_array,self.output_angles,out_iteration=self.scan_out_pol(output_pol_start,output_pol_end,output_pol_step,self.power_array,in_iteration,out_iteration)
            
        return  self.power_array,self.output_angles
    
    def scan_out_pol(self,output_pol_start,output_pol_end,output_pol_step,power_array=[],in_iteration=0,out_iteration=0):
        
        
        
        
        self.output_pol_stage.moveTo(output_pol_start)
        output_curr_angle=output_pol_start
        
        
        if(output_pol_start==output_pol_end and output_pol_step==0):
            powerReading= (self.pm.power())
            #self.power_array.append(([self.input_pol_stage.getPosition()+(in_iteration*360),powerReading]))
            self.power_array.append(powerReading)
            self.output_angles.append(self.input_pol_stage.getPosition())
            return self.power_array,self.output_angles
        
        while((output_curr_angle+(out_iteration*360))<=output_pol_end):
            if(self.stop):
                return self.power_array,self.output_angles
            
            print "========================================================="
            print "output angle:  "+ str((output_curr_angle+(out_iteration*360)))
            print "=="+str(out_iteration)
            print "output_pol_end:  "+ str(output_pol_end)
            print "========================================================="
            
            #capture data
            powerReading= (self.pm.power())
            #self.power_array.append([self.output_pol_stage.getPosition()+(out_iteration*360),powerReading]) 
            self.power_array.append(powerReading)
            self.output_angles.append(self.output_pol_stage.getPosition())
            
            print powerReading
            
            out_angle=round((self.output_pol_stage.getPosition()+output_pol_step))
            
            if(output_curr_angle>output_pol_end):
                break
            if(out_angle>=360):
                
                out_angle=out_angle%360
                out_iteration+=1
                
            
            self.output_pol_stage.moveTo(out_angle)
            output_curr_angle=out_angle
        return (self.power_array,self.output_angles,out_iteration)
    def stopScan(self):
        self.stop=True

            



    