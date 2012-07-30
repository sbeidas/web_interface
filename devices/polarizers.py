# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib import scimath
from scipy.optimize.minpack import curve_fit
from matplotlib.widgets import Slider


def polarized_intensity(x, amp, phi, bg):
    y = abs(amp)*(np.cos((x - phi)*np.pi/180.))**2 + bg
    return y

def fitpol(x,y, guess=np.array([1, 60., 0.])):
    '''
    print "---------------------------------"
    print y
    print str(len(y))
    print "---------------------------------"
    '''
    p, cov = curve_fit(polarized_intensity, x, y, p0=guess, Dfun=None, maxfev=2500)
    if p[0]<0:
        p[0]*=-1.0
    while p[1]>180.0:
        p[1]-=180.0 
    while p[1]<0.0:
        p[1]+=180.0
        

    
    return p

def general_ellipse(a, b, r0, theta0, phi, theta):
    '''
    The following equation on the polar coordinates (r, θ)  
    describes a general ellipse with semidiameters a and b,
    centered at a point (r0, θ0), with the a axis rotated by
    φ relative to the polar axis.

    a, b are semimajor diameters
    r0. theta0 is the origin
    phi is the rotation angle
    '''
    PP = r0*((b**2-a**2)*np.cos(theta+theta0-2*phi) + (a**2+b**2)*np.cos(theta-theta0))
    RR = (b**2-a**2)*np.cos(2*theta-2*phi) + a**2 + b**2
    QQ = np.sqrt(2)*a*b*np.sqrt(RR - 2*r0**2*(np.sin(theta-theta0))**2)   
    return (PP+QQ)/RR

def fresnel_coefficients(n1, n2, theta):
    cos_out = scimath.sqrt(1-(n1/n2*np.sin(theta)**2))
    cos_in  = np.cos(theta)
    rs = (n1*cos_in  - n2*cos_out)/(n1*cos_in  + n2*cos_out)
    rp = (n1*cos_out - n2*cos_in )/(n1*cos_out + n2*cos_in )
    ts = (2*n1*cos_in)/(n1*cos_in  + n2*cos_out)
    tp = (2*n1*cos_in)/(n1*cos_out + n2*cos_in )
    return rs, rp, ts, tp

# reflectivity and tranmsission
def fresnel_Rs(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    rs = coefficients[0]
    return np.abs(rs)**2

def fresnel_Rp(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    rp = coefficients[1]
    return np.abs(rp)**2

def fresnel_Ts(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    ts = coefficients[2]
    cos_out = scimath.sqrt(1-(n1/n2*np.sin(theta)**2))
    cos_in  = np.cos(theta)
    return (n2*cos_out)/(n1*cos_in)*np.abs(ts)**2

def fresnel_Tp(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    tp = coefficients[3]
    cos_out = scimath.sqrt(1-(n1/n2*np.sin(theta)**2))
    cos_in  = np.cos(theta)
    return (n2*cos_out)/(n1*cos_in)*np.abs(tp)**2

# phase shifts on reflection
def fresnel_Rs_phase(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    rs = coefficients[0]
    return -np.angle(rs) #sign convention...?

def fresnel_Rp_phase(n1, n2, theta):
    coefficients = fresnel_coefficients(n1,n2,theta)
    rp = coefficients[1]
    return np.angle(rp)


class jones_vector():
    def __init__(self, psi_x, psi_y):
        self.psi = np.array([psi_x, psi_y])
    def through_polarizer(self, angle):
        cos = np.cos(angle*np.pi/180.0)
        sin = np.sin(angle*np.pi/180.0)
        M = np.array([[cos*cos+0j,cos*sin+0j],
                      [cos*sin+0j,sin*sin+0j]])
        self.psi = np.dot(M,self.psi)
    def through_quarterwave(self):
        M = np.exp(1j*np.pi/4.0)* np.array([[1.0+0.0j, 0.0+0.0j],
                                            [0.0+0.0j, 0.0-1.0j]])
        self.psi = np.dot(M,self.psi)
    def rotate(self, angle):
        cos = np.cos(angle*np.pi/180.0)
        sin = np.sin(angle*np.pi/180.0)
        M = np.array([[ cos+0j, sin+0j],
                      [-sin+0j, cos+0j]])
        self.psi = np.dot(M,self.psi)
    def plot_field_ellipse(self):
        theta = np.linspace(0,360,1000)*np.pi/180.
        Ix = np.real(self.psi[0] * np.exp(1j*theta))
        Iy = np.real(self.psi[1] * np.exp(1j*theta))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(Ix,Iy)
        plt.xlim(-2,2)
        plt.ylim(-2,2)
        ax.set_aspect(1)
        plt.show()
    def analyze(self, show_plot=False, guess=np.array([1, 60., 0.])):
        theta = np.linspace(0,360,1000)*np.pi/180. #or 1000 angels ?
        Ix = np.real(self.psi[0] * np.exp(1j*theta))
        Iy = np.real(self.psi[1] * np.exp(1j*theta))
        power = np.real(Ix*Ix + Iy*Iy)
        
        p = fitpol(theta*180.0/np.pi,power, guess=guess)
        if (show_plot):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(theta*180.0/np.pi,power)
            plt.xlim(0,360)
            plt.ylim(0,1)
            plt.title('fit: %f, %f, %f'%(p[0],p[1],p[2]))
            plt.show()
        return p

def simulate_scan(angles, inputangle=0.0):
    print '***************** SIMULATING POLARIZER ALIGNMENT TEST @ INPUT ANGLE = %5.2f ***************\n' % inputangle
    filename = 'sim_pol_alignment_%04d.csv'%(inputangle*100)
    f = open(filename, 'a')
    f.write('angle, amplitude, phi, bg\n')
    f.close()
    amp = np.zeros(len(angles))
    phi = np.zeros(len(angles))
    bgs = np.zeros(len(angles))
    for i, inpolangle in enumerate(angles):
        #assume linearly polarized light; vertical
        p = jones_vector(1.0+0.0j, 0.0+0.0j)
        p.rotate(inputangle)
        p.through_polarizer(inpolangle)
        p.through_quarterwave()
        params= p.analyze(show_plot=False, guess=np.array([1.0, 90.0, 0.0]))
        #print '     fit: %5.4f %5.4f %5.4f ' % (params[0], params[1], params[2])
        #pol_cal_build_figure(pos,pow)
        f = open(filename, 'a')
        f.write('%12e, %12e, %12e, %12e\n' % (inpolangle, params[0], params[1], params[2]))
        f.close()
        amp[i] = params[0]
        phi[i] = params[1]
        bgs[i] = params[2]
    return (amp, phi, bgs)
    
def update(val):
    print str(sTestAngle.val)
    angles = np.linspace(0,360,360)
    amp, phi, bgs = simulate_scan(angles, inputangle=sTestAngle.val)
    l1.set_ydata(amp)
    l2.set_ydata(phi)
    l3.set_ydata(bgs)
    plt.draw()
    
testangles = [90.] #(laster angle) np.linspace(40,50,11)
fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)



angles = np.linspace(0,360,360)
for inputangle in testangles:
    amp, phi, bgs = simulate_scan(angles, inputangle=inputangle)
    
    l1,=ax1.plot(angles,amp,label='%4.1f deg'%(inputangle))
    l2,=ax2.plot(angles,phi,label='%4.1f deg'%(inputangle))
    l3,=ax3.plot(angles,bgs,label='%4.1f deg'%(inputangle))


handles, labels = ax1.get_legend_handles_labels()
ax1.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)
ax1.set_xlim(0,360)
ax2.set_xlim(0,360)
ax3.set_xlim(0,360)

axcolor = 'lightgoldenrodyellow'
ax4 =  plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
sTestAngle = Slider(ax4, 'Test Angel', 0, 360.0, valinit=testangles[0])
sTestAngle.on_changed(update)

plt.show()
            

    
'''
The geometry of the setup has a preferred orientation based on the alignment of the Fresnel Rhomb
 - the phase of the output cos should be 45/135 if the rhomb is vertical -- this we can use to find the offset for the output polarizer
 - then we look for the input polarizer scan angles where we get discontinuities in the output phase; these should be 45/135 and give the offset for the input polarizer
 - finally, with the input polarizer fixed at 45deg, we can optimize the transmission by rotating the source if the source is polarized

'''
            
'''
p = jones_vector(1.0/np.sqrt(2.0), 1j/np.sqrt(2.0))  #RCP
'''

'''
n1 = 1.5145
n2 = 1.0
theta = np.linspace(0,90,100)*np.pi/180.
fig = plt.figure()
ax1 = fig.add_subplot(131)
p1 = ax1.plot(theta*180/np.pi, fresnel_Rs(n1, n2, theta), 'r-')
p2 = ax1.plot(theta*180/np.pi, fresnel_Ts(n1, n2, theta), 'k-')
plt.xlim(0,90)
plt.ylim(0,1.01)
plt.legend([p2, p1], ["R", "T"])
plt.title('S polarization')
ax2 = fig.add_subplot(132)
p1 = ax2.plot(theta*180/np.pi, fresnel_Rp(n1, n2, theta), 'r-')
p2 = ax2.plot(theta*180/np.pi, fresnel_Tp(n1, n2, theta), 'k-')
plt.xlim(0,90)
plt.ylim(0,1.01)
plt.legend([p2, p1], ["R", "T"])
plt.title('P polarization')
ax3 = fig.add_subplot(133)
p1 = ax3.plot(theta*180/np.pi, fresnel_Rp_phase(n1, n2, theta)*180/np.pi, 'b-')
p2 = ax3.plot(theta*180/np.pi, fresnel_Rs_phase(n1, n2, theta)*180/np.pi, 'r-')
plt.xlim(0,90)
plt.ylim(0,181)
plt.legend([p2, p1], ["Rp", "Rs"])
plt.title('Phase Shift on Reflection')
plt.show()
'''

'''
# Fesnel Rhomb 
# overall T with phase for P and S...
theta = np.linspace(0,90,100)*np.pi/180.
n_air = 1.0
n_BK7 = 1.5145
Ts = fresnel_Ts(n_air, n_BK7,  0.0) *  fresnel_Rs(n_BK7, n_air, theta)**2 * fresnel_Ts(n_BK7, n_air,  0.0)
Tp = fresnel_Tp(n_air, n_BK7,  0.0) *  fresnel_Rp(n_BK7, n_air, theta)**2 * fresnel_Tp(n_BK7, n_air,  0.0)
phaseTs = 2 * fresnel_Rs_phase(n_BK7, n_air, theta)*180./np.pi
phaseTp = 2 * fresnel_Rp_phase(n_BK7, n_air, theta)*180./np.pi

fig = plt.figure()
ax1 = fig.add_subplot(121)
p1 = ax1.plot(theta*180/np.pi, Ts, 'r-')
p2 = ax1.plot(theta*180/np.pi, Tp, 'k-')
plt.xlim(50,70)
plt.ylim(0,1.01)
plt.legend([p2, p1], ["Ts", "Tp"])
plt.title('Transmission')
ax2 = fig.add_subplot(122)
p1 = ax2.plot(theta*180/np.pi, phaseTs-phaseTp, 'r-')
plt.xlim(50,70)
plt.ylim(-361,361)
plt.title('S-P phase shift')
plt.show()
'''


'''
t = np.linspace(0,600,10000)*np.pi/180.
Is = 1 * np.cos(t)
Ip = 5 * np.cos(t + np.pi/2)
plt.plot(Is,Ip)

theta = np.linspace(0,360,10000)*np.pi/180.
rr = general_ellipse(1, 5, 0, 0, 0, theta)
xr = rr * np.cos(theta)
yr = rr * np.sin(theta)
plt.plot(xr,yr)

plt.xlabel('Is')
plt.ylabel('Ip')
plt.xlim(-12,12)
plt.ylim(-12,12)
plt.show()
'''


'''
#(a, b, r0, theta0, phi, theta)
theta = np.linspace(0,360,10000)*np.pi/180.
rr = general_ellipse(Is, Ip, 0, 0, np.pi/2, theta)
xr = rr * np.cos(theta)
yr = rr * np.sin(theta)
plt.xlim(-12,12)
plt.ylim(-12,12)
plt.plot(xr,yr)
#rotate using Rhomb
angle = 58.935*np.pi/180.
n_air = 1.0
n_BK7 = 1.5145
Ts = fresnel_Ts(n_air, n_BK7,  0.0) *  fresnel_Rs(n_BK7, n_air, angle)**2 * fresnel_Ts(n_BK7, n_air,  0.0)
Tp = fresnel_Tp(n_air, n_BK7,  0.0) *  fresnel_Rp(n_BK7, n_air, angle)**2 * fresnel_Tp(n_BK7, n_air,  0.0)
phaseTs = 2 * fresnel_Rs_phase(n_BK7, n_air, angle)*180./np.pi
phaseTp = 2 * fresnel_Rp_phase(n_BK7, n_air, angle)*180./np.pi
print phaseTs-phaseTp
plt.show()
'''

