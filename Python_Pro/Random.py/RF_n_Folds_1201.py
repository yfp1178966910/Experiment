# random_forest_classifier.py

from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
import pandas as pd
import numpy as np

# 读取数据
dataset = pd.read_csv("flow_1201.csv")
data = dataset.iloc[:dataset.shape[0], :dataset.shape[1] - 1] # 特征集
target = dataset.iloc[:dataset.shape[0], dataset.shape[1] - 1:]  # 标记

# X_train 训练特征集，  X_test 测试特征集
# y_train 训练标记集，	y_test 测试标记集
X_train, X_test, y_train, y_test = cross_validation.train_test_split(
 								data, target, test_size=0.1, random_state=0)

# print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
classifier = RandomForestClassifier(n_estimators=30, max_depth=None, min_samples_split=2, random_state=0)
classifier.fit(X_train, y_train)
score = classifier.score(X_test, y_test)
print(score)

prediction = classifier.predict(X_test)
print(prediction)