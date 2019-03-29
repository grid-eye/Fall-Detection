import sys
import csv     #用于处理csv文件
import random    #用于随机数
import math
import operator
import numpy as np
from sklearn import svm
from sklearn.model_selection import GridSearchCV
from sklearn.externals.six import StringIO
from sklearn.tree import export_graphviz

#加载并分割数据集
def split_loadDataset(filename,split,trainingSet=[],testSet = []):
    with open(filename,"rt") as csvfile:
        lines = csv.reader(csvfile)
        temp = list(lines)
        dataset = np.array(temp[1:],dtype = float)
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
    
    all_dataset = np.concatenate((train_dataset, test_dataset), axis=0)
    #数据归一化
    for x in range(4): 
        train_dataset[:,x] = (train_dataset[:, x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])

    for x in range(train_dataset.shape[0]):
        trainingSet.append(train_dataset[x])

    #数据归一化
    for x in range(4): 
        test_dataset[:,x] = (test_dataset[:, x] - np.mean(all_dataset[:, x])) / np.std(all_dataset[:, x])
        
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

def svm_cross_validation(train_x, train_y):    
    model = svm.SVC(kernel='rbf', probability=True)    
    param_grid = {'C': [1, 3, 5, 7, 9, 11, 13, 15, 17, 19], 'gamma': [0.00001, 0.0001, 0.001, 0.1, 1, 10, 100, 1000]}    
    grid_search = GridSearchCV(model, param_grid, cv = 5, n_jobs = 8)    
    grid_search.fit(train_x, train_y)    
    best_parameters = grid_search.best_estimator_.get_params()    
    """
    for para, val in list(best_parameters.items()):    
        print(para, val)    
    """
    model = svm.SVC(kernel='rbf', C=best_parameters['C'], gamma=best_parameters['gamma'], probability=True)    
    model.fit(train_x, train_y)    
    return model

def svm_algorithm(train_data = "", test_data = ""):
    trainingSet = []  #训练数据集
    testSet = []      #测试数据集
    split = 0.5      #分割的比例

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
    
    # kernel = 'rbf'
    test_rbf = svm_cross_validation(train_data, train_target)
    predict_rbf = test_rbf.predict(test_data)
    rbf_score = getAccuracy(test_target, predict_rbf)
    print("The score of rbf is :" + repr(rbf_score))

    # kernel = 'linear'
    test_linear = svm.SVC(C=1.0, kernel = 'linear')
    test_linear.fit(train_data, train_target)
    predict_linear = test_linear.predict(test_data)
    linear_score = getAccuracy(test_target, predict_linear)
    print("The score of linear is :" + repr(linear_score))

    """
    # kernel = 'poly'
    clf_poly = svm.SVC(kernel='poly', gamma='auto')
    clf_poly.fit(train_data, train_target)
    score_poly = clf_poly.score(test_data,test_target)
    print("The score of poly is : %f"%score_poly)
    
    """

if __name__ == "__main__":
    if len(sys.argv) > 2:
        try:
            train_data = sys.argv[1]
            test_data = sys.argv[2]
            svm_algorithm(train_data, test_data)
        except:
            raise ValueError("please input the correct dir of npy data")
    else:
        main()

