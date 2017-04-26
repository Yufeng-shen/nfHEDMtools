import numpy as np

def GenAll(leftx,lefty,minlen,N1,N2,Ngen):
    """
    generate a large diamond area of triangle mesh
    leftx: the x coordinate of left most point
    lefty: the y coordinate of left most point
    minlen: the sidewidth of finest triangles
    N1: the number of cells in horizontal direction
    N2: the number of cells in the other direction
    Ngen: number of generation, just for output
    """
    Grid=np.empty((N1,N2,2))
    Grid[0,0,0]=leftx
    Grid[0,0,1]=lefty
    minhight=minlen*0.5*3**0.5
    ores=[]
    for i in range(N1):
        for j in range(N2):
            tmp=np.zeros(10)
            tmp[4]=Ngen
            tmp[5]=1
            if i!=0:
                Grid[i,j,0]=Grid[i-1,j,0]+minlen
                Grid[i,j,1]=Grid[i-1,j,1]
            elif j!=0:
                Grid[i,j,1]=Grid[i,j-1,1]+minhight
                Grid[i,j,0]=Grid[i,j-1,0]+minlen*0.5
            tmp[0]=Grid[i,j,0]
            tmp[1]=Grid[i,j,1]
            if j!=N2-1:
                tmp[3]=1
                ores.append(tmp.copy())
            if j!=0:
                tmp[3]=2
                ores.append(tmp.copy())
    return ores

def Crop(meshall,f):
    """
    crop the large area mesh to smaller one
    meshall: input mesh, it's a list
    f: criteria function, input x and y, returns True or False
    """
    todel=[]
    for i in range(len(meshall)):
        if not f(meshall[i][0],meshall[i][1]):
            todel.append(i)
    meshall=np.array(meshall)
    newmesh=np.delete(meshall,todel,axis=0)
    return newmesh

def SimpleCut(x,y,a,b,c,d):
    if x>a and x<b and y>c and y<d:
        return True
    else:
        return False

def MicOut(mesh,initlen):
    newmesh=np.array(mesh)
    np.savetxt('try.mic',mesh,fmt=['%.6f','%.6f']+['%d']*8,delimiter='\t',header=str(initlen),comments='')
    return

def main(leftx,lefty,minlen,N1,N2,Ngen,a,b,c,d):
    mesh=GenAll(leftx,lefty,minlen,N1,N2,Ngen)
    newmesh=Crop(mesh,lambda x,y:SimpleCut(x,y,a,b,c,d))
    MicOut(newmesh,minlen*2**Ngen)
    return
