import sys
import socket
import threading
import cv2
import numpy
PORT = 9000


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def handle_clnt(clnt_sock):

    while True:
        sys.stdout.flush()
        clnt_msg = clnt_sock.recv(1024)
        print(clnt_msg.decode())
        if("idcheck" in clnt_msg.decode()):
            sock.send("OK".encode())
        elif("check" == clnt_msg.decode()):
            length = recvall(clnt_sock,6) 
            print(length)
            stringData = recvall(clnt_sock, int(length))
            data = numpy.fromstring(stringData, dtype='uint8')
            decimg=cv2.imdecode(data,1)
            cv2.imshow('SERVER',decimg)
            cv2.waitKey(0)
            cv2.destroyAllWindows() 



if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', PORT))
    sock.listen(5)

    while True:
        clnt_sock, addr = sock.accept()

       
        print(clnt_sock)
        

        t = threading.Thread(target=handle_clnt, args=(clnt_sock,))
        t.start()
