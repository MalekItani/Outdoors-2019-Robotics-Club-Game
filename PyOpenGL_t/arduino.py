import serial
import time
import bluetooth


class Handheld():
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        self.serial = serial.Serial(port=port, baudrate=baudrate)

    def get_rotation(self):
        while not self.serial.in_waiting:
            pass
        if self.serial.in_waiting:
            time.sleep(0.001)
            x = self.serial.readline().decode().replace('\r', '').rstrip().split(',')
            if '' in x:
                x.remove('')
            try:
                a = [float(i) for i in x]
                return a
            except ValueError:
                return []
            return x
        return []

    def get_quaternion(self):
        while not self.serial.in_waiting:
            pass
        if self.serial.in_waiting:
            time.sleep(0.001)
            x = self.serial.readline().decode().replace('\r', '').rstrip().split(',')
            if '' in x:
                x.remove('')
            try:
                a = [float(i) for i in x]
                return a
            except ValueError:
                return []
            return x
        return []

    def close_connection(self):
        self.serial.close()


def hh_test():
    h = Handheld(baudrate=9600, port='/dev/rfcomm0')
    time.sleep(1)
    while 1:
        x = h.get_rotation()
        print(x)
    h.close_connection()

def bhh_test():
    bd_addr = "00:21:13:02:A6:A0"
    port = 1
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((bd_addr, port))
    print('Connected')
    while(1):
        print(sock.recv(1024))


if __name__ == "__main__":
    hh_test()
    # bhh_test()