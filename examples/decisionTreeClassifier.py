import sys
import csv     #用于处理csv文件
import random    #用于随机数
import math
import operator
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.externals.six import StringIO
from sklearn.tree import export_graphviz

#加载并分割数据集
def split_loadDataset(filename,split,trainingSet=[],testSet = []):
    with open(filename,"rt") as csvfile:
        lines = csv.reader(csvfile)
        temp = list(lines)
        dataset = np.array(temp[1:],dtype = float)
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
        for x in range(train_dataset.shape[0]):
            trainingSet.append(train_dataset[x])
                         
    with open(test_filename,"rt") as test_csvfile:
        test_lines = csv.reader(test_csvfile)
        temp = list(test_lines)
        test_dataset = np.array(temp[1:],dtype = float)

        for x in range(test_dataset.shape[0]):
            testSet.append(test_dataset[x])

#计算准确率
def getAccuracy(test_target,predict_target):
    fall_num = np.sum(test_target == 1.0)
    nonfall_num = np.sum(test_target == 0.0)
    predict_fall_num, predict_nonfall_num = fall_num, nonfall_num
    correct = 0
    for x in range(len(test_target)):
        if test_target[x] == predict_target[x]:
            correct+=1
        else:
            if predict_target[x] == 1.0:#若未跌倒被检测成跌倒
                predict_nonfall_num -= 1
            if predict_target[x] == 0.0:#若跌倒被检测成未跌倒
                predict_fall_num -= 1
    print("fall correct is " + repr(predict_fall_num/fall_num*100))
    print("nonfall correct is " + repr(predict_nonfall_num/nonfall_num*100))
    return (correct/float(len(test_target))) * 100.0
                                  
def decisiontree(train_data = "", test_data = ""):
    trainingSet = []  #训练数据集
    testSet = []      #测试数据集
    split = 0.3      #分割的比例
    if train_data == "" and test_data == "":
        split_loadDataset(r"data.csv", split, trainingSet, testSet)
    elif train_data != "" and test_data != "" :
        loadDataset(train_data, test_data, trainingSet, testSet)
    else:
        raise ValueError("please input the correct dir of npy data")
    
    print ("Train set :" + repr(len(trainingSet)))
    print ("Test set :" + repr(len(testSet)))

    #训练集
    train_data = np.array(trainingSet)[:,:len(trainingSet[0])-1]
    # 训练集样本类别
    train_target = np.array(trainingSet)[:,len(trainingSet[0])-1]
    # 测试集
    test_data = np.array(testSet)[:,:len(testSet[0])-1]
    #测试集样本类别
    test_target = np.array(testSet)[:,len(testSet[0])-1]
    
    #build the decisionTreeClassifier
    clf = DecisionTreeClassifier(criterion = 'gini', max_depth = 4, min_samples_split = 0.05, class_weight = 'balanced')
    clf.fit(train_data, train_target)  # 训练决策树
    #print(clf)
    predict_target = clf.predict(test_data)  # 预测
    accuracy = getAccuracy(test_target, predict_target)
    print ("Accuracy:" + repr(accuracy) + "%")
    with open("iris.dot", 'w') as f:
        f = export_graphviz(clf, out_file=f)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        try:
            train_data = sys.argv[1]
            test_data = sys.argv[2]
            decisiontree(train_data, test_data)
        except:
            raise ValueError("please input the correct dir of npy data")
    else:
        decisiontree()
