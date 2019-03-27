import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import os
import sys
"""绘图脚本"""
if len(sys.argv) > 2:
    path = sys.argv[1]
    output = sys.argv[2]
else:
    raise ValueError("please input the image's data's path and output dir")
if not os.path.exists(path):
    raise ValueError("please input a valid path")
def compatibleForCv(image):
    cv.imwrite("temp.png",image)
    return cv.imread("temp.png",0)
def convertData2Image(imageData,image_id,filter_process=False):
    if filter_process == True:
        plt.subplot(221)
    else:
        plt.subplot(211)
    plt.imshow(imageData)
    plt.xticks([])
    plt.yticks([])
    plt.title("image_%d"%(image_id))
    plt.tight_layout()
    plt.savefig("image_%d"%(image_id))
    plt.clf()
imagedata = np.load(path)
print("load data sucessfully!")
print(imagedata.shape)
for i in range(len(imagedata)):
    print('%dth frames pic'%(i))
    convertData2Image(imagedata[i],i,True)
print("save sucessfully")

