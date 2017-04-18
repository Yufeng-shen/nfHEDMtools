import matplotlib.pyplot as plt
import numpy as np
from math import atan2

def Q2Mat(q0,q1,q2,q3):
    """
    convert quarternion to active matrix
    """
    m=np.matrix([[1-2*q2**2-2*q3**2,2*q1*q2+2*q0*q3,2*q1*q3-2*q0*q2],[2*q1*q2-2*q0*q3,1-2*q1**2-2*q3**2,2*q2*q3+2*q0*q1],[2*q1*q3+2*q0*q2,2*q2*q3-2*q0*q1,1-2*q1**2-2*q2**2]])
    return m.T

def Euler2Mat(e):
    """
    Euler Angle (radian)  in ZYZ convention to active rotation matrix, which means newV=M*oldV
    """
    x=e[0]
    y=e[1]
    z=e[2]
    s1=np.sin(x)
    s2=np.sin(y)
    s3=np.sin(z)
    c1=np.cos(x)
    c2=np.cos(y)
    c3=np.cos(z)
    m=np.array([[c1*c2*c3-s1*s3,-c3*s1-c1*c2*s3,c1*s2],
        [c1*s3+c2*c3*s1,c1*c3-c2*s1*s3,s1*s2],
        [-c3*s2,s2*s3,c2]])
    return m

def EulerZXZ2Mat(e):
    """
    Euler Angle (radian)  in ZXZ convention to active rotation matrix, which means newV=M*oldV
    """
    x=e[0]
    y=e[1]
    z=e[2]
    s1=np.sin(x)
    s2=np.sin(y)
    s3=np.sin(z)
    c1=np.cos(x)
    c2=np.cos(y)
    c3=np.cos(z)
    m=np.array([[c1*c3-c2*s1*s3,-c1*s3-c3*c2*s1,s1*s2],
        [s1*c3+c2*c1*s3,c1*c2*c3-s1*s3,-c1*s2],
        [s3*s2,s2*c3,c2]])
    return m

def GetSymRotMat(symtype='Cubic'):
    """
    return an array of active rotation matrices of the input crystal symmetry

    Parameters
    ----------
    symtype: string
            Symmetry type of crystal. For now only 'Cubic' and 'Hexagonal' are implemented. 

    Returns
    ----------
    m:  ndarray
        A three dimensional numpy array, which has the shape (n,3,3). 
    """
    if symtype == 'Cubic':
        m=np.zeros((24,3,3))
        m[0][0,1]=1
        m[0][1,0]=-1
        m[0][2,2]=1

        m[1][0,0]=-1
        m[1][1,1]=-1
        m[1][2,2]=1

        m[2][0,1]=-1
        m[2][1,0]=1
        m[2][2,2]=1

        m[3][0,2]=-1
        m[3][1,1]=1
        m[3][2,0]=1

        m[4][0,0]=-1
        m[4][1,1]=1
        m[4][2,2]=-1

        m[5][0,2]=1
        m[5][1,1]=1
        m[5][2,0]=-1

        m[6][0,0]=1
        m[6][1,2]=1
        m[6][2,1]=-1

        m[7][0,0]=1
        m[7][1,1]=-1
        m[7][2,2]=-1

        m[8][0,0]=1
        m[8][1,2]=-1
        m[8][2,1]=1

        m[9][0,1]=1
        m[9][1,2]=1
        m[9][2,0]=1

        m[10][0,2]=1
        m[10][1,0]=1
        m[10][2,1]=1

        m[11][0,2]=-1
        m[11][1,0]=1
        m[11][2,1]=-1

        m[12][0,1]=1
        m[12][1,2]=-1
        m[12][2,0]=-1

        m[13][0,2]=1
        m[13][1,0]=-1
        m[13][2,1]=-1

        m[14][0,1]=-1
        m[14][1,2]=-1
        m[14][2,0]=1

        m[15][0,2]=-1
        m[15][1,0]=-1
        m[15][2,1]=1

        m[16][0,1]=-1
        m[16][1,2]=1
        m[16][2,0]=-1

        m[17][0,0]=-1
        m[17][1,2]=1
        m[17][2,1]=1

        m[18][0,2]=1
        m[18][1,1]=-1
        m[18][2,0]=1

        m[19][0,1]=1
        m[19][1,0]=1
        m[19][2,2]=-1

        m[20][0,0]=-1
        m[20][1,2]=-1
        m[20][2,1]=-1

        m[21][0,2]=-1
        m[21][1,1]=-1
        m[21][2,0]=-1

        m[22][0,1]=-1
        m[22][1,0]=-1
        m[22][2,2]=-1

        m[23][0,0]=1
        m[23][1,1]=1
        m[23][2,2]=1
        
        return m
    elif symtype == 'Hexagonal':
        m=np.zeros((12,3,3))
        m[0][0,0]=0.5
        m[0][1,1]=0.5
        m[0][2,2]=1
        m[0][0,1]=-np.sqrt(3)*0.5
        m[0][1,0]=np.sqrt(3)*0.5

        m[1]=m[0].dot(m[0])
        m[2]=m[1].dot(m[0])
        m[3]=m[2].dot(m[0])
        m[4]=m[3].dot(m[0])
        m[5]=np.eye(3)

        m[6][0,0]=1
        m[6][1,1]=-1
        m[6][2,2]=-1

        m[7]=m[0].dot(m[6])
        m[8]=m[1].dot(m[6])
        m[9]=m[2].dot(m[6])
        m[10]=m[3].dot(m[6])
        m[11]=m[4].dot(m[6])

        return m
    else:
        print "not implemented yet"
        return 0

def Orien2FZ(m,symtype='Cubic'):
    """
    Reduce orientation to fundamental zone, input and output are both active matrices
    Careful, it is m*op not op*m

    Parameters
    -----------
    m:      ndarray
            Matrix representation of orientation
    symtype:string
            The crystal symmetry

    Returns
    -----------
    oRes:   ndarray
            The rotation matrix after reduced. Note that this function doesn't actually
            reduce the orientation to fundamental zone, only make sure the angle is the 
            smallest one, so there are multiple orientations have the same angle but
            different directions. oRes is only one of them.
    angle:  scalar
            The reduced angle.
    """
    ops=GetSymRotMat(symtype)
    angle=6.3
    for op in ops:
        tmp=m.dot(op)
        cosangle=0.5*(tmp.trace()-1)
        cosangle=min(0.9999999,cosangle)
        cosangle=max(-0.9999999,cosangle)
        newangle=np.arccos(cosangle)
        if newangle<angle:
            angle=newangle
            oRes=tmp
    return oRes,angle

#def plane2FZ(v,symtype='Cubic'):
#    V=v.reshape((3,1))
#    if symtype=='Cubic':
#        ops=GetSymRotMat(symtype)
#        for op in ops:
#            oRes=op.dot(V)
#            if oRes[0]>oRes[1] and oRes[0]>oRes[2] and oRes[1]>0 and oRes[2]>0:
#                break
#        return oRes

def Misorien2FZ1(m1,m2,symtype='Cubic'):
    """
    Careful, it is m1*op*m2T, the order matters. Only returns the angle, doesn't calculate the right axis direction

    Parameters
    -----------
    m1:     ndarray
            Matrix representation of orientation1
    m2:     ndarray
            Matrix representation of orientation2
    symtype:string
            The crystal symmetry

    Returns
    -----------
    oRes:   ndarray
            The misorientation matrix after reduced. Note that this function doesn't actually
            reduce the orientation to fundamental zone, only make sure the angle is the 
            smallest one, so there are multiple orientations have the same angle but
            different directions. oRes is only one of them.
    angle:  scalar
            The misorientation angle.
    """
    m2=np.matrix(m2)
    ops=GetSymRotMat(symtype)
    angle=6.3
    for op in ops:
        tmp=m1.dot(op.dot(m2.T))
        cosangle=0.5*(tmp.trace()-1)
        cosangle=min(0.9999999999,cosangle)
        cosangle=max(-0.99999999999,cosangle)
        newangle=np.arccos(cosangle)
        if newangle<angle:
            angle=newangle
            oRes=tmp
    return oRes,angle

#def Misorien2FZ3(m1,m2,symtype='Cubic'):
#    m1=np.matrix(m1)
#    dm=(m1.T).dot(m2)
#    oRes,angle=Orien2FZ(dm,symtype)
#    return oRes,angle
#
#def Misorien2FZ2(m1,m2,symtype='Cubic'):
#    m2=np.matrix(m2)
#    dm=m1.dot(m2.T)
#    ops=GetSymRotMat(symtype)
#    angle=6.3
#    for op1 in ops:
#        for op2 in ops:
#            tmp=op1.dot(dm.dot(op2))
#            cosangle=0.5*(tmp.trace()-1)
#            cosangle=min(0.9999999,cosangle)
#            cosangle=max(-0.9999999,cosangle)
#            newangle=np.arccos(cosangle)
#            if newangle<angle:
#                angle=newangle
#                oRes=tmp
#    return oRes,angle
#

def Mat2Euler(m):
    """
    transform active rotation matrix to euler angles in ZYZ convention
    """
    threshold=0.9999999
    if m[2,2]>threshold:
        x=0
        y=0
        z=atan2(m[1,0],m[0,0])
    elif m[2,2]< -threshold:
        x=0
        y=np.pi
        z=atan2(m[0,1],m[0,0])
    else:
        x=atan2(m[1,2],m[0,2])
        y=atan2(np.sqrt(m[2,0]**2+m[2,1]**2),m[2,2])
#        y=np.arccos(m[2,2])
        z=atan2(m[2,1],-m[2,0])
#    if np.sin(x)*m[1,2]<0 or np.cos(x)*m[0,2]<0 : x=x+np.pi
#    if np.sin(z)*m[2,1]<0 or np.cos(z)*m[2,0]>0 : z=z+np.pi
    if x<0: x=x+2*np.pi
    if y<0: y=y+2*np.pi
    if z<0: z=z+2*np.pi
    return x,y,z

def Mat2EulerZXZ(m):
    """
    transform active rotation matrix to euler angles in ZXZ convention, not right
    """
    threshold=0.9999999
    if m[2,2]>threshold:
        x=0
        y=0
        z=atan2(m[1,0],m[0,0])
    elif m[2,2]< -threshold:
        x=0
        y=np.pi
        z=atan2(m[0,1],m[0,0])
    else:
        x=atan2(m[0,2],-m[1,2])
        y=atan2(np.sqrt(m[2,0]**2+m[2,1]**2),m[2,2])
        z=atan2(m[2,0],m[2,1])
    if x<0: x=x+2*np.pi
    if y<0: y=y+2*np.pi
    if z<0: z=z+2*np.pi
    return x,y,z

#def plot(m,symtype='Cubic'):
#    ops=GetSymRotMat(symtype)
#    for op in ops:
#        tmp=op.dot(m)
#        x,y,z=Mat2Euler(tmp)
#        plt.scatter(x,y+z)
#    plt.show()
#def plot2(m,symtype='Cubic'):
#    ops=GetSymRotMat(symtype)
#    for op1 in ops:
#        for op2 in ops:
#            tmp=op1.dot(m.dot(op2))
#            x,y,z=Mat2Euler(tmp)
#            plt.scatter(x,y+z)
#    plt.show()
