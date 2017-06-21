import numpy as np
from IntBin import ReadI9BinaryFiles
from scipy import sparse

class ExpImage:
    def __init__(self,NumOmega,NumDet,FilePrefix):
        self.NumOmega=NumOmega
        self.NumDet=NumDet
        self.images=[]
        self.read(FilePrefix)
    def read(self,FilePrefix):
        self.images=[]
        for i in range(self.NumOmega):
            tmpOmega=[]
            for j in range(self.NumDet):
                tmp=ReadI9BinaryFiles(FilePrefix+"{0:06d}.bin{1:d}".format(i,j))
                tmpL=sparse.csr_matrix((tmp[2],(tmp[0],tmp[1])),shape=(2048,2048))
                tmpOmega.append(tmpL)
            self.images.append(tmpOmega)
    def IsBright(self,omega,L,J,K):
        if self.images[omega][L][J,K]>=1:
            return True
        else:
            return False

class SimImage:
    def __init__(self,NumOmega,NumDet):
        self.NumOmega=NumOmega
        self.NumDet=NumDet
        self.images=[]
        for tomega in range(NumOmega):
            tmpOmega=[]
            for tdet in range(NumDet):
                tmpOmega.append([])
            self.images.append(tmpOmega)
    def AddHit(self,pixels,omega,det):
        self.images[omega][det].extend(pixels)
    def MakeSet(self):
        for tomega in range(self.NumOmega):
            for tdet in range(self.NumDet):
                self.images[tomega][tdet]=set( self.images[tomega][tdet])
    def IsBright(self,omega,L,J,K):
        if tuple((J,K)) in self.images[omega][L]:
            return True
        else:
            return False
