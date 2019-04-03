import sys
import csv     #用于处理csv文件
import random    #用于随机数
import math         
import operator  
import numpy as np
from sklearn import neighbors,preprocessing
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals.six import StringIO
from sklearn.tree import export_graphviz

#加载数据集
def loadDataset(filename):
    with open(filename,"rt") as csvfile:
        lines = csv.reader(csvfile)
        temp = list(lines)
    return np.array(temp[1:],dtype = float)

def normalization(trainingSet, testSet):
    all_dataset = np.row_stack((trainingSet[:,:4],testSet))
    #print(all_dataset)
    #数据归一化
    for x in range(4):
        trainingSet[:,x] = (trainingSet[:, x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])
        testSet[x] = (testSet[x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])
        
    
#计算距离
def euclideanDistance(instance1,instance2,length):
    distance = 0
    for x in range(length):
        distance += pow((instance1[x] - instance2[x]),2)
    return math.sqrt(distance)
                                             
#返回K个最近邻
def getNeighbors(trainingSet,testInstance,k):
    distances = []
    length = len(testInstance) -1
    #计算每一个测试实例到训练集实例的距离
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x],dist))
    #对所有的距离进行排序
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    #返回k个最近邻
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors

#对k个近邻进行合并，返回value最大的key
def getResponse(neighbors):
    classVotes = {}
    for x in range(len(neighbors)):
        response = neighbors[x][-1]
        if response in classVotes:
            classVotes[response]+=1
        else:
            classVotes[response] = 1
    #排序
    sortedVotes = sorted(classVotes.items(),key = operator.itemgetter(1),reverse =True)
    return sortedVotes[0][0]
                                                                                 

def kneighbor(trainingSet, testSet):
    #print(testSet)
    normalization(trainingSet, testSet)
    #print(trainingSet)
    #print(testSet)
    k = 3
    neighbors = getNeighbors(trainingSet, testSet, k)
    result = getResponse(neighbors)
    if result == 0:
        return False
    elif result == 1:
        return True
    else:
        raise ValueError("出现错误！")

def main_step(train_data = "", test_data = []):
    trainingSet = []  #训练集
    testSet = np.array(test_data)      #测试集
    if testSet == [] or np.size(testSet,0) != 4:
        raise ValueError("please input the correct npy data")
    else:
        if train_data == "":
            trainingSet = loadDataset(r"examples/train_data.csv")
        else:
            trainingSet = loadDataset(train_data)
    print ("Train set :" + repr(len(trainingSet)) + "\nTest set :1")
    is_fall = kneighbor(trainingSet, testSet)
    return is_fall
