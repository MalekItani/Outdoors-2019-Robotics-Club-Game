import socket
import time
import requests

host = 'http://192.168.4.2'
pc = host + '/pc'
store = host + '/store'
port = 80

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


def main():
    esp = socket.socket()
    esp.connect((host, 80))
    msg = esp.recv(10)
    print(msg)
    esp.send(b'C')  # Tell esp that you are the computer
    time.sleep(0.5)
    esp.close()



if __name__ == "__main__":
    # main()
    req()