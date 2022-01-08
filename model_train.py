# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestRegressor
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
# %matplotlib inline

root = '/home/eunji/project_dir/sodescar/data/socar_usage_processed.csv'

df = pd.read_csv(root)
df.head(3)

# 임의의 컬럼 삭제 -> tree 구조에서는 원핫인코딩은 도움이 되지 않는다고 합니다.
drop_col = ['member_id', 'member_gender','region',
            'reservation_return_at','reservation_start_at',
            'member_created_date','car_name']

df = df.drop(columns=drop_col)

car_type = df.car_type.unique().tolist()
df.car_type.value_counts()

# 레이블 인코딩
def encoding_features(x):
    le = preprocessing.LabelEncoder()
    le.fit(x)
    label = le.transform(x)

    return label

df['car_type']=encoding_features(df['car_type'])

# 인코딩하면서 생긴 결측치 제거
df.dropna()
find_index4 = df[df['car_type']==4].index
df = df.drop(find_index4)
#df.tail()

car_type = df.car_type.unique().tolist()
car_type

x = df.drop(['car_type'], axis=1) #feature
y = df['car_type'] #target

minmaxScaler = MinMaxScaler()
XminmaxScaled = minmaxScaler.fit_transform(x)

y.value_counts()

x_train, x_test, y_train, y_test = train_test_split(XminmaxScaled, y, test_size=0.2)

# imbalanced data 오버 샘플링 처리
x_resampled, y_resampled = SMOTE(random_state=0).fit_resample(x_train, y_train)
y_resampled.value_counts()

# k_fold validation 적용 (연산이 오래 걸릴수도 있음)
# -> 연산이 너무 많이 걸리지 않는 선에서 최대 효율을 뽑을 필요가 있어보임
k_fold = KFold(random_state=50, n_splits=5, shuffle=True)

# 모델 설정
model = RandomForestRegressor()
#model = 다른 모델 사용가능

# 그리드 서치 파라미터 설정
param_grid = {#'max_iter':[50, 100, 200, 300],
              'n_estimators': [200,250],
              'max_depth': [40,50],
              'min_samples_split' : [30,35],
              'min_samples_leaf': [30,40],
              }

grid_search = GridSearchCV(estimator = model, 
                           param_grid = param_grid,
                           cv = 5)

grid_search.fit(x_resampled, y_resampled)
best_param = grid_search.best_params_

# 최적 파라미터와 결과
print(best_param)
print('best score : {}'.format(grid_search.best_score_))

# 최종 모델 학습
'''
final_model = ensemble.HistGradientBoostingRegressor(
           max_iter=200,
           #n_estimators=300, 
           max_depth=3, 
           min_samples_leaf=100,
           learning_rate=0.05,
           categorical_features = [2],
           loss='squared_error')
'''
'''
def metircs(y_test, pred):
    accuracy = accuracy_score(y_test,pred)
    precision = precision_score(y_test,pred)
    recall = recall_score(y_test,pred)
    f1 = f1_score(y_test,pred)
    roc_score = roc_auc_score(y_test,pred,average='macro')
    print('정확도 : {0:.2f}, 정밀도 : {1:.2f}, 재현율 : {2:.2f}'.format(accuracy,precision,recall))
    print('f1-score : {0:.2f}, auc : {1:.2f}'.format(f1,roc_score,recall))

def metric_result(model, x_train, x_test, y_train, y_test):
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics(y_test, pred)
'''