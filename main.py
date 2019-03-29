import os
import sys
import time
from examples.countpeople import CountPeople as CP
from examples.calAveBgTemperature import readBgTemperature 
from examples.feature_extraction import calFeature
from real_time import * 
"""
这个文件是自动收集n次m帧数据
"""
n ,m = 20,2000
if len(sys.argv) >3 :
        try:
            currDir = sys.argv[1]
            n = int(sys.argv[2])
            m = int(sys.argv[3])
        except:
            raise ValueError("please input a valid number ,default is 2000")
else:
    if len(sys.argv) > 2:
        try:
            currDir = sys.argv[1]
            n = int(sys.argv[2])
        except:
            raise ValueError("please input a valid number ,default is 2000")
    else:
        if len(sys.argv) > 1:
            currDir = sys.argv[1]
        else:
            raise ValueError("please specified a valid output dir for the imagedata")

cp = CP()
cp.preReadPixels()
counter = 0
curr = os.path.abspath(os.path.dirname(__file__))
if curr.endswith("Fall-Detection"):
    curr += "/examples"
bgactual = curr+"/"+currDir
imageactual = curr+"/"+currDir
cp.setPackageDir(curr)
start_time = time.time()
while counter < n:
    counter+=1
    print("the %dth whiles"%(counter))
    bgtempdir =bgactual+str(counter)
    if n == 1:
        cudr = currDir
        imagedir = imageactual
    else:
        cudr = currDir+str(counter)
        imagedir = imageactual+str(counter)
    #readBgTemperature(400,bgtempdir)
    try:
        cp.acquireImageData(m,imagedir)
    except KeyboardInterrupt:
        print("catch a keyboardinterrupt ,break the while")
        break

end_time = time.time()
print(end_time - start_time)
print("sucessfully test all picture")
if len(sys.argv) > 4:
    dataDir = imagedir + "/imagedata.npy"
    #四个特征
    max_moving_frame = 0
    max_variance = 0.0
    max_therhold_pixel_num = 0
    max_R = 0.0
    max_moving_frame, max_variance, max_therhold_pixel_num, max_R = calFeature(dataDir, max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
    feature = np.array([max_moving_frame,max_variance,max_therhold_pixel_num,max_R])
    main_step(r"five_to_five.csv",feature)
