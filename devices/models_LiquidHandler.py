import numpy as np

class Serial_Delution():
    def __init__(self,max_conc,min_conc,count):
        self.max_conc=float(max_conc)
        self.min_conc=float(min_conc)
        self.count=count
  
        self.conc_array =  np.empty((0),'float32')
        self.vol_array =  np.empty((0),'float32')
        
        self.plate=Plate(12,8)
        
        self.max_sample_volume=1

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
                self.plate.setCurrentCell(final_sample_volume,self.max_conc,water,total_volume)
                self.plate.nextNode()

            else:
                total_volume=self.max_sample_volume+self.vol_array[index]
                final_sample_volume=self.getVolumeFromConc(self.conc_array[index],self.conc_array[index-1],self.max_sample_volume+self.vol_array[index])
                water=total_volume-final_sample_volume
                print ("We need"+"["+str(final_sample_volume)+"]"+"ml of the"+"["+str(self.conc_array[index-1])+"]"+  "and ["+str(water)+"] water")
                
                self.plate.prevNode().reduceTotalVolume(self.vol_array[index-1])
                self.plate.nextNode()
                self.plate.setCurrentCell(final_sample_volume,self.conc_array[index],water,total_volume)
                self.plate.nextNode()
        else:
            print 'No more Samples to Dilute'
            
    def getConcentrationArray(self):
         return self.conc_array
   
             
class Plate():
    
    def __init__(self,rows,columns):
        self.array=np.array([])
        for index in range(rows*columns):
            self.array=np.append(self.array,Sample(0,0,0,0))
            
        self.array=self.array.reshape(columns,rows)
        self.rows=rows
        self.columns=columns
        
        self.x_index=0
        self.y_index=0
        
    def nextNode(self):
        if(self.rows>self.y_index+1):
            self.y_index+=1
            
        elif((self.rows==self.x_index+1) and (self.columns==self.y_index+1)):
            self.x_index=0
            self.y_index=0
        else:
            self.x_index+=1
            self.y_index=0
        
        return self.getCell(self.y_index,self.x_index)
        
    def prevNode(self):
        if(0<self.y_index):
            self.y_index-=1
            
        elif((0==self.x_index) and (0==self.y_index)):
            self.x_index=self.rows-1
            self.y_index=self.columns-1
        else:
            self.x_index-=1
            self.y_index=self.columns-1
        
        return self.getCell(self.y_index,self.x_index)
    
  


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
            
        
          

    def getCell(self,x,y):
        return self.array[y][x]
        
    def getIndex(self):
        return self.y_index+(self.x_index*(self.rows))
        
class Sample():
    
    def __init__(self,volume_conc,conc_value,vol_diluent,totalVolume):    
        self.volume_conc=volume_conc
        self.conc_value=conc_value
        self.vol_diluent=vol_diluent
        self.totalVolume=totalVolume
      
        
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
        
        
        

        

        
       

       
        
        
         
        
        
        
        
        
        
 
    

  