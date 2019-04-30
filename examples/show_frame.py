import numpy as np
import time
import os
import cv2 as cv
import sys
#使矩阵完整显示
np.set_printoptions(threshold = np.inf)

def showframe(curr_frame, window_name = "image"):
    cv.namedWindow(window_name,cv.WINDOW_NORMAL)
    avgCal = np.mean(curr_frame)
    diff = np.array([x - avgCal for x in curr_frame])
    plot_img = np.zeros(curr_frame.shape,np.uint8)
    plot_img[np.where(diff > 1) ] = 255
    img_resize  = cv.resize(plot_img,(16,16),interpolation=cv.INTER_CUBIC)
    cv.imshow(window_name,img_resize)
    cv.waitKey(1)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            Dir = sys.argv[1]
        except:
            raise ValueError("please input the correct dir of npy data")                    
    else:
        raise ValueError("please input the dir of npy data")

    #读取路径
    currDir = os.path.abspath(os.path.dirname(__file__))
    if currDir.endswith("examples"):
        Dir = currDir + "/" + Dir
    #读取数据
    all_frame = np.load(Dir)
    #print(all_frame.shape[0])
    for i in range(all_frame.shape[0]):
        showframe(all_frame[i])
