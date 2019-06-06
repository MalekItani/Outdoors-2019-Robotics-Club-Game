import socket
import time
import requests
from _pickle import loads


host = 'http://192.168.4.2'
pc = host + '/pc'
store = host + '/store'
req_data = host + '/request_data'
kill = host + '/death'
port = 80


def notify_death():
    resp = requests.get(kill)
    while resp.status_code != 200:
        resp = requests.get(kill)
    print('K')

def send_ip():
    resp = requests.get(store)
    while resp.status_code != 200:
        resp = requests.get(store)

def get_pc_ip():
    resp = requests.get(pc)
    while resp.status_code != 200:
        resp = requests.get(pc)
    return resp.text


def req():
    send_ip()
    ip = get_pc_ip()
    print(ip)


def request_pos():
    resp = requests.get(req_data)
    while resp.status_code != 200:
        resp = requests.get(req_data)
    return resp.text


def main():
    esp = socket.socket()
    esp.connect((host, 80))
    msg = esp.recv(10)
    print(msg)
    esp.send(b'C')  # Tell esp that you are the computer
    time.sleep(0.5)
    esp.close()


def connect():
    host = ''
    port = 12345
    sk = socket.socket()
    sk.bind((host, port))
    sk.listen(1)
    pi, addr = sk.accept()
    return pi


def receive_pos(sock):
    try:
        cntr = sock.recv(512)
        return loads(cntr)
    except:
        pass


if __name__ == "__main__":
    # main()
    # req()
    send_ip()
    pi = connect()
    for i in range(100):
        receive_pos(pi)
    pi.close()