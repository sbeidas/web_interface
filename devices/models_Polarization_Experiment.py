from models_XPS import *
from models_PM100D import *
import os


class PolazrizationExperiment():


    def __init__(self):   
        self.input_pol_stage=Polarization(group='GROUP1',positioner='POSITIONER')   #to be modified
        self.output_pol_stage=Polarization(group='GROUP2',positioner='POSITIONER')  #to be modified
        self.pm=PM100D()
        
    def scan(self,input_pol_start,input_pol_end,input_pol_step,output_pol_start,output_pol_end,output_pol_step):
        self.stop=False
        self.input_pol_stage.moveTo(input_pol_start)
        self.output_pol_stage.moveTo(output_pol_start)
        
        
        intput_angle=input_pol_start  #use current position instead
        output_angle=output_pol_start #use current position instead
        
        while (intput_angle<input_pol_end):
            if(self.stop):
                break


            intput_angle=self.input_pol_stage.getPosition()
            in_angle=(self.input_pol_stage.getPosition()+input_pol_step)%360
            self.input_pol_stage.moveTo(in_angle)
            input_angle=self.input_pol_stage.getPosition()
            #print "Current Input angle: "+str(intput_angle)
            
            output_angle=output_pol_start
            self.output_pol_stage.moveTo(output_angle)
            
            while(output_angle<=output_pol_end):
                if(self.stop):
                    break

                #capture data
                print str(self.pm.power())

                out_angle=int(self.output_pol_stage.getPosition()+output_pol_step)%360
                self.output_pol_stage.moveTo(out_angle)
                output_angle=self.output_pol_stage.getPosition()

    def stopScan(self):
        self.stop=True

            



    