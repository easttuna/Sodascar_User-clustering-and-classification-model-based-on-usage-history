
import os
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE, RandomOverSampler
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score,recall_score,f1_score,confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

root = os.path.join(os.getcwd(), "drive", "MyDrive", "Colab Notebooks", "member_type_prediction_full_record.csv")
df = pd.read_csv(root)

# 의미없는 컬럼과 원핫인코딩 칼럼 삭제
drop_col = [...]
df = df.drop(columns=drop_col)

x = df.drop(['member_type'], axis=1) #feature
y = df['member_type'] #target

#  standard scaler적용
standardScaler = StandardScaler()
XminmaxScaled = standardScaler.fit_transform(x)

x_train, x_test, y_train, y_test = train_test_split(XminmaxScaled, y, test_size=0.2)

# imbalanced data 오버 샘플링 처리
x_resampled, y_resampled = SMOTE(random_state=0).fit_resample(x_train, y_train)
y_resampled.value_counts()

# k_fold validation 적용 (연산이 오래 걸릴수도 있음)
# -> 연산이 너무 많이 걸리지 않는 선에서 최대 효율을 뽑을 필요가 있어보임
k_fold = KFold(random_state=50, n_splits=5, shuffle=True)

# 모델 설정
#model = RandomForestClassifier()
model = XGBClassifier()
#model = LGBMClassifier()

# 그리드 서치 파라미터 설정

# RandomForest 파라미터
'''
param_grid = {
              'n_estimators': [200, 250],
              'max_depth': [25,30],
              'min_samples_split' : [15,20],
              'bootstrap':['False','True'],
              'min_samples_leaf': [10,15],
              }
'''   

#XGBoost 파라미터
param_grid = {
              'n_estimators': [400,450],
              'max_depth':[8,10],
              'min_child_weight':[5,8], #min sample leaf
              'nthread':[8], #스레드 갯수 고정
              'colsample_bytree':[0.8,0.9], #max feature
              'objective':['multi:softmax']
              }


'''
#lightGBM 파라미터
param_grid = {
              'n_estimators': [200],
              'min_child_samples':[1,2], #과적합을 방지하는 파라미터
              'max_depth':[7,8,10],
              'num_leaves':[70],
              'sub_sample':[0.2,0.4] #과적합 방지하기 위해 데이터 샘플링 하는 비율
              }
'''

grid_search = GridSearchCV(estimator = model, 
                           param_grid = param_grid,
                           cv = k_fold)

grid_search.fit(x_resampled, y_resampled)
best_param = grid_search.best_params_

# 최적 파라미터와 결과
print(best_param)
print('best score : {}'.format(grid_search.best_score_))

# 최종 모델 평가
from sklearn.metrics import accuracy_score, precision_score,recall_score,f1_score,confusion_matrix, roc_auc_score
final_model = grid_search.best_estimator_
final_pred = final_model.predict(x_test)

def metric(y_test, pred):
    accuracy = accuracy_score(y_test,pred)
    precision = precision_score(y_test,pred, average='macro')
    recall = recall_score(y_test,pred, average='macro')
    f1 = f1_score(y_test,pred, average='macro')
    print('정확도 : {0:.6f}, 정밀도 : {1:.6f}, 재현율 : {2:.6f}'.format(accuracy,precision,recall))
    print('f1-score : {0:.6f}'.format(f1))

metric(y_test, final_pred)

# confusion matrix 확인하기


con_mat = confusion_matrix(y_test, final_pred)
sns.heatmap(con_mat, square=True, annot=True, fmt='d')
plt.xlabel('true_label')
plt.ylabel('predicted_label')
plt.xticks(rotation=45)
plt.show()

# 특성 중요도 추출하기
diction= {}
for name, score in zip(df.columns, final_model.feature_importances_):
    #print(name, score)
    diction[name]=score
    
feature_importance = pd.DataFrame(list(diction.items()), columns=['features', 'score'])

plt.figure(figsize=(10, 8))
sns.barplot(x='features', y='score', data=feature_importance)
plt.title('Feature Importances', fontsize=15)
plt.show()

