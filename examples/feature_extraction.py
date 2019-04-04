import numpy as np
import os
import sys
import time
import csv
from skimage.measure import label,regionprops
row_num = 8
col_num = 8
pixel_num = 64
k_start = 0 
k_end = 0
#阈值
therhold = 0.8
#取的帧数
pick_frame = 10

max_var_list = [] #存放最大方差的矩阵
active_pixel_num_list = []#存放一帧中高温点的个数的矩阵
max_R_list = []#存放高温区域的形态特征R的矩阵

def calR(curr_temp_frame):
    global max_R_list
    temp = curr_temp_frame.flatten()
    #舍弃1/3的温度，取温度相对较高的部分计算温度均值
    sorted_temp = np.sort(temp)[::-1]
    chosed_temp = sorted_temp[:np.size(sorted_temp) * 2 // 3]
    """
    print(chosed_temp)
    print(np.size(chosed_temp))
    """
    #计算高温均值
    avgTemp = np.mean(chosed_temp)
    higher_temp_frame = np.array(curr_temp_frame)
    """
    print(higher_temp_frame)
    """
    #得到各个高温连通区域
    higher_temp_frame[higher_temp_frame <= avgTemp] = 0
    higher_temp_frame[higher_temp_frame > avgTemp] = 1
    higher_temp_frame.astype(int)
    """
    print(avgTemp)
    print(higher_temp_frame)
    """
    label_img = label(higher_temp_frame,connectivity = 1)
    """
    print(label_img)
    """
    #各个连通区域的属性
    props = regionprops(label_img)
    #找到最大高温区域
    area_dict = dict()
    for i in range(len(props)):
        area_dict[i] = props[i].area
    """
    print(max(area_dict,key = area_dict.get))
    """
    max_area_pos = max(area_dict,key = area_dict.get)
    #求高温特征R
    pos = props[max_area_pos].bbox
    row_len = pos[2] - pos[0]
    col_len = pos[3] - pos[1]
    curr_R = props[max_area_pos].area * max(row_len, col_len) / min(row_len, col_len)
    max_R_list.append(curr_R)

def calFeature(all_frame, max_moving_frame = 0, max_variance = 0, max_therhold_pixel_num = 0, max_R = 0):
    is_human = False
    if np.size(all_frame) < pick_frame * pixel_num:
        raise ValueError("please input the dir larger than 10*64")

    frame_num = np.size(all_frame) // pixel_num #帧数
    #print(frame_num)
    curr_all_var = np.zeros(pixel_num)
    for k in range(pick_frame,frame_num + 1):
        curr_frame = all_frame[k - pick_frame:k,:,:]
        """ 
        for i in range(row_num):
            for j in range(col_num):
                curr_pixel = curr_frame[:,i,j]
                curr_var = np.var(curr_pixel)
                curr_all_var[i * 8 + j ] = curr_var
        """
        curr_all_var = np.var(curr_frame,0)
        #当前温度分布最大方差        
        curr_max_var = np.max(curr_all_var)
        #如果存在方差分布有超过阈值的像素点，则证明有人在传感器范围内
        if curr_max_var > therhold:
            if not is_human:
                is_human = True
                curr_k_start = k
            #存放当前最大方差
            max_var_list.append(curr_max_var)
            #存放活跃像素数量
            active_pixel = np.where(curr_all_var > therhold)
            active_num = np.size(active_pixel)
            active_pixel_num_list.append(active_num)
            #计算当前帧高温区域的形态特征R
            calR(curr_frame[pick_frame - 1])
        else:
            if is_human:
                is_human = False
                curr_k_end = k
                if max_moving_frame < curr_k_end - curr_k_start + 1:
                    k_start = curr_k_start
                    k_end = curr_k_end
                    print(k_start, k_end)
                    #计算出最大运动帧数
                    max_moving_frame = curr_k_end - curr_k_start + 1
                    #计算出最大方差
                    frame_size = np.size(max_var_list) - (k_end - k_start)
                    max_variance = np.max(max_var_list[frame_size:])
                    #计算出最大活跃像素数量
                    max_therhold_pixel_num = np.max(active_pixel_num_list[frame_size:])
                    #计算出高温区域的形态特征R的最大值
                    max_R = np.max(max_R_list[frame_size:])
                """ 
                print(max_R_list)
                print(max_var_list)
                print(max_var_list[frame_size:])
                print(active_pixel_num_list)
                """
            else:
                continue
    if is_human:
        return 0,0,0,0
    return max_moving_frame, max_variance, max_therhold_pixel_num, max_R

                                
def write_csv(max_moving_frame, max_variance, max_therhold_pixel_num, max_R, is_fall):
    path  = "backup.csv"
    with open(path,'a+') as f:
        csv_write = csv.writer(f)
        data_row = [max_moving_frame, max_variance, max_therhold_pixel_num, max_R, is_fall]
        csv_write.writerow(data_row)

if __name__ == "__main__":
    #四个特征
    max_moving_frame = 0
    max_variance = 0.0
    max_therhold_pixel_num = 0
    max_R = 0.0 
    #使矩阵完整显示
    np.set_printoptions(threshold = np.inf)
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
    max_moving_frame, max_variance, max_therhold_pixel_num, max_R = calFeature(all_frame, max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
    print(max_moving_frame, max_variance, max_therhold_pixel_num, max_R)
    if len(sys.argv) > 2:
        is_fall = sys.argv[2]
        write_csv(max_moving_frame, max_variance, max_therhold_pixel_num, max_R, is_fall)
