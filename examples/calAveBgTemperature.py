import time
import busio
import board
import adafruit_amg88xx
import math
import scipy
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
frame_x = 8
frame_y = 8
# we need th_bgframes frames  to calculate the average temperature of the bground
th_bgframes = 400
# the counter of the bgframes frames
bgframe_cnt = 0
# 8X8 grid
points = [(math.floor(ix/8), (ix % 8)) for ix in range(0, 64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
pre_read_count=20
for i in range(pre_read_count):
    for row in amg.pixels:
        pass


# 插值(cublic)
def interpolate(points, pixels, grid_x, grid_y, ip_type='cubic'):
    return griddata(points, pixels, (grid_x, grid_y), method=ip_type)
def readBgTemperature(th_bg=None,save_dir="bgtemp"):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    all_bgframes = []
    print("read bg temperature ,the save dir is %s"%(save_dir))
    if th_bg != None:
       th_bgframes = th_bg
    bgframe_cnt = 0
    while True:
        temp = []
        for row in amg.pixels:
            # Pad to 1 decimal place
            temp.append(row)
        bgframe_cnt = bgframe_cnt + 1
        if bgframe_cnt == 1:
            print(np.array(temp))
        all_bgframes.append(temp)
        if bgframe_cnt >= th_bgframes:
            print('next step')
            print(len(all_bgframes))
            total_frames = np.zeros((8,8))
            for aitem in range(len(all_bgframes)):
                total_frames = total_frames + np.array(all_bgframes[aitem])
            average_temperature = total_frames /len(all_bgframes)
            print("the average temperature is considered as bgtemperature")
            print(average_temperature)
            # print(grid_x.shape, grid_y.shape)
            # the result of the interpolating for the grid
            # average_temp = np.array(average_temperature).flatten()
            average_temp = np.round(average_temperature,2)
            #inter_result = interpolate(
            #   points, average_temp, grid_x, grid_y, 'linear')

            # temp = interpolate(points, np.array(
            #    temp).flatten(), grid_x, grid_y, 'linear')
            # print("after interpolating , save the data in path %s"%(save_dir))
            np.save('%s/avgtemp.npy'%(save_dir), average_temp)
            '''
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
            ax1.imshow(inter_result, cmap='hot', interpolation='bilinear')
            ax1.set_xlabel('X')
            ax1.set_ylabel('Y')
            ax1.axis([0, 32, 32, 0])
            ax2.hist(inter_result.ravel(),
                     bins=256, range=(16, 20), fc='k', ec='k')

            ax2.set_xlabel('temperature')
            ax2.set_ylabel('%')
            temp_diff = np.array(temp) - inter_result
            ax3.hist(temp_diff.ravel(), bins=256,
                     range=(-1.0, 0.9), fc='k', ec='k')
            ax3.set_xlabel('temperature-diff')
            ax3.set_ylabel('%')
            #plt.show()
            '''
            break
if __name__ == '__main__':
    pre_read_count = 30
    curr_dir = os.path.abspath(os.path.dirname(__file__))
    if curr_dir.endswith("grideye"):
        curr_dir = curr_dir+"/countpeople"
    actual_path = curr_dir
    if len(sys.argv) > 1:
        actual_path = actual_path +"/"+ sys.argv[1]
    if not os.path.exists(actual_path):
        os.mkdir(actual_path)
    readBgTemperature(400 ,actual_path)
