# -*- coding: utf-8 -*-
# 使用LR进行MNIST手写数字分类
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_digits
# from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt

# 加载数据
digits = load_digits()
data = digits.data
# 数据探索
print(data.shape)
# 查看第103幅图像
print(digits.images[102])
# 第103幅图像代表的数字含义
print(digits.target[102])
# 将第103幅图像显示出来
plt.gray()
plt.imshow(digits.images[102])
plt.show()

# 分割数据，将26%的数据作为测试集，其余作为训练集
train_x, test_x, train_y, test_y = train_test_split(data, digits.target, test_size=0.26, random_state=33)

# 采用Z-Score规范化
ss = preprocessing.StandardScaler()
train_ss_x = ss.fit_transform(train_x)
test_ss_x = ss.transform(test_x)

# # 创建LR分类器
# lr = LogisticRegression()
# lr.fit(train_ss_x, train_y)
# predict_y=lr.predict(test_ss_x)

#创建CART决策树分类器
clf = DecisionTreeClassifier(criterion='gini')
clf.fit(train_ss_x, train_y)
predict_y=clf.predict(test_ss_x)
print('CART准确率: %0.4lf' % accuracy_score(predict_y, test_y))
