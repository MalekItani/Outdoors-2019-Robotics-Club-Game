import socket
from _pickle import loads, dumps
import cv2
import struct


class _OpenCVSocketBase:
    def __init__(self, host, port):
        self.port = port
        self.host = host
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def sendData(self, data):
        data = dumps(data)
        self.Socket.send(data)

    def receiveData(self):
        data = self.Socket.recv(1024)
        return loads(data)
    
    def close(self):
        self.Socket.close()


class OpenCVServerSocket(_OpenCVSocketBase):
    def __init__(self, port, chunkSize=4096, numClients=1):
        _OpenCVSocketBase.__init__(self, '', port)
        self.cs = chunkSize
        self.Socket.bind((self.host, self.port))
        self.Socket.listen(numClients)
        self.clientConn, self.clientAddr = self.Socket.accept()

    def receiveFrame(self, mode=cv2.IMREAD_COLOR):
        data = b""
        payload_size = struct.calcsize(">L")
        while len(data) < payload_size:
            data += self.clientConn.recv(self.cs)
            imgSize = struct.unpack('>L', data[:payload_size])[0]
            data = data[payload_size:]
            while len(data) < imgSize:
                data += self.clientConn.recv(self.cs)
        frame_data = data[:imgSize]
        frame = loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, mode)
        self.clientConn.send('1'.encode())
        return frame

    def sendData(self, data):
        data = dumps(data)
        self.clientConn.send(data)


class OpenCVClientSocket(_OpenCVSocketBase):
    def __init__(self, host, port):
        _OpenCVSocketBase.__init__(self, host, port)
        self.Socket.connect((self.host, self.port))

    def sendFrame(self, frame, tries=0):
        result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        payload = dumps(frame)
        size = len(payload)
        self.Socket.send(struct.pack('>L', size) + payload)
        if self.Socket.recv(1).decode() != '1' and tries < 3:
            self.sendFrame(frame, tries+1)

    def receiveData(self):
        data = self.Socket.recv(1024)
        return loads(data)
