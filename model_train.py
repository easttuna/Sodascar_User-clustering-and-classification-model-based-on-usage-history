# -*- coding: utf-8 -*-


# Commented out IPython magic to ensure Python compatibility.
import os
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
# %matplotlib inline


root = os.path.join(os.getcwd(), "drive", "MyDrive", "Colab Notebooks", "member.csv")
root

root = '/home/eunji/project_dir/sodescar/data/socar_usage_processed.csv'


df = pd.read_csv(root)
df.head(3)

# 임의의 컬럼 삭제 -> tree 구조에서는 원핫인코딩은 도움이 되지 않는다고 합니다.
drop_col = ['member_id', 'member_gender','region',
            'reservation_return_at','reservation_start_at',
            'member_created_date','car_name']

df = df.drop(columns=drop_col)

car_type = df.car_type.unique().tolist()

# 레이블 인코딩
def encoding_features(x):
    features = df.car_type.unique().tolist()
    
    le = preprocessing.LabelEncoder()
    le.fit(x)
    label = le.transform(x)

    return label

df['car_type']=encoding_features(df['car_type'])

x = df.drop(['car_type'], axis=1) #feature
y = df['car_type'] #target

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

# k_fold validation 적용 (연산이 오래 걸릴수도 있음)
# -> 연산이 너무 많이 걸리지 않는 선에서 최대 효율을 뽑을 필요가 있어보임

k_fold = KFold(random_state=50, n_splits=5, shuffle=True)

# 모델 설정
model = RandomForestClassifier()
#model = 다른 모델 사용가능

# 그리드 서치 파라미터 설정
# imbalanced 문제를 해결하기 위해서, boostrap 허용 -> van 카테고리를 다른 카테고리에 합치고 upsampling 해볼 필요도 있을 듯
param_grid = {#'max_iter':[50, 100, 200, 300],
              'n_estimators': [8,10,20],
              'max_depth': [10,15,24],
              'min_samples_split' : [15, 20, 25],
              'bootstrap' : ['True', 'False'],
              'min_samples_leaf': [14,20],
}

k_fold = KFold(random_state=50, n_splits=5, shuffle=True)

# 모델 설정
model = RandomForestClassifier()
#model = 다른 모델 사용가능(HistGradientBoosting, XGBboostingregressor ...)

# 그리드 서치 파라미터 설정
param_grid = {#'max_iter':[50, 100, 200, 300],
              'n_estimators': [200, 300],
              'max_depth': [30,40],
              'min_samples_split' : [25,30],
              'min_samples_leaf': [25,30,40],

              }

grid_search = GridSearchCV(estimator = model, 
                           param_grid = param_grid,
                           cv = 5)

grid_search.fit(x_train, y_train)
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

final_model.fit(x_train, y_train)
'''



