import umap
import pandas as pd
import numpy as np
from sklearn_som.som import SOM
from sklearn.metrics import silhouette_samples as ss
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler


# 멤버 테이블 로드
member = pd.read_csv('./data/member.csv')

# 클러스터링 피쳐 선정
cluster_features = ['wd_ratio', 'interval_med', 'usage_time_med', 'zone_gini', 'trip_gini', 'attraction_mean']
member_selected = member[['member_id'] + cluster_features].copy()

# 극단치 제거
member_selected = member_selected[member_selected.wd_ratio.ne(1) & member_selected.zone_gini.ne(0) & member_selected.trip_gini.ne(0)]
criteria = pd.DataFrame()
for col in cluster_features:
    values = member_selected[col]
    Q1 = values.quantile(0.25)
    Q3 = values.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5*IQR
    upper_bound = Q3 + 1.5*IQR

    criteria = pd.concat([criteria, values.between(lower_bound,upper_bound)], axis=1)
member_selected = member_selected[criteria.all(axis=1)]

# 피쳐 스케일링
scaler = StandardScaler()
member_normalized = scaler.fit(member_selected[cluster_features]).transform(member_selected[cluster_features])

# UMAP 차원축소
reducer = umap.UMAP(random_state=42, n_components=2, min_dist=0.25, n_epochs=500)
reducer.fit(member_normalized)
embedding = reducer.transform(member_normalized)

# SOM 클러스터링
num_features = embedding.shape[1]
som = SOM(m=2, n=2, dim=num_features, lr=0.1, max_iter=3000, random_state=42)
som.fit(embedding, epochs=100)

# 군집라벨 부여 (예측모델 정답 라벨)
cluster_label = som.predict(embedding)
result = member_selected.copy()
result['member type'] = cluster_label
result['emb_1'] = embedding[:,0]
result['emb_2'] = embedding[:,1]

# 군집 성능 점수 계산
sil_score = ss(embedding, result.pred)
sil_score
result['score'] = sil_score

# 5회 이용이력만으로 생성한 member테이블 로드
member5 = pd.read_csv(('./data/member_5records.csv'))

# 정답 라벨 태깅
member_5_record = member5.merge(result[['member_id', 'pred']], how='right', on='member_id')
member_full_record = member.merge(result[['member_id', 'pred']], how='right', on='member_id')

# 5회이용이력, 전체 이용이력으로 변수 생성 + 정답라벨 부여한 데이터셋 저장
member_5_record.to_csv('data/member_type_prediction_5record.csv', index=False)
member_full_record.to_csv('data/member_type_prediction_full_record.csv', index=False)
