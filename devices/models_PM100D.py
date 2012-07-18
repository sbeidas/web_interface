# -*- coding: utf-8 -*-
"""
Created on Fri May 06 17:37:25 2011

@author: LAB
"""

import visa
import numpy as np
import time
import matplotlib.pyplot as plt

class PM100D():
    def __init__(self):
        self.session = visa.instrument('USB0::0x1313::0x8078::PM002374')
        print 'Opening VISA session with PM100D'
        self.session.write('syst:lfr 60')
        self.session.write('disp:brig 0')
        self.session.write('init:conf:pow')
        self.session.write('init:meas:pow')
        self.session.write('sens:aver:count 1')
        self.session.write('pow:rang:auto 0')
        self.session.write('inp:pdi:filt:lpas 0')
    def power(self, n=1):
        vals = np.empty(n)
        for i in range(n):
            vals[i] = self.session.ask_for_values('meas:pow?')[0]
        return np.median(vals)
    def setwavelength(self, wl):
        self.session.write('sens:corr:wav %.2f' % wl)
    def getwavelength(self):
        return self.session.ask_for_values('sens:corr:wav?')[0]
    def autorange(self):
        self.session.write('pow:rang:auto 1')
        self.session.write('pow:rang:auto 0')
    def autorange_on(self):
        self.session.write('pow:rang:auto 1')
    def autorange_off(self):
        self.session.write('pow:rang:auto 0')       
    def inspect_calibration(self):
        print '*************** testing PM calibration ' 
        print '*************** illumination conditions should be measureable and constant '
        print '     wavelengths, measured power'
        wls = np.arange(400,1100,5)
        p = []
        for wl in wls:
            pm.setwavelength(wl)
            pm.autorange()
            power = pm.power(10)
            p.append(power)
            print '%12f, %12f' % (wl,power)
        fig = plt.figure()
        plt.plot(wls, np.reciprocal(p), 'go', label='measured powers')
        plt.show()
            
if __name__ == '__main__':

    datapoints = 20
    print 'num PM reads: %d' % datapoints
    
    pm = PM100D()
    
    print 'setting wavelength to 600nm'
    pm.setwavelength(600)
    
    values = np.empty(datapoints)
    for i in range(datapoints):
        values[i]=pm.power()
    print 'avg PM read:', np.average(values)
    
    print 'setting wavelength to 700nm'
    pm.setwavelength(700)

    values = np.empty(datapoints)
    for i in range(datapoints):
        values[i]=pm.power()
    print 'avg PM read:', np.average(values)
    
    print 'autoranging'
    pm.autorange()
    values = []
    values = np.empty(datapoints)
    for i in range(datapoints):
        values[i]=pm.power()
    print 'avg PM read:', np.average(values)               
    
    #pm.inspect_calibration()
    


