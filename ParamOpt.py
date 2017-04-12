#naive version, only find x,y,L
import numpy as np
import os
from IntBin import ReadI9BinaryFiles

def readdata(reduceddir,simdir,detN1=0,detN2=0):
    """
    Read the reduced images and the simulated images.

    Parameters
    -----------
    reduceddir: string
                Directory of reduced experimental images, which are outputs from 'ParallelReduction'.
    simdir:     string
                Directory of simulated images, which are outputs from 'IceNine' simulation mode.
    detN1,detN2:int
                index of detector, usually 0 or 1 or 2 or 3. detN1 is for the reduceddir, detN2 is for the simdir

    Returns
    ----------
    mysimdata:  dictionary
                Keys are the frame indices, values are tuple of pixel positions and frame index. The pixels positions are
                saved as n*m ndarry where n is the number of pixels, first two columns are the x, y coordinates.
    myexpdata:  dictionary
                Keys are the frame indices, values are tuple of pixel positions and frame index. The pixels positions are
                saved as n*m ndarry where n is the number of pixels, first two columns are the x, y coordinates, the fourth
                column is the peakID.

    """
    lexp=os.listdir(reduceddir)
    lsim=os.listdir(simdir)
    mysimdata={}
    myexpdata={}
    for fn in lsim:
        if fn[-1]==str(detN2):
            tmp=np.loadtxt(simdir+fn,delimiter=',')
            if len(tmp)>0:
                idx=int(fn[-10:-5])
                mysimdata[idx]=(tmp,idx)
    for fn in lexp:
        if fn[-1]==str(detN1):
            tmp=np.array(ReadI9BinaryFiles(reduceddir+fn))
            if len(tmp[0])>0:
                idx=int(fn[-10:-5])
                myexpdata[idx]=(tmp.T,idx)
    return mysimdata,myexpdata


def myreduce(simdata,expdata):
    """
    Reduce the images for better optimization speed. Each simulated image choose the first pixel, each reduced image choose
    the averages of each peak.

    Parameters
    ----------
    simdata:  dictionary
                Keys are the frame indices, values are tuple of pixel positions and frame index. The pixels positions are
                saved as n*m ndarry where n is the number of pixels, first two columns are the x, y coordinates.
    expdata:  dictionary
                Keys are the frame indices, values are tuple of pixel positions and frame index. The pixels positions are
                saved as n*m ndarry where n is the number of pixels, first two columns are the x, y coordinates, the fourth
                column is the peakID.

    Returns
    --------
    resim:  dictionary
            Reduced simulated data
    reexp:  dictionary
            Reduced experimental data
    """
    resim={}
    reexp={}
    for i in simdata:
        resim[i]=(simdata[i][0][0].reshape((1,-1)),i)
    for i in expdata:
        tmp=expdata[i][0]
	peakid=tmp[:,3].astype('int')
        xmean=np.bincount(peakid,weights=tmp[:,0])/np.bincount(peakid)
        ymean=np.bincount(peakid,weights=tmp[:,1])/np.bincount(peakid)
        reexp[i]=(np.array([xmean,ymean]).T.reshape((-1,2)),i)
    return resim,reexp


def rot(x,y,theta):
    newx=x*np.cos(theta)-y*np.sin(theta)
    newy=y*np.cos(theta)+x*np.sin(theta)
    return newx,newy



pars={'x':(972.219-989.438),'y':(2000.26-2018.58),'L':7.48317/0.00148}
def trans(simdata,micx=0.0715625,micy=-0.091357,SimL=5.49918,SimJ=989.438,SimK=2018.58,par=pars):
    """
    Transform the simulation images, based on the parameters used for that simulation and the guessing parameters for new images.

    Parameters
    ---------
    simdata: dictionary
            Keys are the frame indices, values are tuple of pixel positions and frame index.
    micx,micy: scalar
            The simulated voxel position in I9 mic file. Units are mm.
    SimL,SimJ,SimK: scalar
            The parameters used by I9 simulation in det file. SimL unit is mm, SimJ and SimK units are number of pixels.
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


def kernel(x0,x1,r=5000):
    """
    Guassian kernel, default bandwidth is sqrt(5000) about 70 pixels.
    """
    return np.exp(-np.sum((x0-x1)**2)/float(r))

def similarity(exp,sim):
    """
    Similarity of two images
    """
    xyexp=exp[:,:2]
    xysim=sim[:,:2]
    s=0
    for i in range(len(xysim)):
        for j in range(len(xyexp)):
            s=s+kernel(xyexp[j],xysim[i])
    s=s/float(len(xysim)*len(xyexp))
    return s

def Objective(x,y,L,simdata,expdata,micx=0.0715625,micy=-0.091357,SimL=5.49918,SimJ=989.438,SimK=2018.58):
    """
    Objective function for the optimization

    Parameters
    ----------
    x:  scalar
        True J value minus SimJ, unit is number of pixels
    y:  scalar
        True K value minus SimK, unit is number of pixels
    L:  scalar
        True L distance, unit is number of pixels
    Others:
        See the help information of function trans
    """
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


