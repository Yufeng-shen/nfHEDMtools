import numpy as np
from math import floor

def frankie_angles_from_g( g ,verbo=True, **exp ):
    """
    Converted from David's code, which converted from Bob's code.
    I9 internal simulation coordinates: x ray direction is positive x direction, positive z direction is upward, y direction can be determined by right hand rule.
    I9 mic file coordinates: x, y directions are the same as the simulation coordinates.
    I9 detector images (include bin and ascii files): J is the same as y, K is the opposite z direction.
    The omega is along positive z direction.

    Parameters
    ------------
    g: array
       One recipropcal vector in the sample frame when omega==0. Unit is ANGSTROM^-1.
    exp:
        Experimental parameters. If use 'wavelength', the unit is 10^-10 meter; if use 'energy', the unit is keV.

    Returns
    -------------
    2Theta and eta are in radian, chi, omega_a and omega_b are in degree. omega_a corresponding to positive y direction scatter, omega_b is negative y direction scatter.
    """
    ghat = g / np.linalg.norm( g );
    if 'wavelength' in exp:
        sin_theta = np.linalg.norm( g )*exp['wavelength'] / ( 4*np.pi );
    elif 'energy' in exp:
        sin_theta = np.linalg.norm(g)/(exp['energy']*0.506773182)/2
    cos_theta = np.sqrt( 1 - sin_theta**2 );
    cos_chi = ghat[2]; 
    sin_chi = np.sqrt( 1 - cos_chi**2 );
    omega_0 = np.arctan2( ghat[0] , ghat[1] );
    phi = np.arccos( sin_theta / sin_chi) ;
    sin_phi = np.sin( phi );
    eta = np.arcsin( sin_chi*sin_phi/ cos_theta );
    
    if np.fabs( sin_theta ) <= np.fabs( sin_chi ):
        delta_omega = np.arctan2( ghat[0] , ghat[1] );
        delta_omega_b1 = np.arcsin( sin_theta / sin_chi );
        delta_omega_b2 = np.pi - delta_omega_b1; 
        omega_res1 = delta_omega + delta_omega_b1;
        omega_res2 = delta_omega + delta_omega_b2; 
        if omega_res1 > np.pi:
            omega_res1 -= 2*np.pi;
        if omega_res1 < -np.pi:
            omega_res1 += 2*np.pi;
        if omega_res2 > np.pi:
            omega_res2 -= 2*np.pi;
        if omega_res2 < -np.pi:
            omega_res2 += 2*np.pi;
    else:
        omega_res1 = 720;
        omega_res2 = 720;
    if verbo==True:
        print '2theta: ',2*np.arcsin(sin_theta)*180/np.pi
        print 'chi: ',np.arccos(cos_chi)*180/np.pi
        print 'phi: ',phi*180/np.pi
        print 'omega_0: ',omega_0*180/np.pi
        print 'omega_a: ',omega_res1*180/np.pi
        print 'omega_b: ',omega_res2*180/np.pi
        print 'eta: ',eta*180/np.pi
    return {'chi':np.arccos(cos_chi)*180/np.pi,'2Theta':2*np.arcsin(sin_theta),'eta':eta,'omega_a':omega_res1*180/np.pi,'omega_b':omega_res2*180/np.pi} 

class Detector:
    def __init__(self):
        self.__Norm=np.array([0,0,1])
        self.__CoordOrigin=np.array([0.,0.,0.])
        self.__Jvector=np.array([1,0,0])
        self.__Kvector=np.array([0,-1,0])
        self.__PixelJ=0.00148
        self.__PixelK=0.00148
        self.__NPixelJ=2048
        self.__NPixelK=2048
    def Move(self,J,K,trans,tilt):
        self.__CoordOrigin-=J*self.__Jvector*self.__PixelJ+K*self.__Kvector*self.__PixelK
        self.__CoordOrigin=tilt.dot(self.__CoordOrigin)+trans
        self.__Norm=tilt.dot(self.__Norm)
        self.__Jvector=tilt.dot(self.__Jvector)
        self.__Kvector=tilt.dot(self.__Kvector)
    def IntersectionIdx(self,ScatterSrc,TwoTheta,eta):
        dist=self.__Norm.dot(self.__CoordOrigin-ScatterSrc)
        scatterdir=np.array([np.cos(TwoTheta),np.sin(TwoTheta)*np.sin(eta),np.sin(TwoTheta)*np.cos(eta)])
        InterPos=dist/(self.__Norm.dot(scatterdir))*scatterdir+ScatterSrc
        J=int(self.__Jvector.dot(InterPos-self.__CoordOrigin)/self.__PixelJ)
        K=int(self.__Kvector.dot(InterPos-self.__CoordOrigin)/self.__PixelK)
        if 0 <= J <= 2047 and 0 <= K <= 2047:
            return J,K
        else:
            return -1
    def Reset(self):
        self.__init__()
    def Print(self):
        print "Norm: ",self.__Norm
        print "CoordOrigin: ",self.__CoordOrigin
        print "J vector: ",self.__Jvector
        print "K vector: ",self.__Kvector

class CrystalStr:
    def __init__(self,material='new'):
        self.AtomPos=[]
        self.AtomZs=[]
        if material=='gold':
            self.PrimA=4.08*np.array([1,0,0])
            self.PrimB=4.08*np.array([0,1,0])
            self.PrimC=4.08*np.array([0,0,1])
            self.addAtom([0,0,0],79)
            self.addAtom([0,0.5,0.5],79)
            self.addAtom([0.5,0,0.5],79)
            self.addAtom([0.5,0.5,0],79)
        elif material=='copper':
            self.PrimA=3.61*np.array([1,0,0])
            self.PrimB=3.61*np.array([0,1,0])
            self.PrimC=3.61*np.array([0,0,1])
            self.addAtom([0,0,0],29)
            self.addAtom([0,0.5,0.5],29)
            self.addAtom([0.5,0,0.5],29)
            self.addAtom([0.5,0.5,0],29)
        elif material=='Ti7':
            self.PrimA=2.92539*np.array([1,0,0])
            self.PrimB=2.92539*np.array([np.cos(np.pi*2/3),np.sin(np.pi*2/3),0])
            self.PrimC=4.67399*np.array([0,0,1])
            self.addAtom([1/3.0,2/3.0,1/4.0],40)
            self.addAtom([2/3.0,1/3.0,3/4.0],40)
        else:
            pass
    def setPrim(self,x,y,z):
        self.PrimA=np.array(x)
        self.PrimB=np.array(y)
        self.PrimC=np.array(z)
    def addAtom(self,pos,Z):
        self.AtomPos.append(np.array(pos))
        self.AtomZs.append(Z)
    def getRecipVec(self):
        self.RecipA=2*np.pi*np.cross(self.PrimB,self.PrimC)/(self.PrimA.dot(np.cross(self.PrimB,self.PrimC)))
        self.RecipB=2*np.pi*np.cross(self.PrimC,self.PrimA)/(self.PrimB.dot(np.cross(self.PrimC,self.PrimA)))
        self.RecipC=2*np.pi*np.cross(self.PrimA,self.PrimB)/(self.PrimC.dot(np.cross(self.PrimA,self.PrimB)))
    def calStructFactor(self,hkl):
        F=0
        for ii in range(len(self.AtomZs)):
            F+=self.AtomZs[ii]*np.exp(-2*np.pi*1j*(hkl.dot(self.AtomPos[ii])))
        return F
    def getGs(self,maxQ):
        self.Gs=[]
        maxh=int(maxQ/float(np.linalg.norm(self.RecipA)))
        maxk=int(maxQ/float(np.linalg.norm(self.RecipB)))
        maxl=int(maxQ/float(np.linalg.norm(self.RecipC)))
        for h in range(-maxh,maxh+1):
            for k in range(-maxk,maxk+1):
                for l in range(-maxl,maxl+1):
                    if h==0 and k==0 and l==0:
                        pass
                    else:
                        G=h*self.RecipA+k*self.RecipB+l*self.RecipC
                        if np.linalg.norm(G)<=maxQ:
                            if np.absolute(self.calStructFactor(np.array([h,k,l])))>1e-6:
                                self.Gs.append(G)
	self.Gs=np.array(self.Gs)
