import sys
import csv     #用于处理csv文件
import random    #用于随机数
import math         
import operator  
import numpy as np
from sklearn import neighbors,preprocessing
 
#加载并分割数据集
def split_loadDataset(filename,split,trainingSet=[],testSet = []):
    with open(filename,"rt") as csvfile:
        lines = csv.reader(csvfile)
        temp = list(lines)
        dataset = np.array(temp[1:],dtype = float)
        """
        for x in range(1, dataset.shape[0]):
            for y in range(dataset.shape[1] - 1):
                dataset[x][y] = float(dataset[x][y])
        """
        #数据归一化
        for x in range(4):
            dataset[:,x] = (dataset[:, x] - np.mean(dataset[:, x])) / np.std(dataset[:, x])

        for x in range(dataset.shape[0]):
            if random.random()<split:
                trainingSet.append(dataset[x])
            else:
                testSet.append(dataset[x])

def loadDataset(train_filename, test_filename,trainingSet=[],testSet = []):
    with open(train_filename,"rt") as train_csvfile:
        train_lines = csv.reader(train_csvfile)
        temp = list(train_lines)
        train_dataset = np.array(temp[1:],dtype = float)
    with open(test_filename,"rt") as test_csvfile:
        test_lines = csv.reader(test_csvfile)
        temp = list(test_lines)
        test_dataset = np.array(temp[1:],dtype = float)
    all_dataset = np.concatenate((test_dataset,train_dataset), axis = 0)
    #数据归一化
    for x in range(4):
        train_dataset[:,x] = (train_dataset[:, x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])
        test_dataset[:,x] = (test_dataset[:, x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])
    for x in range(train_dataset.shape[0]):
        trainingSet.append(train_dataset[x])
    for x in range(test_dataset.shape[0]):
        testSet.append(test_dataset[x])

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
                                                                                 
#计算准确率
def getAccuracy(testSet,predictions):
    fall_num = [x[-1] for x in testSet].count(1.0)
    nonfall_num = [x[-1] for x in testSet].count(0.0)
    predict_fall_num, predict_nonfall_num = fall_num, nonfall_num
    correct = 0
    for x in range(len(testSet)):
        if testSet[x][-1] == predictions[x]:
            correct+=1
        else:
            if predictions[x] == 1.0:#若未跌倒被检测成跌倒
                predict_nonfall_num -= 1
            if predictions[x] == 0.0:#若跌倒被检测成未跌倒
                predict_fall_num -= 1
    print("fall correct is " + repr(predict_fall_num/fall_num*100))
    print("nonfall correct is " + repr(predict_nonfall_num/nonfall_num*100))
    return (correct/float(len(testSet))) * 100.0
                                                                                                                         

def kneighbor(train_data = "", test_data = ""):
    trainingSet = []  #训练数据集
    testSet = []      #测试数据集
    split = 0.5 #分割的比例
    k = 3
    if train_data == "" and test_data == "":
        split_loadDataset(r"three_to_seven.csv", split, trainingSet, testSet)
    elif train_data != "" and test_data != "" :
        loadDataset(train_data, test_data, trainingSet, testSet)
    print ("Train set :" + repr(len(trainingSet)))
    print ("Test set :" + repr(len(testSet)))        
    
    predictions = []
    for x in range(len(testSet)):
        neighbors = getNeighbors(trainingSet, testSet[x], k)
        result = getResponse(neighbors)
        predictions.append(result)
        #print (">predicted = " + repr(result) + ",actual = " + repr(testSet[x][-1]))
    
    accuracy = getAccuracy(testSet, predictions)
    print ("Accuracy:" + repr(accuracy) + "%")
    
if __name__ == "__main__":
    if len(sys.argv) > 2:
        try:
            train_data = sys.argv[1]
            test_data = sys.argv[2]
            kneighbor(train_data, test_data)
        except:
            raise ValueError("please input the correct dir of npy data")
    else:
        kneighbor()
