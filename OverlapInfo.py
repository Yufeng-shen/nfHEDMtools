import numpy as np

def NaiveCostFn(oExpImage,oPeaks,n):
    """
    for test, only use one L distance
    """
    L=n
    NumOmega=oExpImage.NumOmega
    NumOverlap=0
    for i in range(len(oPeaks)):
        omega=int((oPeaks[i][2]+90)*NumOmega/180)
        J=int(oPeaks[i][0])
        K=int(oPeaks[i][1])
        if oExpImage.IsBright(omega,L,J,K):
            NumOverlap+=1
    return NumOverlap/float(len(oPeaks))
