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
        #self.plate=Plate(12,8,381.5,62,9)
        self.max_sample_volume=1000
        self.max_well_capacity=2000
        
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
    
            
    def final(self):
        self.getConcentrationSamples()
        index=len(self.conc_array)-1
        self.conc_volume_array =  []
        self.water=[]
        conc=self.max_sample_volume


        while (index >= 0):
            print str(index)
            if  self.conc_array[index]==0 :
                
                self.conc_volume_array.append(0)
                self.water.append(self.max_sample_volume)
                print "Appended 0"
            elif  self.conc_array[index-1]==0:
                self.conc_volume_array.append(conc_volume+self.max_sample_volume)
                self.water.append(0)
                print "["+str(self.conc_array[index])+"] * "+str(conc)+"="+ "["+str(self.conc_array[index-1])+"]"+  "vol"
                print "vol= "+str(conc_volume+self.max_sample_volume)
                print "water= "+str(0)
            elif index==0:
                self.conc_volume_array.append(conc_volume+self.max_sample_volume)
                self.water.append(0 )
                print "["+str(conc_volume)+"] * "+ "["+str(self.conc_array[index-1])+"]"+  "vol2"
                print "water= "+str(0)
            
            else:
                conc_volume=self.getVolumeFromConc(self.conc_array[index],self.conc_array[index-1],conc)
                print "["+str(self.conc_array[index])+"] * "+str(conc)+"="+ "["+str(self.conc_array[index-1])+"]"+  "vol"
                print "vol= "+str(conc_volume)
                print "water= "+str(conc-conc_volume)
                self.conc_volume_array.append(conc_volume)
                self.water.append(conc-conc_volume)
                conc=self.max_sample_volume+conc_volume
            index=index-1
    
        self.conc_volume_array.reverse()
        self.water.reverse()
        #summed = [sum(pair) for pair in zip(sample_array2, self.vol_array)]
        return self.conc_volume_array
    def where(self):
        index=0
        while(self.conc_volume_array[index]+self.water[index]>=self.max_well_capacity):
            index+=1
        return index
    def prepareSamples(self):
        index=self.plate.getIndex()
        self.final()
        iterations=int(((self.conc_volume_array[index]+self.water[index])/self.max_well_capacity)+3)
        
        for i in range(iterations):
            index=0
            self.plate.x_index=0
            self.plate.y_index=0
            
            while(index<self.where()):
                if(index==0):
          
                    if not (self.plate.lh.probes[1].has_tip):
                       self.plate.lh.probes.load_tips([0,1,0,0],box=1,row=12,col=1,tip_size=1000)
                    if not (self.plate.lh.probes[2].has_tip):
                       self.plate.lh.probes.load_tips([0,0,1,0],box=2,row=12,col=1,tip_size=200)
                    final_sample_volume=self.conc_volume_array[index]/iterations
                    water=self.water[index]/iterations
                    print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.max_conc)+"]"+ "and ["+str(water)+"] water")
                    if not water<=0.00001:    #to be modified 
                        self.plate.get_volume_from_eppendorf_tubes(water,940,1000,'L')
                    self.plate.get_volume_from_eppendorf_tubes(final_sample_volume,940,1000,'R')
                    self.plate.nextNode()
                    index+=1
                else:
                    final_sample_volume=self.conc_volume_array[index]/iterations
                    water=self.water[index]/iterations
                    print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.conc_array[index-1])+"]"+ "and ["+str(water)+"] water")
                    
                    

                    if not water==0.0:
                        self.plate.get_volume_from_eppendorf_tubes(water,158,200,'L')
                        print str(water)+ "needed-------"
                    currentNode=self.plate.getCurrentCell()
                    prevNode=self.plate.prevNode()
                    if not final_sample_volume<=0.00001:    #to be modified 
                        self.plate.dilute_conc_from_well(final_sample_volume,940,currentNode,prevNode,1000) 
                    self.plate.nextNode()
                    self.plate.nextNode()
                    index+=1
        while(index<self.count):
            print '######################################'
            self.prepareSample()
    def prepareSample(self):
        
        index=self.plate.getIndex()
        
        if(index<self.count):
           
            
            if(index==0):
                self.final()


                final_sample_volume=self.conc_volume_array[index]
 
                water=self.water[index]
                print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.max_conc)+"]"+  "and ["+str(water)+"] water")
                
                if not (self.plate.lh.probes[1].has_tip):
                   self.plate.lh.probes.load_tips([0,1,0,0],box=1,row=12,col=1,tip_size=1000)
                if not (self.plate.lh.probes[2].has_tip):
                   self.plate.lh.probes.load_tips([0,0,1,0],box=2,row=12,col=1,tip_size=200)
                self.plate.lh.syringes.aspirate([0,0,1,0],15.0,'N','max')
                    
                if not water<=0.00001:    #to be modified 
                    print str(water)+ "needed---------------------"
                    self.plate.get_volume_from_eppendorf_tubes(water,940,1000,'L')
                self.plate.get_volume_from_eppendorf_tubes(final_sample_volume,940,1000,'R')
                

                print str(final_sample_volume)+ "conc needed------------"
         
                
                #self.plate.setCurrentCell(final_sample_volume,self.max_conc,water,final_sample_volume+water)
                self.plate.nextNode()
                
                #self.plate.lh.probes.eject_tips([0,1,0,0])
                #self.plate.lh.probes.load_tips([0,1,0,0],box=1,row=12,col=2,tip_size=1000)
                
            

            else:
                final_sample_volume=self.conc_volume_array[index]
 
                water=self.water[index]
                print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.conc_array[index-1])+"]"+  "and ["+str(water)+"] water")
                if not water==0.0:
                    #elf.plate.lh.move_volume_tip(water,self.plate.getCurrentCell().x,self.plate.getCurrentCell().y,(self.plate.z_end+self.plate.lh.probes[1].z_offset)-10,'L')
                    self.plate.get_volume_from_eppendorf_tubes(water,158,200,'L')
                    print str(water)+ "needed-------"
                currentNode=self.plate.getCurrentCell()
                prevNode=self.plate.prevNode()
                if not final_sample_volume<=0.00001:    #to be modified 
                    self.plate.dilute_conc_from_well(final_sample_volume,940,currentNode,prevNode,1000)
        
                #self.plate.lh.move_volume_from_well(self.vol_array[index-1],prevNode.x,prevNode.y,(self.plate.z_end+self.plate.lh.probes[2].z_offset)-12,currentNode.x,currentNode.y,(self.plate.z_end+self.plate.lh.probes[2].z_offset)-12)
                self.plate.nextNode()
                #   self.plate.setCurrentCell(final_sample_volume,self.conc_array[index],water,final_sample_volume+water)
                print str(final_sample_volume)+ "conc needed------------"
                self.plate.nextNode()
        else:
            self.plate.lh.syringes.dispense([0,0,1,0],15.0,'max')
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
            print '0'
        elif((self.x_index==0) and (self.y_index==0)):
            self.x_index=self.columns-1
            self.y_index=self.rows-1
            print '1'
        else:
            self.y_index=self.rows-1
            self.x_index-=1
            

            print '2'
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
                self.lh.probes.move_xy(mask=[0,1,0,0],xy=(263.5,63))
                self.z_start=100
                self.z_end=91
            else:
                Plate.__init__(self,12,8,381.5,62,9)
                self.lh.probes.move_xy(mask=[0,1,0,0],xy=(381.5,62))
                self.z_start=102
                self.z_end=64
                self.max_well_capacity=2000
                
            
    def iterate(self,direction):
        
        for i in range ((self.rows*self.columns)-1):
            self.lh.probes.move_xy(mask=[0,1,0,0],xy=(self.getCurrentCell().x,self.getCurrentCell().y))
            if(direction=='F'):
                self.nextNode()
            else:
                self.prevNode()
                
    def get_volume_from_eppendorf_tubes(self,volume,tip_volume,probe,eppendorf_tube):
        well_volume_left=self.max_well_capacity-self.getCurrentCell().totalVolume
        
        if volume<tip_volume:
            if(probe==1000):
                z_offset=self.get_z_offset(1000,self.getCurrentCell(),10,volume)
                if(volume*2<well_volume_left):
                    
                    
                    self.lh.move_volume_tip(volume,self.getCurrentCell().x,self.getCurrentCell().y,z_offset,eppendorf_tube,0)
                    self.getCurrentCell().totalVolume+=volume
                else:#need to dispense twice to avoid spilling
                    z_2nd_dispense=self.get_z_offset(1000,self.getCurrentCell(),10,self.getCurrentCell.totalVolume+volume+well_volume_left/2.0)
                    self.lh.move_volume_tip(volume,self.getCurrentCell().x,self.getCurrentCell().y,z_offset,eppendorf_tube,z_2nd_dispense)
                    self.getCurrentCell().totalVolume+=volume
                    
            elif(probe==200):
                self.lh.move_volume(volume,self.getCurrentCell().x,self.getCurrentCell().y,self.get_z_offset(200,self.getCurrentCell(),15,volume),eppendorf_tube)
                self.getCurrentCell().totalVolume+=volume
        else:
            iterations=int((volume/tip_volume)+1)
            vol_iteration=float(volume)/iterations
            for i in range (iterations):
                well_volume_left=self.max_well_capacity-self.getCurrentCell().totalVolume
                if(probe==1000):
                    
                    
                    if(vol_iteration*2<well_volume_left):
                        z_offset=self.get_z_offset(1000,self.getCurrentCell(),10,vol_iteration)

                        self.lh.move_volume_tip(vol_iteration,self.getCurrentCell().x,self.getCurrentCell().y,z_offset,eppendorf_tube,0)
                        self.getCurrentCell().totalVolume+=vol_iteration
                    else:#need to dispense twice to avoid spilling
                        z_offset=self.get_z_offset(1000,self.getCurrentCell(),10,vol_iteration)
                        x=vol_iteration+self.getCurrentCell().totalVolume+float(vol_iteration)/2.0
                        z_2nd_dispense=self.get_z_offset(1000,self.getCurrentCell(),10,x)

                        
                        self.lh.move_volume_tip(vol_iteration,self.getCurrentCell().x,self.getCurrentCell().y,z_offset,eppendorf_tube,z_2nd_dispense)
                        self.getCurrentCell().totalVolume+=vol_iteration



                elif(probe==200):
                    self.lh.move_volume(vol_iteration,self.getCurrentCell().x,self.getCurrentCell().y,self.get_z_offset(200,self.getCurrentCell(),15,vol_iteration),eppendorf_tube)
                    self.getCurrentCell().totalVolume+=vol_iteration

    def dilute_conc_from_well(self,volume,tip_volume,currentNode,prevNode,probe):
        
        well_volume_left=self.max_well_capacity-currentNode.totalVolume
        
        if volume<tip_volume:
                z_offset=self.get_z_offset(probe,currentNode,6,volume)
                if(volume*2<well_volume_left):
                    self.lh.move_volume_from_well(volume,prevNode.x,prevNode.y,self.get_z_offset(probe,prevNode,15,volume),currentNode.x,currentNode.y,self.get_z_offset(probe,currentNode,6,volume),probe)
                    
                else:
                    print'1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111'
                    x=volume+currentNode.totalVolume+float(volume)/2.0
                    z_2nd_dispense=self.get_z_offset(probe,currentNode,0,x)
                    self.lh.move_volume_from_well(volume,prevNode.x,prevNode.y,self.get_z_offset(probe,prevNode,15,volume),currentNode.x,currentNode.y,self.get_z_offset(probe,currentNode,6,volume),probe,z_2nd_dispense)
                    
                currentNode.totalVolume+=volume
                prevNode.totalVolume-=volume
        else:
            iterations=int((volume/tip_volume)+1)
            vol_iteration=float(volume)/iterations
            for i in range (iterations):
                
                if(vol_iteration*2<well_volume_left):
                    self.lh.move_volume_from_well(vol_iteration,prevNode.x,prevNode.y,self.get_z_offset(probe,prevNode,16,vol_iteration),currentNode.x,currentNode.y,self.get_z_offset(probe,currentNode,6,vol_iteration),probe)
                    currentNode.totalVolume+=vol_iteration
                    prevNode.totalVolume-=vol_iteration 
                else:
                    z_offset=self.get_z_offset(probe,currentNode,5,vol_iteration)
                    x=vol_iteration+currentNode.totalVolume+float(vol_iteration)/2.0
                    z_2nd_dispense=self.get_z_offset(probe,currentNode,2,x)
                    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                    print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                    self.lh.move_volume_from_well(vol_iteration,prevNode.x,prevNode.y,self.get_z_offset(probe,prevNode,16,vol_iteration),currentNode.x,currentNode.y,z_offset,probe,z_2nd_dispense)
                    currentNode.totalVolume+=vol_iteration
                    prevNode.totalVolume-=vol_iteration
                    
                
                
    def get_z_offset(self,probe,well,offset,volume_to_aspirate):
        if probe==1000:
            probe=1
        elif probe==200:
            probe=2
            #return  (self.z_end+self.lh.probes[probe].z_offset)+((self.z_start-self.z_end)*(float(well.totalVolume-volume_to_aspirate)/2000.0) -offset)
        #if(well.totalVolume-volume_to_aspirate>=0):
        return  (self.z_end+self.lh.probes[probe].z_offset)+((self.z_start-self.z_end)*(float(abs(well.totalVolume-volume_to_aspirate))/2000.0) -offset)
        #else:
            #return  (self.z_end+self.lh.probes[probe].z_offset)+((self.z_start-self.z_end)*(0/2000.0) -offset)
            
class Sample():
    
    def __init__(self,volume_conc,conc_value,vol_diluent,totalVolume,x,y):    
        self.volume_conc=volume_conc
        self.conc_value=conc_value
        self.vol_diluent=vol_diluent
        self.totalVolume=totalVolume
        self.x=x
        self.y=y
      
        
    def reduceTotalVolume(self,value):

        if(self.totalVolume>=value):
            self.totalVolume=self.totalVolume-value

            self.totalVolume=self.totalVolume-value
        else:
            print 'Not enough Volume of '+ " ["+ str(self.conc_value)+"] available"
            print 'Total Volume= '+str(self.totalVolume)
    def getTotalVolume(self):
        self.totalVolume
    
 
        
        
        
        

        

        
       

       
        
        
         
        
        
        
        
        
        
 
    

  