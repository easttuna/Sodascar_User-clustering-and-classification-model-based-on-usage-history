! git pull하여 사용해주세요 

# SOCAR 이용이력 기반 고객 세분화와 초기 이용자 유형 예측모델
! SOCAR 이용이력 기반 고객 군집화? 및 초기 이용자 유형 분류?모델

## 프로젝트 소개

본 프로젝트에서는 SOCAR 고객들의 이용이력에 기반하여 설명가능하며, 비즈니스적으로 의미 있는 고객 유형을 도출하고자 하였습니다. 또한 이용자의 일부 이용이력으로 고객 유형을 예측하는 모델을 만듦으로써 신속하게 고객유형을 파악할수 있도록 하였습니다. 

## 프로젝트 수행 배경

- 쏘카 고객들은 업무, 일과, 여행 등 다양한 이용목적으로 쏘카를 이용함

> “이전에는 20대가 주로 시내에서 단거리 이동을 위해 카셰어링을 이용했다면 지금은 보다 넓은 연령층에서 출장이나 여행부터 출퇴근, 장보기, 차량 수리시 대차까지 등 이동이 필요한 모든 순간에 다양한 목적으로 쏘카를 이용하고 있음을 알 수 있습니다.” 출처: SOCAR Blog (2020.08.04. [https://blog.socar.kr/10370](https://blog.socar.kr/10370))
> 
- 시장 및 고객 규모가 커지고 고객의 이용행태 및 목적이 점차 다변화되어감에 따라 고객층을 더욱 잘게 세분화 하여 관리할 필요성이 생김
- 쏘카 이용이력에 기반하여 고객특성을 도출하고, 고객을 세분화하는 프레임워크를 수립함
    - 전체 고객 대비 각 고객 유형의 차지 비율, 이용비율을 종단, 횡단적으로 파악하여 고객 현황 관리가 가능함
    - 고객층별 이용행태를 확인하여 맞춤 상품 제공, 서비스 개선이 가능함

## 작업 개요
![image](https://user-images.githubusercontent.com/65028694/148731329-0ed979ad-090c-43c8-9ee2-f5315e8ef31f.png)
![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled.png)

### [STEP1.] ‘쏘카 이용정보’ 전처리 및 변수 가공

- 제공받은 쏘카 이용정보 테이블을 가공하여 각 ‘이용’의 특성과 목적을 나타내는 변수를 가공 및 생성함
- 기존재하는 컬럼을 변환하고  해당 이용자가 방문한 지역로그 (TripLog)를 통해 외부데이터를 매핑함

### [STEP2.] Meber별 이용정보 집계, Member Table 생성

- 이전 단계에서 정제된 쏘카 이용정보를 각 멤버별로 집계하여 각 멤버를 대표하는 변수를 생성함
- 이용정보 테이블의 단순 평균 뿐만 아니라 각 이용간의 간격 (이용 주기) 등 개별 이용정보 record로는 알 수 없는 Member의 특성을 파악함

### [STEP3.] Member 클러스터링 및 고객 유형 해석

- Member 변수에서 member의 유형을 구분해낼 수 있는 주요변수를 선정하여 차원축소, 클러스터링 알고리즘을 사용하여 member를 군집화함
- 군집화된 member에 대한 EDA를 바탕으로 각 군집을 ‘**고객 유형**’으로 해석함

### [STEP4.] 고객 유형 예측 모델 생성 및 검증

- ‘**고객 유형’**을 정답라벨로 부여하고, member의 특성으로 이를 예측하는 Multiclass Classification 모델을 만들고 검증함
- 이때 member의 특성은 이용정보에 존재하는 각 member 별 최초 5회의 이용이력만으로 생성하여 예측결과의 활용이 유의미하도록 함 
(cf. member 군집화를 위하여 [STEP2.]에서는 약 1년간의 모든 이용정보를 사용하여 member 변수를 생성하였음)

## [STEP1.] ‘쏘카 이용정보’ 전처리 및 변수 가공

### 1) 전처리 및 변수 생성

- 쏘카 이용정보 테이블에는 총 751,548행이 존재하며, member의 고유식별자를 포함하여 22개의 컬럼이 존재함
- 30분 미만의 이용 및 member나이, member 성별, Trip 정보가 존재하지 않는 행은 제외하였음
- 7개의 기존 변수를 가공하여 6개의 새로운 변수를 생성하였음
- TripLog에 외부데이터를 매핑해 attraction_score, restaurant_score, shopping_score를 도출한 과정은 아래 추가 설명함

![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled%201.png)

### 2) Trip의 관광지, 식당, 쇼핑점 점수 생성 방법

- 각 이용정보 별 방문한 지역이 ‘시군구’의 단위로 존재함
- 방문지의 이름만으로는 이용의 특성을 발견할 수 없으므로, 이용의 특성을 반영하는 수치형 정보로 변환함
- 한국문화정보원의 ‘**국내여행 소비 역세권지도**’에 시군구별 관광지 수, 음식점 수, 쇼핑점 수와 인구수가 존재함 ([https://www.bigdata-culture.kr/bigdata/user/data_market/detail.do?id=98124fc8-5024-4b27-b9a7-5631021ed5a8](https://www.bigdata-culture.kr/bigdata/user/data_market/detail.do?id=98124fc8-5024-4b27-b9a7-5631021ed5a8))
- TripLog상의 가 방문지역별 인구 천명 대비 관광지, 음식점, 쇼핑점 수를 구한 뒤, 모든 지역에 대해 평균내어 해당 이용의 전반적인 방문지 특성을 산출함

![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled%202.png)

### 3) 결과

- [STEP1.]을 통해 507,800 rows, 19 columns의 테이블 ‘socar_usage_processed’를 생성하여 다음 단계에서 사용함

![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled%203.png)

## [STEP2.] Member별 이용정보 집계, Member Table 생성

- 각각의 member는 복수의 이용정보를 가지고 있으며, 이를 해당 member의 특성을 잘 표현할 수 있는 방향으로 종합하여 member 변수를 생성해야함
- 수치형 변수는 각 member별로 ‘mean’ ,’median’, ‘std.’ 등 단순 기술통계적 집계가 가능하나 (ex. member 평균 이용시간: 해당 member의 모든 이용시간의 평균) 대여존, 방문지이력(TripLog) 등 범주형 변수는 불가능함
- 범주형 변수를 처리한 방법을 위주로 Member Table 생성 과정을 설명함

### 1) Gini Index를 활용한 예약존 다양성, 방문지 다양성 변수 생성

- **배경**
    - ‘유사한 이용을 반복하는 member’와 ‘이용행태가 다양한 member’를 구분하기 위한 지표를 도출하고자 함
    - 단순히 예약해본 존과 방문해본 지역의 가짓수를 count 할 시, 각 범주가 차지하는 비중이 손실됨
        - 예시
            1. 두명의 member x,y는 총 5개의 zone을 이용해봄
            2. x는 대부분의 이용을 5개 중 한곳에서 하고, 나머지 4개의 zone은 한번씩만 이용해봄
            3. y는 비슷한 5개 존을 골고루 이용함
            4. ‘이용의 다양성’ 측면에서 x,y는 다른 특성을 가지고 있으나 이용해본 zone의 count는 5로 동일
    - 각 범주의 발생확률로 다양성을 계산할 수 있는 **불순도 지표** Gini Index를 사용함
    
- **계산 과정**
    - 한 memeber의 모든 이용정보에 존재하는 예약존(zone_name), 방문지(trip) 내역 통합
    - (각존의 예약건수 / 전체 이용건수)를 계산하여, 각 존의 예약확률로 변환
    - Gini index 연산으로 다양성(불순도) 지수 도출
    - **하나의 zone만 이용할 시, Gini Index는 0으로 최저값을 가지며, 여러 존을 유사한 비중으로 이용할 수록 1에 가깝게 증가함**
    
    ```python
    def zone_gini(zone_name):
        """
        각 member별 이용한 zone의 gini index 반환
        """
        probs = zone_name.value_counts(normalize=True).values
        gini = 1- np.power(probs, 2).sum()
        return gini
    ```
    
- 실제 데이터 예시
    
    ![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled%204.png)
    
- 위의 연산을 예약존 뿐만아니라 TripLog에도 동일하게 적용하여 다음의 두 변수를 도출함
    - **zone_gini**: 각 member가 이용해본 예약존의 다양성
    - **region_gini**: 각 member가 이용중 방문한 지역의 다양성

### 2) 이용목적과 관련된 추가 변수 생성

- zone_gini, region_gini이외에 [STEP3.] 군집분석에 활용한 추가 변수는 4가지임
    - **wd_ratio: 이용시점의 평일 비율**
        - 산식: (평일에 시작한 이용 수) / (전체 이용 수)
    - **interval_med: 이용주기의 중앙값**
    - **usage_time_med: 모든 이용정보의 이용시간 중앙값**
    - **attraction_mean: 모든 이용정보의 attraction_score 평균**
- 4개의 변수 모두 member의 **이용목적을 내포**하고 있는 변수이며 각 변수에 따른 member 유형의 가설은 다음과 같음
    - wd_ratio가 높을 수록 레저보다는 평일 업무나 생활 등 필요에 의해 사용하는 member 일것
    - interval_med가 클수록 출장 및 여행 등, 빈도가 낮은 용도를 위해 쏘카를 이용할 것
    - usage_time_med가 작을 수록 지역내 단거리 이용을 위해 이용할 것
    - attraction_mean이 클수록 주로 여행목적으로 쏘카를 이용할 것

### 3) 결과

- [STEP2.] 단계에서 ~~명의 member에 대한 ~~가지 변수를 가진 ‘member’ Table을 생성함
- member Table의 모든 속성은 아래와 같음 (군집화에 사용된 변수는 붉은색 처리)

![Untitled](%E1%84%8C%E1%85%A6%E1%84%8E%E1%85%AE%E1%86%AF%E1%84%8C%E1%85%A1%E1%84%85%E1%85%AD%2072aa660ab14c4d75b7814c3a21200109/Untitled%205.png)

## [STEP3.] Member 클러스터링 및 고객 유형 해석

### 1)  변수선별

### 2) UMAP 차원축소

### 3) SOM (Self Organizing Map) 클러스터링

## [STEP4.] 고객 유형 예측 모델 생성 및 검증
- 클러스터링을 통해 얻은 네개의 군집을 레이블로 하여 사용 이력이 5회인 초기 이용자들의 유형을 분류하는 모델을 생성함  
- 군집 분류를 위해 사용한 6개의 컬럼을 feature로 사용하였으, member_type의 분류를 타겟으로 함  

### 1) 학습과 검증 과정
- feature 데이터를 학습하기 위해, 분류에 유용한 standard scaler를 적용하였음.  
- 또한, 레이블 간의 불균형 문제를 해결하기 위해, 학습 데이터에 SMOTE OverSampling을 사용하였음.  
- train set과 test set은 8:2 구성으로 사용하였으며, train set은 10881개, test setd은 2721개 데이터를 사용하였음.  
- 학습에는 5 k_fold validation과 GridSearchCV를 사용하였으며, 모델은 RandomForest Classifier, XGBoost Classifier, LGBM Classifier 등 7가지 모델을 사용하고 성능을 비교하였음.  

### 2) 성능 평가 및 분석
