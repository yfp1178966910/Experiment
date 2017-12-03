# -- coding:utf-8 --

'''
随机森林算法;
1. n折交叉验证
2. 评价指标，准确度、

'''

from random import seed
from random import randrange
from csv import reader
from math import sqrt

# 加载CSV文件
def load_csv(filename):
    dataset = list()
    with open(filename, "r") as file:
        csv_reader = reader(file)
        for row in csv_reader:
            if not row:
                continue
            dataset.append(row)

    return dataset


# 数据集中 特征字符串 -> float
def str_column_to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())
        # print(row)


# 数据集中 类别 ->  int
def str_column_to_int(dataset, column):
    #class_values = [row[column] for row in dataset]
    # print(class_values)
    # unique = set(class_values)
    # lookup = dict()
    # for i, value in enumerate(unique):
    #     lookup[value] = i
    # for row in dataset:
    #     row[column] = lookup[row[column]]
    # return lookup
    for row in dataset:
        row[column] = int(row[column])


# n折数据集
def cross_validation_split(dataset, n_folds):
    dataset_split = list()
    dataset_copy = list(dataset)
    # print(len(dataset_copy))
    fold_size = len(dataset) / n_folds
    # print(fold_size)
    for i in range(n_folds):
        fold = list()
        while len(fold) < fold_size:

            if len(dataset_copy) != 0:
                index = randrange(len(dataset_copy))
            else:
                break
            fold.append(dataset_copy.pop(index))
        dataset_split.append(fold)
        # print(dataset_split)
    return dataset_split


# 计算准确度
def accuracy_metric(actual, predicted):
    TP = 0
    FP = 0
    TN = 0
    FN = [0, 0, 0, 0]
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            TP += 1
        # if actual[i] == 47:
        #     if predicted[i] != 47:
        #         FN[0] += 1
        # if actual[i] == 46:
        #     if predicted[i] != 46:
        #         FN[2] += 1
        # if actual[i] == 2:
        #     if predicted[i] != 2:
        #         FN[1] += 1
        # if actual[i] == 4:
        #     if predicted[i] != 4:
        #         FN[3] += 1

    #print(FN)

    return TP / float(len(actual)) * 100.0


# 评价算法
def evaluate_algorithm(dataset, algorithm, n_folds, *args):
    folds = cross_validation_split(dataset, n_folds)
    scores = list()
    for fold in folds:
        train_set = list(folds)
        train_set.remove(fold)
        train_set = sum(train_set, [])
        test_set = list()
        for row in fold:
            row_copy = list(row)
            test_set.append(row_copy)
            row_copy[-1] = None
        predicted = algorithm(train_set, test_set, *args)  # 预测结果
        actual = [row[-1] for row in fold]  # 真实值
        print(predicted)
        print(actual)
        accuracy = accuracy_metric(actual, predicted)  # 计算准确度
        scores.append(accuracy)
    return scores


# 随机森林
def random_forest(train, test, max_depth, min_size, sample_size, n_trees, n_features):
    trees = list()
    for i in range(n_trees):
        sample = subsample(train, sample_size)
        tree = build_tree(sample, max_depth, min_size, n_features)
        trees.append(tree)
    predictions = [bagging_predict(trees, row) for row in test]
    # print(predictions)
    return (predictions)


# Split a dataset based on an attribute and an attribute value
def test_split(index, value, dataset):
    left, right = list(), list()
    for row in dataset:
        # print(index, row[index])
        if row[index] < value:
            left.append(row)
        else:
            right.append(row)
    return left, right


# Calculate the Gini index for a split dataset
def gini_index(groups, class_values):
    gini = 0.0
    for class_value in class_values:
        for group in groups:
            size = len(group)
            if size == 0:
                continue
            proportion = [row[-1] for row in group].count(class_value) / float(size)
            gini += (proportion * (1.0 - proportion))
    return gini


# Select the best split point for a dataset
def get_split(dataset, n_features):
    class_values = list(set(row[-1] for row in dataset))
    b_index, b_value, b_score, b_groups = 999, 999, 999, None
    features = list()
    while len(features) < n_features:
        index = randrange(len(dataset[0]) - 1)
        if index not in features:
            features.append(index)
    for index in features:
        for row in dataset:
            groups = test_split(index, row[index], dataset)
            gini = gini_index(groups, class_values)
            if gini < b_score:
                b_index, b_value, b_score, b_groups = index, row[index], gini, groups
    return {"index": b_index, "value": b_value, "groups": b_groups}


# Create a terminal node value
def to_terminal(group):
    outcomes = [row[-1] for row in group]
    return max(set(outcomes), key=outcomes.count)


# Create child splits for a node or make terminal
def split(node, max_depth, min_size, n_features, depth):
    left, right = node["groups"]
    del (node["groups"])
    # check for a no split
    if not left or not right:
        node["left"] = node["right"] = to_terminal(left + right)
        return
    # check for max depth
    if depth >= max_depth:
        node["left"], node["right"] = to_terminal(left), to_terminal(right)
        return
    # process left child
    if len(left) <= min_size:
        node["left"] = to_terminal(left)
    else:
        node["left"] = get_split(left, n_features)
        split(node["left"], max_depth, min_size, n_features, depth + 1)
    # process right child
    if len(right) <= min_size:
        node["right"] = to_terminal(right)
    else:
        node["right"] = get_split(right, n_features)
        split(node["right"], max_depth, min_size, n_features, depth + 1)


# Build a decision tree
def build_tree(train, max_depth, min_size, n_features):
    root = get_split(dataset, n_features)
    split(root, max_depth, min_size, n_features, 1)
    return root


# Make a prediction with a decision tree
def predict(node, row):
    if row[node["index"]] < node["value"]:
        if isinstance(node["left"], dict):
            return predict(node["left"], row)
        else:
            return node["left"]
    else:
        if isinstance(node["right"], dict):
            return predict(node["right"], row)
        else:
            return node["right"]


# Create a Ran subsample from the dataset with replacement
def subsample(dataset, ratio):
    sample = list()
    n_sample = round(len(dataset) * ratio)
    while len(sample) < n_sample:
        index = randrange(len(dataset))
        sample.append(dataset[index])
    return sample


# Make a prediction with a list of bagged trees
def bagging_predict(trees, row):
    predictions = [predict(tree, row) for tree in trees]
    # print(max(set(predictions), key=predictions.count))
    return max(set(predictions), key=predictions.count)


# Test the Ran forest algorithm
seed(1)
# load and prepare data
filename = "flow_1201.csv"
dataset = load_csv(filename)


# convert string attributes to integers
print(len(dataset[0]) - 1)
for i in range(0, len(dataset[0]) - 1):
    str_column_to_float(dataset, i)

# convert class column to integers
str_column_to_int(dataset, len(dataset[0]) - 1)

# evaluate algorithm
n_folds = 10  # n-fold validation
max_depth = 5  # tree max depth
min_size = 1
sample_size = 1.0  #
n_features = int(sqrt(len(dataset[0]) - 1))
# print(n_features)
# n_features = 11
for n_trees in [1, 5, 10]:
    scores = evaluate_algorithm(dataset, random_forest, n_folds,
                                max_depth, min_size, sample_size, n_trees, n_features)
    print("Trees: %d" % n_trees)
    print("Scores: %s" % scores)
    print("Mean Accuracy: %.3f%%" % (sum(scores) / float(len(scores))))
