import numpy as np
import sys
from Gilson_Liquid_Handlers import *

class Serial_Delution():
    def __init__(self,max_conc,min_conc,count,wellVolume):
        print 'In constructor -Serial_Delution'
        self.max_conc=float(max_conc)
        self.min_conc=float(min_conc)
        self.count=count
  
        self.conc_array =  np.empty((0),'float32')
        self.vol_array =  np.empty((0),'float32')
        
        self.plate=Well_Plate(wellVolume=wellVolume)

        self.max_sample_volume=100

    def getConcentrationSamples(self):
        i=0
        diff=(self.max_conc-self.min_conc)/(self.count-1)
        while (self.count>i):
            conc_point=float(self.max_conc-(diff*i))
            self.conc_array=np.append(self.conc_array,conc_point)
            print conc_point
            i+=1
        return self.conc_array
        
    def getVolumeFromConc(self,desired_conc,reagent_conc,volume_sample):
        
        if(volume_sample==0):
            volume_sample=self.max_sample_volume
            
        solution_volume=(float(desired_conc)*volume_sample)/float(reagent_conc)
        water=volume_sample-solution_volume
        #print ("We need"+"["+str(solution_volume)+"]"+"ml of the"+"["+str(reagent_conc)+"]"+  "and ["+str(water)+"] water")
        return solution_volume
    
    def getSampleVolumeArray(self):
        
        for index in range(len(self.conc_array)):
            
            if not (index==0):
                final_sample_volume=self.getVolumeFromConc(self.conc_array[index],self.conc_array[index-1],0)
                self.vol_array=np.append(self.vol_array,final_sample_volume)
    
        self.vol_array=np.append(self.vol_array,0)
    
    
    
    def prepareSample(self):
        
        index=self.plate.getIndex()
        
        if(index<self.count):
           
            
            if(index==0):
                self.getConcentrationSamples()
                self.getSampleVolumeArray()
                total_volume=self.max_sample_volume+self.vol_array[index]
                final_sample_volume=self.getVolumeFromConc(self.max_conc,self.max_conc,total_volume)
 
                water=total_volume-final_sample_volume
                print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.max_conc)+"]"+  "and ["+str(water)+"] water")
                
                self.plate.lh.probes.load_tips([0,0,1,0],box=2,row=12,col=1,tip_size=200)
                self.plate.lh.probes.load_tips([0,1,0,0],box=1,row=12,col=1,tip_size=1000)
                if not water==0.0:
                    print str(water)+ "needed---------------------"
                    self.plate.lh.move_volume_tip(water,self.plate.getCurrentCell().x,self.plate.getCurrentCell().y,150)
                self.plate.lh.move_volume(final_sample_volume,self.plate.getCurrentCell().x,self.plate.getCurrentCell().y,130)
                print str(final_sample_volume)+ "conc needed------------"
         
                
                self.plate.setCurrentCell(final_sample_volume,self.max_conc,water,total_volume)
                self.plate.nextNode()

            else:
                total_volume=self.max_sample_volume+self.vol_array[index]
                final_sample_volume=self.getVolumeFromConc(self.conc_array[index],self.conc_array[index-1],self.max_sample_volume+self.vol_array[index])
                water=total_volume-final_sample_volume
                print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.conc_array[index-1])+"]"+  "and ["+str(water)+"] water")
                if not water==0.0:
                    self.plate.lh.move_volume_tip(water,self.plate.getCurrentCell().x,self.plate.getCurrentCell().y,150)
                    print str(water)+ "needed-------"
                currentNode=self.plate.getCurrentCell()
                prevNode=self.plate.prevNode()
                self.plate.lh.move_volume_from_well(self.vol_array[index-1],prevNode.x,prevNode.y,130,currentNode.x,currentNode.y,130)
                self.plate.nextNode()
                self.plate.setCurrentCell(final_sample_volume,self.conc_array[index],water,total_volume)
                print str(final_sample_volume)+ "conc needed------------"
                self.plate.nextNode()
        else:
            self.plate.lh.probes.eject_tips([0,1,0,0])
            self.plate.lh.probes.eject_tips([0,0,1,0])
            print 'No more Samples to Dilute'
            
    def getConcentrationArray(self):
         return self.conc_array
   
             
class Plate():
    
    def __init__(self,rows,columns,x_init,y_init,cell_spacing):
        self.array=np.array([])
        self.x_init=x_init
        self.y_init=y_init
        for index in range(rows*columns):
            curr_col=index%rows
            curr_row=index/rows
            x =  self.x_init + (cell_spacing*(curr_row))
            y =  self.y_init+ (cell_spacing*(curr_col))
            self.array=np.append(self.array,Sample(0,0,0,0,x,y))  

        self.array=self.array.reshape(columns,rows)
        self.rows=rows
        self.columns=columns
        
        self.x_index=0
        self.y_index=0
        
    def nextNode(self):
        if(self.rows-1>self.y_index):
            
            self.y_index+=1
            
        elif((self.columns-1==self.x_index) and (self.rows-1==self.y_index)):
            self.x_index=0
            self.y_index=0
        else:
            self.x_index+=1
            self.y_index=0
        print "x: "+str(self.x_index)
        print "y: "+str(self.y_index)
        
        return self.getCell(self.x_index,self.y_index)
        
    def prevNode(self):
        if(0<self.y_index):
            self.y_index-=1
            
        elif((self.x_index==0) and (self.y_index==0)):
            self.x_index=self.columns-1
            self.y_index=self.rows-1
        else:
            self.y_index-=1
            self.x_index=self.columns-1
        
        return self.getCell(self.x_index,self.y_index)
    
  


        #def getCurrentCell(self):
        #print '---------Current Cell--------------'
        #print 'Volume Conc: '+str(self.array[self.x_index][self.y_index].volume_conc)
        #print 'Conc Value: '+str(self.array[self.x_index][self.y_index].conc_value)
        #print 'Volume of diluent :'+ str(self.array[self.x_index][self.y_index].vol_diluent)
        #print 'Total Volume : '+ str(self.array[self.x_index][self.y_index].totalVolume)
        #print '-----------------------------------'

    def setCurrentCell(self,volume_conc,conc_value,vol_diluent,totalVolume):
        self.array[self.x_index][self.y_index].volume_conc=volume_conc
        self.array[self.x_index][self.y_index].conc_value=conc_value
        self.array[self.x_index][self.y_index].vol_diluent=vol_diluent
        self.array[self.x_index][self.y_index].totalVolume=totalVolume
        #self.array[self.x_index][self.y_index].x=x
        #self.array[self.x_index][self.y_index].y=y
        
    def printTotalVolumes(self):
        for samplearray in self.array:
            print "["
            for sample in samplearray:
              
                print str(sample.totalVolume)+","
            print"] \n"
    def printConcValue(self):
        for samplearray in self.array:
            print "["
            for sample in samplearray:
              
                print str(sample.conc_value)+","
            print"] \n"
            
    def printCoordinates(self):
        for samplearray in self.array:
            print "["
            for sample in samplearray:
              
                print "("+str(sample.x)+","+str(sample.y)+")"
            print"] \n"
    
            

    def getCell(self,x,y):
        return self.array[x][y]
    
    def getCurrentCell(self):
        return self.getCell(self.x_index,self.y_index)
        
    def getIndex(self):
        return self.y_index+(self.x_index*(self.rows))
        
class Well_Plate(Plate):
    'Class abstracting  the 12*8 well module,wellVolume is used to indicate the maximuim well volume and thus assign the account for the physical characteristics of the Plate such height and well depth '
    def __init__(self,wellVolume=300):
            
            logging.basicConfig(level=logging.DEBUG)
            probe_types = ['injection','2507253','2507253','2507253']
            syringe_pump_1 = {'device_id':0, 'left_volume': 250, 'right_volume': 5000}
            syringe_pump_2 = {'device_id':1, 'left_volume': 5000, 'right_volume': 500}
            self.lh = Gilson_System(com_port = 1)
            self.lh.add_Quad_Z_215(22,probe_types)
            self.lh.add_syringes(syringe_pump_1,syringe_pump_2)
            self.lh.syringes.initialize([1,1,1,1])
            self.lh.probes.move_z(mask=[1,1,1,1],z=175,speed='max')
            
            if(wellVolume==300):
                Plate.__init__(self,12,8,262,63,9)
                self.lh.probes.move_xy(mask=[0,1,0,0],xy=(263,63))
                self.z_start=100
                self.z_end=91
            else:
                Plate.__init__(self,12,8,381.5,62,9)
                self.lh.probes.move_xy(mask=[0,1,0,0],xy=(381.5,62))
                self.z_start=102
                self.z_end=64
                
            
    def iterate(self,direction):
        
        for i in range ((self.rows*self.columns)-1):
            self.lh.probes.move_xy(mask=[0,1,0,0],xy=(self.getCurrentCell().x,self.getCurrentCell().y))
            if(direction=='F'):
                self.nextNode()
            else:
                self.prevNode()
                
        
class Sample():
    
    def __init__(self,volume_conc,conc_value,vol_diluent,totalVolume,x,y):    
        self.volume_conc=volume_conc
        self.conc_value=conc_value
        self.vol_diluent=vol_diluent
        self.totalVolume=totalVolume
        self.x=x
        self.y=y
      
        
    def reduceTotalVolume(self,value):
        print '--------------'
        print 'Reduce by '+ str(value)
        if(self.totalVolume>=value):

            self.totalVolume=self.totalVolume-value
        else:
            print 'Not enough Volume of '+ " ["+ str(self.conc_value)+"] available"
            print 'Total Volume= '+str(self.totalVolume)
    def getTotalVolume(self):
        self.totalVolume
        
        
        

        

        
       

       
        
        
         
        
        
        
        
        
        
 
    

  