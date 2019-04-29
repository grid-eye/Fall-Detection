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
all_merge_frame = []
cp = CountPeople()
i = 0 
container = []
time_thresh = 0.06
diff_sum = 0 
toggle = False
align = True#两帧数据时间线是否对齐，即同步

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
        current_frame = mergeData(s1,s2)#合并两个传感器的数据,取最大值
        container.append((s1,s2,current_frame))
        if len(container) == 4:
            last_three_tuple = container.pop(0)
            last_three_frame = last_three_tuple[0]
        if not cp.isCalcBg(): 
            if i == thresh:
                avgtemp = cp.calAverageTemp(all_merge_frame)
                cp.setCalcBg(True)
                cp.setBgTemperature(avgtemp)
                cp.constructAverageBgModel(avgtemp)
                print("==========time thresh is %.3f============="%(time_thresh))
                print(show_frame)
                if show_frame:
                    cv.namedWindow("image",cv.WINDOW_NORMAL)
                cp.calcBg = True
                all_merge_frame=[]
            else:
                all_merge_frame.append(current_frame)
            continue
        diff = current_frame - avgtemp
        if show_frame:
            plot_img = np.zeros(current_frame.shape,np.uint8)
            plot_img[ np.where(diff > 1.5) ] = 255
            img_resize  = cv.resize(plot_img,(16,16),interpolation=cv.INTER_CUBIC)
            cv.imshow("image",img_resize)
            cv.waitKey(1)
        res = False
        ret = cp.isCurrentFrameContainHuman(current_frame,avgtemp,diff)
        if not ret[0]:
            cp.updateObjectTrackDictAgeAndInterval()
            cp.tailOperate(current_frame,last_three_frame)
            if cp.getExistPeople():
                cp.setExistPeople(False)
            continue
        cp.setExistPeople(True)
        print("extractbody")
        (cnt_count,image ,contours,hierarchy),area =cp.extractBody(cp.average_temp, current_frame)
        if cnt_count ==0:
            cp.updateObjectTrackDictAgeAndInterval()
            cp.tailOperate(current_frame,last_three_frame)
            continue
        #下一步是计算轮当前帧的中心位置
        loc = cp.findBodyLocation(diff,contours,[ i for i in range(cp.row)])
        cp.trackPeople(current_frame,loc)#检测人体运动轨迹
        cp.updateObjectTrackDictAge()#增加目标年龄
        cp.tailOperate(current_frame,last_three_frame)
        #sleep(0.5)
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

