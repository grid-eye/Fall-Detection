import numpy as np
import cv2 as cv
import time
import busio
import board
import adafruit_amg88xx
import math
import scipy
import os
import sys
import time
import matplotlib.pyplot as plt
from examples.feature_extraction import calFeature
from examples.real_time import main_step
class CountPeople:
    # otsu阈值处理后前景所占的比例阈值，低于这个阈值我们认为当前帧是背景，否则是前景

    def __init__(self, pre_read_count=30, th_bgframes=100, row=8, col=8):
        # the counter of the bgframes
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.amg = adafruit_amg88xx.AMG88XX(self.i2c)
        self.grid_x, self.grid_y = np.mgrid[0:7:32j, 0:7:32j]
        self.bgframe_cnt = 0
        self.all_bgframes = []  # save all frames which sensor read
        self.pre_read_count = pre_read_count
        self.th_bgframes = th_bgframes
        self.row = row  # image's row
        self.col = col  # image's col
        self.image_size = row * col
        self.image_id = 0  # the id of the hot image of each frame saved
        self.hist_id = 0  # the id of the hist image of diff between average
        # temp and current temp
        # 8*8 grid
        self.points = [(math.floor(ix/8), (ix % 8)) for ix in range(0, 64)]
        self.diff_ave_otsu= 0.75#通过OTSU分类的背景和前景的差的阈值,用于判断是否有人
        print("size of image is (%d,%d)"%(self.row,self.col)) 
        print("imagesize of image is %d"%(self.image_size))
        #i discard the first and the second frame
        self.__peoplenum = 0  # 统计的人的数量
        self.__diffThresh = 2.5 #温度差阈值
        self.__otsuThresh = 3.0 # otsu 阈值
        self.__averageDiffThresh = 0.20 # 平均温度查阈值
        self.__otsuResultForePropor = 0.0004
        self.__objectTrackDict = {}#目标运动轨迹字典，某个运动目标和它的轨迹映射
        self.__neiborhoodTemperature = {}#m目标图片邻域均值
        self.__neibor_diff_thresh = 1
        self.__isExist = False #前一帧是否存在人，人员通过感应区域后的执行统计人数步骤的开关
        self.__image_area = (self.row-1)*(self.col-1)
        self.__hist_x_thresh = 2.0
        self.__hist_amp_thresh = 20
        self.__isSingle = False
        
    def preReadPixels(self,pre_read_count = 20):
        self.pre_read_count =  pre_read_count
        #预读取数据，让数据稳定
        for i in range(self.pre_read_count):
            for row in self.amg.pixels:
                pass
            
    def setPackageDir(self, pdir):
        self.pdir = pdir
        
    def saveImageData(self, all_frames, outputdir):
        print("length of the all_frames: %d" % (len(all_frames)))
        print("save all images data in "+outputdir+"/"+"imagedata.npy")
        # save all image data in directory:./actual_dir
        np.save(outputdir+"/imagedata.npy", np.array(all_frames))
        # save all diff between bgtemperature and current temperature in actual dir
        
    def acquireImageData(self,frame_count = 2000,customDir = None, is_realtime = False):
        '''
            这个方法是为了获得图像数据，数据保存在customDir中
        '''
        if customDir:
            if not os.path.exists(customDir):
                os.mkdir(customDir)
                print("create dir sucessfully: %s" % (customDir))
        else:
            customDir = "imagetemp"
            if not os.path.exists(customDir):
                os.mkdir(customDir)
        # load the avetemp.py stores the average temperature
        # the result of the interpolating for the grid
        all_frames = []
        realtime_frame = []
        realtime_counter = 0
        frame_counter = 0  # a counter of frames' num
        # diff_queues saves the difference between average_temp and curr_temp
        try:
            while True:
                currFrame = []
                for row in self.amg.pixels:
                    # Pad to 1 decimal place
                    currFrame.append(row)
                currFrame = np.array(currFrame)
                print("current temperature is ")
                print(currFrame)
                all_frames.append(currFrame)
                frame_counter += 1
                print("the %dth frame" % (frame_counter))
                if frame_counter >= frame_count:
                    self.saveImageData(all_frames, customDir)
                    break
                #如果是实时检测
                if is_realtime:
                    realtime_frame.append(currFrame)
                    #滑动窗口为60帧，每滑动10帧检测一次
                    if len(realtime_frame) < 40:
                        pass
                    else:
                        
                        if realtime_counter == 20:
                            max_moving_frame = 0
                            max_variance = 0.0
                            max_therhold_pixel_num = 0
                            max_R = 0.0
                            temp_frame = np.array(realtime_frame)
                            max_moving_frame, max_variance, max_therhold_pixel_num, max_R = calFeature(temp_frame, max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
                            if max_moving_frame != max_variance:
                                feature = np.array([max_moving_frame,max_variance,max_therhold_pixel_num,max_R])
                                is_fall = main_step(r"examples/five_to_five.csv",feature)
                                if is_fall:
                                    print(max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
                                    print("检测到跌倒状况")
                                    time.sleep(5)
                                realtime_frame = []
                            else:
                                realtime_frame = realtime_frame[20:]
                            realtime_counter = 0 
                        else:
                            realtime_counter += 1
        except KeyboardInterrupt:
            print("catch keyboard interrupt")
            # save all images
            self.saveImageData(all_frames, customDir)
            print("save all frames")
