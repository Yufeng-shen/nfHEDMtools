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
