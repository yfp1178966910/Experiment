from random import seed
from random import randrange
from csv import reader
from math import sqrt

# csv -> list[]
def load_csv(filename):
    dataset = list()
    with open(filename, "r") as file:
        csv_reader = reader(file)
        for row in csv_reader:
            if not row:
                continue
            dataset.append(row)
    return dataset

# features str -> float
def str_Feature_to_Float(dataset):
    for row in dataset:
        for i in range(0, len(row)-1):
            row[i] = float(row[i])

# class str -> int
def str_Class_to_Int(dataset, column):
    class_value = [int(row[-1]) for row in dataset]
    # set dict{ }

    # 利用集合和字典
    unique = set(class_value) # 将所有类别置于一个集合内（无重复）
    lookup = dict()
    for index, value in enumerate(unique): # 建立一个列表，利用enumerate
                                        # 计数功能， 将所有类别转化成连续的数字
        lookup[value] = index+1

    for row in dataset:
        row[-1] = lookup[int(row[-1])]

    return lookup

# Split a dataset based on an attribute and an attribute value
def test_split(index, value, dataset):
    left, right = list(), list()
    for row in dataset:
        #print(index, row[index])
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
    features_num = list()
    while len(features_num) < n_features:
        index = randrange(len(dataset[0]) - 1)
        if index not in features_num:
            features_num.append(index)
    for index in features_num:
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
    print(type(left))
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
    root = get_split(train, n_features)
    split(root, max_depth, min_size, n_features, 1)
    return root

# Create a Ran subsample from the dataset with replacement
def subsample(dataset, ratio):
    sample = list()
    n_sample = round(len(dataset) * ratio)

    while len(sample) < n_sample:
        index = randrange(len(dataset))  # 随机有放回抽样，添加到sample中
        sample.append(dataset[index])
    return sample

# model
def random_forest(train, max_depth, min_size, sample_size, n_trees, n_features):
    trees = list()
    for i in range(n_trees):
        sample = subsample(train, sample_size)
        tree = build_tree(sample, max_depth, min_size, n_features)
        trees.append(tree)

    return trees

# predict
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

def bagging_predict(trees, row):
    predictions = [predict(tree, row) for tree in trees]
    return max(set(predictions), key = predictions.count)

# scores
def accuracy_metric(actual, predicted):
    correct = 0
    for i in range(len(actual)):
        if actual[i] == predicted[i]:
            correct += 1
    return correct / float(len(actual)) * 100.0



train_set = load_csv("flow_1126.csv")
test_set = load_csv("flow.csv")

for train in range(0, len(train_set[0])-1):
    str_Feature_to_Float(train_set)
for test in range(0, len(test_set[0])-1):
    str_Feature_to_Float(test_set)

str_Class_to_Int(train_set, len(train_set[0])-1)
str_Class_to_Int(test_set, len(test_set[0])-1)



max_depth = 5
min_size = 1
sample_size = 1.0
n_features = int(sqrt(len(train_set[0])-1))
#n_features =11
# get model  ( train + test)
for n_trees in [1, 5, 10]:
    trees = random_forest(train_set, max_depth, min_size, sample_size, n_trees, n_features)
    prediction = [bagging_predict(trees, row) for row in test_set]
    actual = [row[-1] for row in test_set]
    print(prediction)
    print(actual)
    accuracy = accuracy_metric(actual, prediction)

    print("Tree %d" % n_trees)
    print("accuracy: %.3f%%" % accuracy)

