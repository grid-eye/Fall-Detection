import time
import numpy as np
import pickle
import busio
import board
import adafruit_amg88xx
import socket
import threading
import sys
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = ""
port = 9998
if len(sys.argv) > 1:
    port = int(sys.argv[1])
print("port is %d "%(port))
addr = (host,port)
hostname = socket.gethostname()
ip = get_host_ip()
try:
    serverSocket.bind(addr)
    print("bind the addr %s , %d "%(host,port))
    print("===============ip is =========")
    print(ip)
    serverSocket.listen(2)
    print("listenning...")
    i2c = busio.I2C(board.SCL, board.SDA)
    amg = adafruit_amg88xx.AMG88XX(i2c,0x69)
    class MyThread(threading.Thread):
        def __init__(self,threadID,name,q):
            threading.Thread.__init__(self)
            self.threadID = threadID
            self.name = name
            self.q = q 
        def run(self):
            print("start thread : "+self.name)
            self.process_data()
        def process_data(self):
            pass

    while True:
        clientSocket,addr = serverSocket.accept()
        print(addr)
        i = 0 
        try:
            rec = clientSocket.recv(30)
            msg = rec.decode("utf-8")
            print(msg) 
            while True:
                temp = [] 
                for row in amg.pixels:
                    # Pad to 1 decimal place
                    temp.append(row)
                t = time.time()
                i += 1
                print(t)
                print(" the %dth frame "%(i))
                temp = np.array(temp)
                temp = (temp,round(t,3))
                serial_temp = pickle.dumps(temp)
                clientSocket.send(serial_temp)
                rec = clientSocket.recv(30)
                msg = rec.decode("utf-8")
                temp = []
        except (BrokenPipeError,ConnectionResetError):
            print("BrokenPipeError or connectionResetError")
        except KeyboardInterrupt:
            print("error ............ ")
            break
        finally:
            print("bind the addr %s , %d "%(host,port))
            print("listenning...")
finally:
    clientSocket.close()
    serverSocket.close()
