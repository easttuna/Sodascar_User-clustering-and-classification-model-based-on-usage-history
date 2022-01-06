# -*- coding: utf-8 -*-

'''
from google.colab import drive
drive.mount('/content/drive')
'''

import os
import torch
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
import matplotlib.pyplot as plt
# %matplotlib inline

root = os.path.join(os.getcwd(), "drive", "MyDrive", "Colab Notebooks", "member.csv")
#root

df = pd.read_csv(root)
#df.head(3)

# 임의의 컬럼 삭제(범주화 컬럼 인코딩 필요), tree 구조에서는 원핫인코딩은 도움이 되지 않는다고 합니다.
drop_col = ['member_id', 'member_gender']
df = df.drop(columns=drop_col)

# df.shape -> (23555, 22) 
# train set 80%, test set 20%

train = df[:18844]
#val = df[14133:18844]
test = df[18844:]

df.head(3)

# 예측 모델을 만들기 위한 데이터셋 정리
x_train = np.asarray(train.drop('car_type_mode',1))
y_train = np.asarray(train['car_type_mode'])

x_test = np.asarray(test.drop('car_type_mode',1))
y_test = np.asarray(test['car_type_mode'])

x = np.concatenate((x_train, x_test), axis=0) # feature
y = np.concatenate((y_train, y_test), axis=0) # target

# k_fold validation 적용 (연산이 오래 걸릴수도 있음)
# -> 연산이 너무 많이 걸리지 않는 선에서 최대 효율을 뽑을 필요가 있어보임
k_fold = KFold(random_state=50, n_splits=10, shuffle=True)

# 모델 설정
model = RandomForestRegressor()
#model = GradientBoostingRegressor()
# model을 더 추가해주셔도 됩니다.

# 그리드 서치 파라미터 설정
param_grid = {#'max_iter':[50, 100, 200, 300],
              'max_depth': [24],
              'min_samples_leaf': [12],
              #'learning_rate': [0.01, 0.02, 0.05],
              'min_samples_split' : [20, 30],
              'n_estimators': [10],
              #'loss' : ["squared_error"],
              #'categorical_features':[0,2,3,]
              }

grid_search = GridSearchCV(estimator = model, 
                           param_grid = param_grid,
                           cv = k_fold,
                           scoring = 'neg_mean_squared_error')

grid_search.fit(x, y)
best_param = grid_search.best_params_

# 최적 파라미터와 결과
print(best_param)
print('best score : {}'.format(grid_search.best_score_))

reg = ensemble.HistGradientBoostingRegressor(
           max_iter=200,
           #n_estimators=300, 
           max_depth=3, 
           min_samples_leaf=100,
           learning_rate=0.05,
           categorical_features = [2],
           loss='squared_error')

reg.fit(x_train, y_train)



