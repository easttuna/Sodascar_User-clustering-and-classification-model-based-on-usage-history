from sklearn.metrics import mean_squared_error
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.ensemble import RandomForestRegressor

# PCA를 적용한 실험과 PCA를 적용하지 않은 실험에서의 성능을 비교
# (multi class에서 차원 축소가 오히려 성능을 더 떨어지는 결과도 있다고 합니다.)


# 그리드 서치를 이용해서 여러 모델을 이용하고자 함.

RF = RandomForestRegressor(max_depth=24, min_samples_leaf=12,
                           min_samples_split=16, n_estimator=10)

