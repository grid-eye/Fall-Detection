import socket
import sys
import numpy as np
import pickle
import time
import threading
from  multiprocessing import Process,Queue ,Event
import os
import cv2 as cv
from countpeople import CountPeople
from examples.show_frame import showframe
from examples.feature_extraction import calFeature
from examples.real_time import main_step
host1 = "192.168.1.100"
show_frame = False
all_frame_sensor_1 = []
if len(sys.argv) > 1:
    port1 = sys.argv[1]
    split_res = sys.argv[1].split(":")
    if len(split_res) == 2:
        host1 = split_res[0]
        port1 = split_res[1]
    port1 = int(port1)
path = "test"
if len(sys.argv) > 2:
    path = sys.argv[2]
if not os.path.exists(path):
    os.mkdir(path)
if len(sys.argv) > 3:
    show_arg = sys.argv[3]
    if show_arg == "show_frame":
        show_frame = True 
class myThread (Process) :
    def __init__(self,host,port,condition,event):
        Process.__init__(self)
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.con = condition
        self.quit = False
        self.counter = 0
        self.last_cnt = 0 
        self.queue = Queue(2)
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((self.host,self.port))
        self.event = event
    def setQuitFlag(self,flag):
        self.quit = True
    def getQuitFlag(self):
        return self.quit
    def run(self):
        print("start process")
        self.event.wait()
        self.socket.send("start".encode("utf-8"))
        try:
            while True:
                #if len(self.container) == 0:
                #    self.condition.wait()
                recv = self.socket.recv(1024)
                recv = pickle.loads(recv)
                self.counter += 1
                #print("==========the %dth frame========"%(self.counter))
                #print(recv)
                self.queue.put(recv)
                self.socket.send("ok".encode("utf-8"))
                '''
                self.con.acquire()
                self.container.append(recv)
                self.counter += 1
                self.con.notify()
                self.con.release()
                '''
                #self.condition.notify()
                #self.condition.wait(3)
                #self.condition.release()
        except KeyboardInterrupt:
            print("keyboardinterrupt ..........")
            self.setQuitFlag = True
    def getNextFrame(self):
        return self.queue.get() 
        '''
        if self.con.acquire():
            while self.last_cnt >=  self.counter:
                self.con.wait()
            index = self.last_cnt
            self.last_cnt += 1
            self.con.release()
            return self.container[index]
        '''
    def close(self):
        self.socket.close()
lock = threading.Lock()#互斥锁
con = threading.Condition()#为了轮流读取两个服务器的数据,不需要互斥锁了
event = Event()
print(" is start receive sensor data ? ",end = ":")
print(event.is_set())
mythread1 = myThread(host1,port1,con,event)
mythread1.start()
event.set()
print(" is start receive sensor data ? ",end = ":")
def showData(data):
    for item in data:
        print(np.array(item))
    print("================")

i = 0 
thresh = 40
def saveImageData(sensor1,path,avgtemp):
    np.save(path+"/imagedata.npy",np.array(sensor1))
    np.save(path+"/avgtemp.npy",avgtemp)
all_merge_frame = []
cp = CountPeople()
i = 0 
container = []
#实时检测的数据收集
realtime_frame = []
realtime_counter = 0
initial_avg  = None
try:
    while True:
        if mythread1.getQuitFlag() :
            break
        i += 1
        print(" the %dth frame "%(i))
        print("============wait=============")
        s1 = mythread1.getNextFrame()
        time_1 = s1[1]
        s1 = s1[0]
        all_frame_sensor_1.append(s1)
        print("=============show ===========")
        print("=============time is ==============")
        print(time_1)
        time_local_1 = time.localtime(int(time_1))
        dt1 = time.strftime("%Y-%m-%d:%H:%M:%S",time_local_1)
        print(dt1)
        showData([s1])
        current_frame = s1#合并两个传感器的数据,取最大值
        container.append(s1)
        if len(container) == 4:
            last_three_frame = container.pop(0)
        if show_frame:
            showframe(current_frame)
        realtime_frame.append(current_frame)
        #滑动窗口为60帧，每滑动10帧检测一次
        if len(realtime_frame) < 50:
            pass
        else:
            realtime_counter += 1
            if realtime_counter == 10:
                max_moving_frame = 0
                max_variance = 0.0
                max_therhold_pixel_num = 0
                max_R = 0.0
                temp_frame = np.array(realtime_frame)
                max_moving_frame, max_variance, max_therhold_pixel_num, max_R = calFeature(temp_frame, max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
                if max_moving_frame != max_variance:
                    feature = np.array([max_moving_frame,max_variance,max_therhold_pixel_num,max_R])
                    is_fall = main_step(r"examples/test.csv",feature)
                    if is_fall:
                        print(max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
                        print("检测到跌倒状况")
                        print(len(realtime_frame))
                        time.sleep(5)
                    realtime_frame = []
                else:
                    realtime_frame = realtime_frame[10:]
                realtime_counter = 0


        if mythread1.getQuitFlag() :
            break
        if i >= thresh:
            saveImageData(all_frame_sensor_1,path,initial_avg)
            thresh += 500 
except KeyboardInterrupt:
    print("==========sensor catch keyboardinterrupt==========")
    saveImageData(all_frame_sensor_1,path,initial_avg)
finally:
    saveImageData(all_frame_sensor_1,path,initial_avg)
    mythread1.setQuitFlag(True)
    mythread1.close()
print(" exit sucessfully!")

