import socket
import numpy as np
import struct
import matplotlib.pyplot as plt

import Simulation as G
import RotRep as R

class myProtocol(object):
    @classmethod
    def send_msg(cls,sock,msg):
        msg=struct.pack('>I',len(msg))+msg
        sock.sendall(msg)
    @classmethod
    def recv_msg(cls,sock):
        raw_msglen=cls.recvall(sock,4)
        if not raw_msglen:
            return None
        msglen=struct.unpack('>I',raw_msglen)[0]
        return cls.recvall(sock,msglen)
    @classmethod
    def recvall(cls,sock,n):
        data=[]
        bytes_recd=0
        while bytes_recd<n:
            packet=sock.recv(n-bytes_recd)
            if not packet:
                raise RuntimeError("receive failed, socket connection broken")
            data.append(packet)
            bytes_recd+=len(packet)
        return ''.join(data)

class XRD(object):
    def __init__(self):
        self._sample=G.CrystalStr('Ti7')
        self._sample.getRecipVec()
        self._sample.getGs(11)
        self._Peaks=None
        self._Gs=None
        self._PeaksInfo=None
    def Setup(self,energy,etalimit,pos,orien,Det):
        self._exp={'energy':energy}
        self._etalimit=etalimit
        self._pos=pos
        self._orien=orien
        self._Det=Det
    def ChangeVoxel(self,pos,orien):
        self._pos=pos
        self._orien=orien
    def Simulate(self):
        self._Peaks,self._Gs,self._PeaksInfo = G.GetProjectedVertex(self._Det,self._sample,
                self._orien,self._etalimit,self._pos,getPeaksInfo=True,omegaL=0,omegaU=180,**self._exp)
    @property
    def Peaks(self):
        return self._Peaks
    @property
    def Gs(self):
        return self._Gs

class socketclient():
    def __init__(self,host='localhost',port=9527):
        HOST,PORT=host,port
        #SOCK_STREAM == a TCP socket
        self._sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        #sock.setblocking(0) #optional non-blocking
        self._sock.connect((HOST,PORT))
    def GetImg(self,omegid,y1,y2,x1,x2):
        myProtocol.send_msg(self._sock,'GetImg')
        myProtocol.send_msg(self._sock,struct.pack('>IIIII',omegid,y1,y2,x1,x2))
        photo=np.fromstring(myProtocol.recv_msg(self._sock),dtype=np.uint16).reshape((y2-y1,x2-x1))
        return photo
    def Done(self):
        myProtocol.send_msg(self._sock,'Done')
        self._sock.close()



