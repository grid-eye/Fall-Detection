import socket
import sys
import numpy as np
import pickle
import time
import threading
from  multiprocessing import Process,Queue ,Event
import os
import cv2 as cv
from show_frame import showframe
host1 = "192.168.1.100"
host2 = "192.168.1.211"
port1 = 9999
show_frame = False
port2 = port1
all_frame_sensor_1 = []
all_frame_sensor_2 = []
if len(sys.argv) > 1:
    port1 = sys.argv[1]
    split_res = sys.argv[1].split(":")
    if len(split_res) == 2:
        host1 = split_res[0]
        port1 = split_res[1]
        host2 = host1
    port1 = int(port1)
    port2 = port1
    if len(sys.argv) > 2:
        port2 = sys.argv[2]
        split_res = sys.argv[2].split(":")
        if len(split_res) == 2:
            host2 = split_res[0]
            port2 = split_res[1]
        port2 = int(port2)
path = "double_sensor"
if len(sys.argv) > 3:
    path = sys.argv[3]
if not os.path.exists(path):
    os.mkdir(path)
if len(sys.argv) > 4:
    show_arg = sys.argv[4]
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
        print("host2==========")
        print(host2)
        print("port2==========")
        print(port2)
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
                self.socket.send("1".encode("utf-8"))
                #self.condition.notify()
                #self.condition.wait(3)
                #self.condition.release()
        except KeyboardInterrupt:
            print("keyboardinterrupt ..........")
            self.setQuitFlag = True
    def getNextFrame(self):
        return self.queue.get() 
    def close(self):
        self.socket.close()
lock = threading.Lock()#互斥锁
con = threading.Condition()#为了轮流读取两个服务器的数据,不需要互斥锁了
event = Event()
print(" is start receive sensor data ? ",end = ":")
print(event.is_set())
mythread1 = myThread(host1,port1,con,event)
mythread2 = myThread(host2,port2,con,event)
mythread1.start()
mythread2.start()
event.set()
print(" is start receive sensor data ? ",end = ":")
def showData(data):
    for item in data:
        print(np.array(item))
    print("================")

i = 0 
thresh = 80#用于计算背景的帧数
diff_time_thresh = 20
def saveImageData(sensor1,sensor2,path):
    np.save(path+"/sensor1.npy",np.array(sensor1))
    np.save(path+"/sensor2.npy",np.array(sensor2))
def mergeData(t1,t2):
    temp = np.zeros(t1.shape)
    print(" t1 shape is")
    print(t1.shape)
    for i in range(t1.shape[0]):
        for j in range(t1.shape[1]):
            temp[i][j] = max(t1[i][j],t2[i][j])
    return temp
def isSynchronize(t1,t2,thresh):
    if abs(t1 - t2 ) > thresh:
        return False
    return True
def split_frame(s1, s2):
    """    
    avgCal_1 = np.mean(s1)
    diff_1 = np.array([x - avgCal_1 for x in s1])
    plot_img_1 = np.zeros(s1.shape,np.uint8)
    plot_img_1[np.where(diff_1 > 1.5) ] = 255
    
    avgCal_2 = np.mean(s2)
    diff_2 = np.array([x - avgCal_2 for x in s2])
    plot_img_2 = np.zeros(s2.shape,np.uint8)
    plot_img_2[np.where(diff_2 > 1.5) ] = 255
    """
    n1 = np.array(s1)
    n2 = np.array(s2)
    return np.hstack((n1[:,4:8],n2[:,0:4]))
 
all_merge_frame = []
i = 0 
container = []
time_thresh = 0.06
diff_sum = 0 
toggle = False
align = True#两帧数据时间线是否对齐，即同步
#实时检测的数据收集
realtime_frame_1 = []
realtime_frame_2 = []
realtime_frame_3 = []
realtime_counter = 0


try:
    while True:
        if mythread1.getQuitFlag() or mythread2.getQuitFlag():
            break
        i += 1
        print(" the %dth frame "%(i))
        print("============wait=============")
        s1 = mythread1.getNextFrame()
        s2 = mythread2.getNextFrame()
        print(s1)
        print(s2)
        t1 = s1[1]
        t2 = s2[1]
        diff = t1 - t2
        if diff > 0:
            toggle = True#sensor1快
        else:
            toggle = False#sensor2快
        s1= s1[0]
        s2 = s2[0]
        if i < diff_time_thresh:
            diff_sum += abs(diff)
        elif i == diff_time_thresh:
            complement = diff_sum / i#计算两个传感器的传送的数据的时间的原始差值,这个差值作为补偿值
            print("======complement is %.3f "%(complement))
            time_thresh += complement #判断两个传感器数据是否同步的阈值
            print("======synchronize's thresh is %.3f "%(time_thresh))
        isSync = isSynchronize(t1,t2,time_thresh)
        count = 0
        while_count = 2
        while not isSync and count < while_count:#同步措施
            if not toggle:#sensor2 快
                s1 = mythread1.getNextFrame()
                t1 = s1[1]
                s1 = s1[0]  
            else:
                s2 = mythread2.getNextFrame()#sensor1快
                t2 = s2[1]
                s2 = s2[0]
            diff = t1 - t2 
            if diff >0 :
                toggle = True
            else:
                toggle = False
            isSync = isSynchronize(t1,t2,time_thresh)
            count += 1
        print(t1,t2)
        all_frame_sensor_1.append(s1)
        all_frame_sensor_2.append(s2)
        print("=============show ===========")
        showData([s1,s2])
        current_frame_sensor1 = s1
        current_frame_sensor2 = s2
        current_frame_sensor3 = split_frame(s1,s2)
        if show_frame:
            showframe(current_frame_sensor1, "sensor1")
            showframe(current_frame_sensor2, "sensor2")
            showframe(current_frame_sensor3, "sensor3")
        realtime_frame_1.append(current_frame_sensor1)
        realtime_frame_2.append(current_frame_sensor2)
        realtime_frame_3.append(current_frame_sensor3)

        #滑动窗口为60帧，每滑动10帧检测一次
        if len(realtime_frame_1) < 50:
            pass
        else:
            realtime_counter += 1
            if realtime_counter == 10:
                max_moving_frame = 0
                max_variance = 0.0
                max_therhold_pixel_num = 0
                max_R = 0.0
                temp_frame_1 = np.array(realtime_frame_1)
                temp_frame_2 = np.array(realtime_frame_2)
                temp_frame_3 = np.array(realtime_frame_3)

                max_moving_frame_1, max_variance_1, max_therhold_pixel_num_1, max_R_1 = calFeature(temp_frame_1)
                max_moving_frame_2, max_variance_2, max_therhold_pixel_num_2, max_R_2 = calFeature(temp_frame_2)
                max_moving_frame_3, max_variance_3, max_therhold_pixel_num_3, max_R_3 = calFeature(temp_frame_3)
                
                
                #判断是否跌倒
                if max_moving_frame_1 != 0 and max_moving_frame_2 != 0:
                    feature_1 = np.array([max_moving_frame_1,max_variance_1,max_therhold_pixel_num_1,max_R_1])
                    is_fall_1 = main_step(r"test.csv",feature_1)
   
                    feature_2 = np.array([max_moving_frame_2,max_variance_2,max_therhold_pixel_num_2,max_R_2])
                    is_fall_2 = main_step(r"test.csv",feature_2)

                    feature_3 = np.array([max_moving_frame_3,max_variance_3,max_therhold_pixel_num_3,max_R_3])
                    is_fall_3 = main_step(r"test.csv",feature_3)
                    
                    if is_fall_3:
                        print("检测到跌倒状况")
                        time.sleep(5)
                    else:
                        if is_fall_1 ^ is_fall_2:
                            print("检测到跌倒状况")
                            time.sleep(5)

                elif max_moving_frame_1 != 0 and max_moving_frame_2 == 0:
                    feature = np.array([max_moving_frame_1,max_variance_1,max_therhold_pixel_num_1,max_R_1])
                    is_fall = main_step(r"test.csv",feature)
                    if is_fall:
                        print(max_moving_frame_1, max_variance_1, max_therhold_pixel_num_1, max_R_1)
                        print("检测到跌倒状况")
                        time.sleep(5)
                    realtime_frame_1 = []
                    realtime_frame_2 = []
                    realtime_frame_3 = []

                elif max_moving_frame_1 == 0 and max_moving_frame_2 != 0:
                    feature = np.array([max_moving_frame_2,max_variance_2,max_therhold_pixel_num_2,max_R_2])
                    is_fall = main_step(r"test.csv",feature)
                    if is_fall:
                        print(max_moving_frame_2, max_variance_2, max_therhold_pixel_num_2, max_R_2)
                        print("检测到跌倒状况")
                        time.sleep(5)
                    realtime_frame_1 = []
                    realtime_frame_2 = []
                    realtime_frame_3 = []
                
 
                else:
                    realtime_frame = realtime_frame[10:]
                realtime_counter = 0
                
            
        if mythread1.getQuitFlag() or mythread2.getQuitFlag():
            break
        if i >= thresh:
            saveImageData(all_frame_sensor_1,all_frame_sensor_2,path)
            thresh += 500 
except KeyboardInterrupt:
    print("==========sensor catch keyboardinterrupt==========")
    saveImageData(all_frame_sensor_1,all_frame_sensor_2,path)
finally:
    saveImageData(all_frame_sensor_1,all_frame_sensor_2,path)
    mythread1.setQuitFlag(True)
    mythread2.setQuitFlag(True)
    mythread1.close()
    mythread2.close()
print(" exit sucessfully!")

