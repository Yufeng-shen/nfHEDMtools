import SocketServer
import socket
import time
import numpy as np
import struct
import matplotlib.pyplot as plt

def RawImgFile(omgid):
    return '/home/fyshen13/Mar17Raw/Ti7_S0_{0:06d}.tif'.format(omgid+26496)

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



class XRDHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "peername:",self.request.getpeername()
        try:
            while True:
                comm=myProtocol.recv_msg(self.request)
                if comm=='GetImg':
                    omegid,y1,y2,x1,x2=struct.unpack('>IIIII',myProtocol.recv_msg(self.request))
                    I=plt.imread(RawImgFile(omegid))
                    msg=I[y1:y2,x1:x2].tostring()
                    myProtocol.send_msg(self.request,msg)
                elif comm=='Done':
                    print "disconnected"
                    break
        except RuntimeError:
            print 'Error catched'
            self.request.close()


if __name__=="__main__":
    serv = SocketServer.TCPServer(("",9527),XRDHandler)
    print serv.server_address
    serv.serve_forever()
