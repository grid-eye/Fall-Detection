import numpy as np
import os
import sys
import time
row_num = 8
col_num = 8
pixel_num = 64
#使矩阵完整显示
np.set_printoptions(threshold = np.inf)
if len(sys.argv) > 1:
    try:
        dataDir = sys.argv[1]
    except:
        raise ValueError("please input the correct dir of npy data")
else:
    raise ValueError("please input the dir of npy data")
#读取路径
currDir = os.path.abspath(os.path.dirname(__file__))
if currDir.endswith("examples"):
    dataDir = currDir + "/" + dataDir

all_frame = np.load(dataDir)
if np.size(all_frame) < 10 * pixel_num:
    raise ValueError("please input the dir larger than 10*64")

frame_num = np.size(all_frame) // pixel_num #帧数
print(frame_num)
start_time = time.time()
all_var = np.zeros((frame_num - 10) * pixel_num)
for k in range(10,frame_num):
    curr_frame = all_frame[k - 10:k,:,:]
    for i in range(row_num):
        for j in range(col_num):
            curr_pixel = curr_frame[:,i,j]
            curr_var = np.var(curr_pixel)
            all_var[(k - 10) * 64 + i * 8 + j ] = curr_var
max_var = np.max(all_var)
end_time = time.time()
print(end_time - start_time)
print(max_var)


