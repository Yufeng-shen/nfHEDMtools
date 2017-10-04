from sympy import Symbol,asin,diff,sin,cos,Matrix
import numpy as np
from scipy.optimize import linprog

chi=Symbol('chi')
g=Symbol('g')
O=Symbol('O')
k=Symbol('k')
dg=Symbol('dg')
dchi=Symbol('dchi')
dO=Symbol('dO')

Ob=asin((g/2/k/sin(chi)))

dOb=diff(Ob,g)*dg+diff(Ob,chi)*dchi

x=g*sin(chi)*sin(O)
y=g*sin(chi)*cos(O)
z=g*cos(chi)

Dx=Symbol('Dx')
Dy=Symbol('Dy')
Dz=Symbol('Dz')

m=Matrix([[diff(x,g),diff(x,chi),diff(x,O)],[diff(y,g),diff(y,chi),diff(y,O)],[diff(z,g),diff(z,chi),diff(z,O)]])
mI=m.inv()

def get_co(PeakInfo,G,energy=71.676):
#plus or minus depends on omega_a or omega_b
    if PeakInfo['WhichOmega']=='a':
        expr=dO+dOb.subs([(chi,PeakInfo['chi']/180.0*np.pi),(g,np.linalg.norm(G)),(k,energy*0.506773182)])
    elif PeakInfo['WhichOmega']=='b':
        expr=dO-dOb.subs([(chi,PeakInfo['chi']/180.0*np.pi),(g,np.linalg.norm(G)),(k,energy*0.506773182)])
    a=mI.subs([(chi,PeakInfo['chi']/180.0*np.pi),(g,np.linalg.norm(G)),(O,PeakInfo['omega_0']/180.0*np.pi)]).dot([Dx,Dy,Dz])
    line=expr.subs([(dg,a[0]),(dchi,a[1]),(dO,a[2])])
    return line.subs([(Dx,1),(Dy,0),(Dz,0)]), line.subs([(Dx,0),(Dy,1),(Dz,0)]), line.subs([(Dx,0),(Dy,0),(Dz,1)])

def get_co_true(PeakInfo,G,energy=71.676):
    g=np.linalg.norm(G)
    g2=g**2
    x=G[0]
    y=G[1]
    z=G[2]
    xy2=x**2+y**2
    tmp=g/((2*energy*0.506773182*np.sin(PeakInfo['chi']/180.0*np.pi))**2-g2)**0.5
    if PeakInfo['WhichOmega']=='a':
        return tmp*(2*x/g2-x/xy2)+y/xy2, tmp*(2*y/g2-y/xy2)-x/xy2, tmp*2*z/g2
    if PeakInfo['WhichOmega']=='b':
        return -tmp*(2*x/g2-x/xy2)+y/xy2, -tmp*(2*y/g2-y/xy2)-x/xy2, -tmp*2*z/g2



def get_limit6(NumOmega,oPeaks,PeaksInfo,Gs,lims,energy=71.676):
    """
    for test, only use one L distance
    """
    L=0
    co_s=[]
    b_s=[]
    g_s=[]
    for i in range(len(oPeaks)):
        if lims[i]==None:
            pass
        else:
            llimit=lims[i][0]/float(NumOmega)*np.pi-np.pi*0.5
            ulimit=(lims[i][1]+1)/float(NumOmega)*np.pi-np.pi*0.5
            co=get_co(PeaksInfo[i],Gs[i],energy)
            co_s.append(co)
            b_s.append([llimit-oPeaks[i][2]/180.0*np.pi,ulimit-oPeaks[i][2]/180.0*np.pi])
            g_s.append(Gs[i])
    co_s=np.array(co_s)
    b_s=np.array(b_s)
    g_s=np.array(g_s)

    As=np.empty((len(g_s)*2,6))
    bs=np.empty(len(g_s)*2)
    j=0
    for i in range(len(g_s)):
        a=co_s[i][0]
        b=co_s[i][1]
        c=co_s[i][2]
        x=g_s[i][0]
        y=g_s[i][1]
        z=g_s[i][2]
        As[j]=[a*x,a*y+b*x,a*z+c*x,b*y,b*z+c*y,c*z]
        bs[j]=b_s[i][1]
        As[j+len(g_s)]=-As[j]
        bs[j+len(g_s)]=-b_s[i][0]
        j+=1
    return As,bs

def get_limit9(NumOmega,oPeaks,PeaksInfo,Gs,lims,energy=71.676):
    """
    for test, only use one L distance
    """
    L=0
    co_s=[]
    b_s=[]
    g_s=[]
    for i in range(len(oPeaks)):
        if lims[i]==None:
            pass
        else:
            llimit=lims[i][0]/float(NumOmega)*np.pi-np.pi*0.5
            ulimit=(lims[i][1]+1)/float(NumOmega)*np.pi-np.pi*0.5
            co=get_co(PeaksInfo[i],Gs[i],energy)
            co_s.append(co)
            b_s.append([llimit-oPeaks[i][2]/180.0*np.pi,ulimit-oPeaks[i][2]/180.0*np.pi])
            g_s.append(Gs[i])
    co_s=np.array(co_s)
    b_s=np.array(b_s)
    g_s=np.array(g_s)

    As=np.empty((len(g_s)*2,9))
    bs=np.empty(len(g_s)*2)
    j=0
    for i in range(len(g_s)):
        a=co_s[i][0]
        b=co_s[i][1]
        c=co_s[i][2]
        x=g_s[i][0]
        y=g_s[i][1]
        z=g_s[i][2]
        As[j]=[a*x,a*y,a*z,b*x,b*y,b*z,c*x,c*y,c*z]
        bs[j]=b_s[i][1]
        As[j+len(g_s)]=-As[j]
        bs[j+len(g_s)]=-b_s[i][0]
        j+=1
    return As,bs

def smart_rand(As,bs,x0,N,l=2e-4):
    d=len(x0)
    res=np.empty((N,d))
    last=x0
    for i in range(len(N)):
        tmp=(np.random.random(d)-0.5)*l+last
        while !np.all(bs>As.dot(tmp)):
            tmp=(np.random.random(d)-0.5)*l+last
        res[i]=tmp
        last=tmp
    return res
