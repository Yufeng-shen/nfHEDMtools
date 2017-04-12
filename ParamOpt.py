#naive version, only find x,y,L
import numpy as np
import os
from IntBin import ReadI9BinaryFiles
#number of frames that contains peaks
n=10
#experiment data, a length n list, each element is a x*3 array, x is the number of hitted pixels
expdata=[]
#simulated pattern
simdata=[]

#it's important to replace the hard coded value with the parameters used in simulation,
#like the L=5.5,J=1024,K=2000

def readdata2():
    lexp=os.listdir('/work/yufengs/David/ReducedDavid/')
    lsim=os.listdir('/work/yufengs/David/Sim/')
    mysimdata={}
    myexpdata={}
    for fn in lsim:
        if fn[-1]=='0':
            tmp=np.loadtxt('/work/yufengs/David/Sim/'+fn,delimiter=',')
            if len(tmp)>0:
                idx=int(fn[-10:-5])
                mysimdata[idx]=(tmp,idx)
    for fn in lexp:
        if fn[-1]=='1':
            tmp=np.array(ReadI9BinaryFiles('/work/yufengs/David/ReducedDavid/'+fn))
            if len(tmp[0])>0:
                idx=int(fn[-10:-5])
                myexpdata[idx]=(tmp.T,idx)
    return mysimdata,myexpdata

def readdata():
    lsim=os.listdir('SillySim2/')
    mysimdata={}
    myexpdata={}
    for fn in lsim:
        if fn[-1]=='0':
            tmp=np.loadtxt('SillySim2/'+fn,delimiter=',')
            if len(tmp)>0:
                idx=int(fn[-10:-5])
                mysimdata[idx]=(tmp,idx)
        if fn[-1]=='1':
            tmp=np.loadtxt('SillySim2/'+fn,delimiter=',')
            if len(tmp)>0:
                idx=int(fn[-10:-5])
                myexpdata[idx]=(tmp,idx)
    return mysimdata,myexpdata

def myreduce2(simdata,expdata):
    resim={}
    reexp={}
    for i in simdata:
        resim[i]=(np.mean(simdata[i][0],axis=0).reshape((1,-1)),i)
    for i in expdata:
        tmp=expdata[i][0]
	peakid=tmp[:,3].astype('int')
        xmean=np.bincount(peakid,weights=tmp[:,0])/np.bincount(peakid)
        ymean=np.bincount(peakid,weights=tmp[:,1])/np.bincount(peakid)
        reexp[i]=(np.array([xmean,ymean]).T.reshape((-1,2)),i)
    return resim,reexp

def myreduce(simdata,expdata):
    resim={}
    reexp={}
    for i in simdata:
        resim[i]=(simdata[i][0][0].reshape((1,-1)),i)
    for i in expdata:
        reexp[i]=(expdata[i][0][0].reshape((1,-1)),i)
    return resim,reexp

def rot(x,y,theta):
    newx=x*np.cos(theta)-y*np.sin(theta)
    newy=y*np.cos(theta)+x*np.sin(theta)
    return newx,newy

samplex=0.091357/0.00148
sampley=0.0715625/0.00148
L=5.49918/0.00148


pars={'x':(972.219-989.438),'y':(2000.26-2018.58),'L':7.48317/0.00148}
def trans(simdata,micx=0.0715625,micy=-0.091357,SimL=5.49918,SimJ=989.438,SimK=2018.58,par=pars):
    """
    Transform the simulation images, based on the parameters used for that simulation and the guessing parameters for new images.

    Parameters
    ---------
    simdata: dictionary
            Keys are the frame indices, values are tuple of pixel positions and frame index.
    micx,micy: scalar
            The simulated voxel position in I9 mic file.
    SimL,SimJ,SimK: scalar
            The parameters used by I9 simulation in det file
    par: dictionary
            The parameters used for creating new simulation images

    Returns
    -------
    newsimdata: dictionary
            Transformed simulation images
    """
    samplex=-micy/0.00148
    sampley=micx/0.00148
    L=SimL/0.00148
    newsimdata={}
    for i in simdata:
        new=np.empty((len(simdata[i][0]),2))
        new[:,0]=simdata[i][0][:,0]+par['x']
        new[:,1]=simdata[i][0][:,1]+par['y']
        theta=simdata[i][1]/720.0*np.pi-np.pi/2.0
        x,y=rot(samplex,sampley,theta)
        new[:,0]=(new[:,0]-SimJ+x-par['x'])/(L-y)*(par['L']-y)+SimJ-x+par['x']
        new[:,1]=SimK+par['y']-(SimK-new[:,1]+par['y'])/(L-y)*(par['L']-y)
        newsimdata[i]=(new,i)
    return newsimdata



def kernel2(x0,x1,r=500):
    return r/float(r+np.sum((x0-x1)**2))

def kernel(x0,x1,r=5000):
    return np.exp(-np.sum((x0-x1)**2)/float(r))

def similarity(exp,sim):
    xyexp=exp[:,:2]
    xysim=sim[:,:2]
    s=0
    for i in range(len(xysim)):
        for j in range(len(xyexp)):
            s=s+kernel(xyexp[j],xysim[i])
    s=s/float(len(xysim)*len(xyexp))
    return s

def Object(x,y,L,simdata,expdata,micx=0.0715625,micy=-0.091357,SimL=5.49918,SimJ=989.438,SimK=2018.58):
    par={}
    par['x']=x
    par['y']=y
    par['L']=L
    newsimdata=trans(simdata,micx,micy,SimL,SimJ,SimK,par=par)
    score=[]
    for i in newsimdata:
        if i in expdata:
            score.append(similarity(expdata[i][0],newsimdata[i][0]))
    score=np.array(score)
    res=np.mean(score)
    return res

def Statistics(simdata):
    xysims=[]
    if type(simdata[0])=='tuple':
        for i in range(len(simdata)):
            xysims.append(simdata[i][0][:,:2])
    else:
        for i in range(len(simdata)):
            xysims.append(simdata[i][:,:2])
    xysims=np.array(xysims)
#   xysims=xysims.reshape((-1,3))
    mean=np.mean(xysims,axis=0)
    var=np.var(xysims,axis=0)
    return mean,var 


#bo=BayesianOptimization(Object,{'x':(-40,40),'y':(-10,10)})

