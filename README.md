
# SOCAR 이용이력 기반 유저 군집화 및 분류 모델

## `프로젝트 소개`

`본 프로젝트에서는 SOCAR 유저들의 이용이력에 기반하여 설명가능하며, 비즈니스적으로 의미 있는 유저 유형을 도출하고자 하였습니다. 또한 유저의 일부 이용이력으로 유저 유형을 예측하는 모델을 만듦으로써 신속하게 유저유형을 파악할수 있도록 하였습니다. `

## `프로젝트 수행 배경`

- 쏘카 유저들은 업무, 일과, 여행 등 **다양한 이용목적**으로 쏘카를 이용함

> “이전에는 20대가 주로 시내에서 단거리 이동을 위해 카셰어링을 이용했다면 지금은 **보다 넓은 연령층에서 출장이나 여행부터 출퇴근, 장보기, 차량 수리시 대차까지** 등 이동이 필요한 모든 순간에 다양한 목적으로 쏘카를 이용하고 있음을 알 수 있습니다.” 출처: SOCAR Blog (2020.08.04. [https://blog.socar.kr/10370](https://blog.socar.kr/10370))
>  
- 시장 규모가 커지고 **유저의 이용행태 및 목적**이 점차 **다변화**되어감에 따라 유저층을 더욱 잘게 군집화 하여 관리할 필요성이 생김
- **쏘카 이용이력**에 기반하여 **유저특성을 도출**하고, **유저를 군집화**하는 프레임워크를 수립함
    - 전체 유저 대비 각 유저 유형의 차지 비율, 이용비율을 종단, 횡단적으로 파악하여 **유저 현황 관리**가 가능함
    - 유저 유형별 이용행태를 확인하여 **맞춤 상품 제공, 서비스 개선**이 가능함  

## `작업 개요`

![framework](https://user-images.githubusercontent.com/79245556/149143424-379e2669-3843-4085-ac0f-3c1648e7fa8c.png)

### [STEP1.] ‘쏘카 이용정보’ 전처리 및 변수 가공

- 쏘카 이용정보 테이블처리, -> 각 ‘이용’의 특성과 목적을 나타내는 변수를 가공 및 생성
- 기존재하는 컬럼을 변환, 유저가 방문한 지역정보를 통해 외부데이터를 매핑

### [STEP2.] user별 이용정보 집계, User Table 생성

- 쏘카 이용정보를 각 user별로 집계하여 각 user를 대표하는 변수 생성
- 각 이용간의 간격 (이용 주기) 등 개별 이용정보 record로는 알 수 없는 user의 특성을 파악

### [STEP3.] user 클러스터링 및 유형 해석

- user 변수에서 user의 유형을 구분해낼 수 있는 주요변수 선정, 차원축소&클러스터링 알고리즘을 사용하여 user 군집화
- 군집화된 user에 대한 EDA를 바탕으로 각 군집을 ‘**user 유형**’으로 해석

### [STEP4.] user 유형 예측 모델 생성 및 검증

- ‘**user 유형**’을 정답라벨로 부여하고, user의 특성으로 이를 예측하는 Multiclass Classification 모델 생성 및 검증
- user의 특성은 이용정보에 존재하는 각 user 별 **최초 5회의 이용이력**만으로 생성하여 예측결과의 활용 가능성 확인  
(cf. user 군집화를 위하여 [STEP2.]에서는 약 1년간의 모든 이용정보를 사용하여 user 변수를 생성하였음)  





## `[STEP1.] ‘쏘카 이용정보’ 전처리 및 변수 가공`

### 1) 전처리 및 변수 생성

- 일부 속성을 가공하여 6개의 새로운 변수를 생성하였으며, 30분 미만의 이용 및 방문지가 정보가 없는 행을 제거하였음
- 방문지 정보에 **외부데이터를 매핑**해 attraction_score, restaurant_score, shopping_score를 도출한 과정은 아래 추가 설명함

![usage_feature_gen_resized](https://user-images.githubusercontent.com/79245556/149087367-5ab96e95-20e3-45fb-a16e-c03fa9f7d2ae.png)


### 2) 이용정보의 관광지, 식당, 쇼핑점 점수 생성 방법

- 각 이용정보 별 방문한 지역이 ‘시군구’의 단위로 제공됨
- 방문지의 이름만으로는 이용의 특성을 발견할 수 없으므로, 이용의 특성을 반영하는 **수치형 정보**로 변환함
- 한국문화정보원의 ‘**국내여행 소비 역세권지도**’에 시군구별 관광지 수, 음식점 수, 쇼핑점 수와 인구수가 존재함 ([https://www.bigdata-culture.kr/bigdata/user/data_market/detail.do?id=98124fc8-5024-4b27-b9a7-5631021ed5a8](https://www.bigdata-culture.kr/bigdata/user/data_market/detail.do?id=98124fc8-5024-4b27-b9a7-5631021ed5a8))
- 방문지역별 인구 천명 대비 관광지, 음식점, 쇼핑점 수를 구한 뒤, 모든 지역에 대해 평균내어 해당 이용의 **전반적인 방문지 특성**을 산출함

![region_score_example](https://user-images.githubusercontent.com/79245556/149073677-208e9fca-0524-42ea-84d4-ad707492f8ee.png)

## `[STEP2.] user별 이용정보 집계, User Table 생성`

- 각각의 user는 **복수의 이용정보**를 가지고 있으며, 이를 해당 user의 특성을 잘 표현할 수 있는 방향으로 종합하여 user 변수를 생성해야함
- 이용이력이 적은 user의 경우 소량의 정보로 user의 특성이 잘못 파악될 가능성이 있으므로, 이용이력이 **최소 5회** 존재하는 user 만을 대상으로 user변수를 생성하였음
- 수치형 변수는 각 user별로 ‘mean’ ,’median’, ‘std.’ 등 단순 기술통계적 집계가 가능하나 (ex. user 평균 이용시간: 해당 user의 모든 이용시간의 평균) 대여존, 방문지이력 등 범주형 변수는 불가능함
- **범주형 변수**를 처리한 방법을 위주로 user Table 생성 과정을 설명함

### 1) Gini Index를 활용한 예약존 다양성, 방문지 다양성 변수 생성

- **배경**
    - ‘**유사한 이용을 반복하는 user**’와 ‘**이용행태가 다양한 user**’를 구분하기 위한 지표를 도출하고자 함
    - 단순히 예약해본 존과 방문해본 지역의 가짓수를 count 할 시, **각 범주가 차지하는 비중이 손실됨**
        - **예시**
            1. 두명의 user x,y는 총 5개의 zone을 이용해봄
            2. x는 대부분의 이용을 5개 중 한곳에서 하고, 나머지 4개의 zone은 한번씩만 이용해봄
            3. y는 비슷한 5개 존을 골고루 이용함
            4. ‘이용의 다양성’ 측면에서 x,y는 다른 특성을 가지고 있으나 이용해본 zone의 count는 5로 동일
    - 각 범주의 발생확률로 다양성을 계산할 수 있는 **불순도 지표** Gini Index를 사용함
    
- **계산 과정**
    - 한 user의 모든 이용정보에 존재하는 예약존, 방문지 내역 통합
    - (각존의 예약건수 / 전체 이용건수)를 계산하여, 각 존의 예약확률로 변환
    - Gini index 연산으로 다양성(불순도) 지수 도출
    - **하나의 zone만 이용할 시, Gini Index는 0으로 최저값을 가지며, 여러 존을 유사한 비중으로 이용할 수록 1에 가깝게 증가함**
    
    ```python
    def zone_gini(zone):
        """
        각 user별 이용한 zone의 gini index 반환
        """
        probs = zone.value_counts(normalize=True).values
        gini = 1- np.power(probs, 2).sum()
        return gini
    ```
    
- **산출 예시**

![gini_example](https://user-images.githubusercontent.com/79245556/149144001-55cc79a5-bbea-46c1-b691-a0eaefdf35fa.png)

- 위의 연산을 예약존 뿐만아니라 방문지 정보에도 동일하게 적용하여 다음의 두 변수를 도출함
    - **zone_gini**: 각 user가 이용해본 예약존의 다양성
    - **region_gini**: 각 user가 이용중 방문한 지역의 다양성

### 2) 이용목적과 관련된 추가 변수 생성

- zone_gini, region_gini이외에 [STEP3.] 군집분석에 활용한 추가 변수는 4가지임
    - **wd_ratio: 이용시점의 평일 비율**
        - 산식: (평일에 시작한 이용 수) / (전체 이용 수)
    - **interval_med: 이용주기의 중앙값**
    - **usage_time_med: 모든 이용정보의 이용시간 중앙값**
    - **attraction_mean: 모든 이용정보의 attraction_score 평균**
    
    
    💡 `이용주기 및 이용시간에는 극단치가 포함된 경우가 많기 때문에, 각 user의 평범한 이용주기 및 이용시간을 산출하기 위해 산술평균이 아닌 중앙값을 사용하였음`
    

    
- 4개의 변수 모두 user의 **이용목적을 내포**하고 있는 변수이며 각 변수에 따른 **user 유형의 가설**은 다음과 같음
    - **wd_ratio**가 높을 수록 레저보다는 평일 업무나 생활 등 필요에 의해 사용하는 user 일것
    - **interval_med**가 클수록 출장 및 여행 등, 빈도가 낮은 용도를 위해 쏘카를 이용할 것
    - **usage_time_med**가 작을 수록 지역내 단거리 이용을 위해 이용할 것
    - **attraction_mean**이 클수록 주로 여행목적으로 쏘카를 이용할 것

## `[STEP3.] user 클러스터링 및 유형 해석`

- 클러스터링에 사용할 user 특성변수간의 **선형관계가 작아**, 서로 **다른 특성**을 대변해주고 있음을 알 수 있음
- 극단치를 제거하여, point간의 거리 측정하는데 영향을 주지 않도록하였음
- 특성 변수 간의 상관 관계를 나타낸 그래프는 아래와 같음
<center><img src="https://user-images.githubusercontent.com/79245556/149090911-f055b3ff-f08b-4384-8ad4-7d453e043b09.png"></center>  
    
### 1) UMAP 차원 축소

- 클러스터링 알고리즘은 고차원의 데이터에 영향을 받음
- UMAP (Uniform Manifold Approximation and Projection for Dimension Reduction)은 point 들의 연관구조를 잘 유지한 채로 **고차원의 데이터를 저차원에 투영**하는 효과적인 알고리즘임
- UMAP을 이용해, 6차원의 데이터를 2차원 공간에 투영하였음  
<center><img src="https://user-images.githubusercontent.com/79245556/149080893-d19afe49-a8a8-43fd-ad37-ed4874150fca.png"></center>  


### 2)  SOM 클러스터링

- **HDBSCAN**과 같은 밀도기반 알고리즘을 시도하였으나, 데이터포인트의 군집구조가 명확하지 않아 군집화가 잘 이루어지지 않았음
- user들의 특성이 유형에 따라 **흑백으로 명확히 구분**되기보다, **중간적 성향을 띈 회색영역**에도 많은 user가 분포하기 때문으로 보임
- 저차원 격자에 point를 대응시키는 SOM (Self Organizing Map)알고리즘으로 군집을 할당하였음
- 배정할 격자공간을 3x1, 2x2, 3x2, 4x2, 3x3 등으로 조정해가며, 군집별 평균 silhouette score가 0.3 이상이며, 모든 point의 silhouette score 평균이 가장 높은 공간 수를 선택하였음
- **최적 파라미터에 따라 산출된 군집은 총 4개이며, 각 군집의 point 수와 silhouette score는 아래와 같음**

![cluster_result](https://user-images.githubusercontent.com/79245556/149080918-e14c8026-eb08-4754-b66b-3273318992ab.png)


### 3) 군집별 속성 EDA

- 군집이 명확한 경계로 나누어지지 않았기 때문에  개별 point의 silhouette score가 0.3 이상인 경우만을 선택해 시각화 하였으며, 각 군집별 변수 분포를 확인하며 군집의 특성을 해석하였음
    
![cluster_in_2dim](https://user-images.githubusercontent.com/79245556/149150999-814e963e-4be6-45d2-b556-57a054d50e52.png)

    
- **군집B는 예약존과 방문지의 지니계수가 낮으므로 대여존과 방문지가 타 군집에 비해 정형적임**

![cluster_hist1](https://user-images.githubusercontent.com/79245556/149151042-8be101f2-363a-42e8-aefd-72525a3f764f.png)


- **군집A, B는 평일 대여의 비율이 높고, 비교적 짧은 주기로 이용함**
- **군집D는 주말 대여 비율이 높고, 가장 대여주기가 긴 군집임**

![cluster_hist2](https://user-images.githubusercontent.com/79245556/149151045-10475c5d-1375-4897-abff-43368a437725.png)

- **군집 C는 타 군집에 비해 1회 이용시 긴 시간을 대여하고, 관광지가 많은 지역을 방문함**

![cluster_hist3](https://user-images.githubusercontent.com/79245556/149151046-3a734ea3-75f0-4274-b35a-db9562f31c71.png)

### `4) 군집결과 종합 및 member 유형화`

- 위의 결과를 종합하여, 다음과 같이 쏘카 이용 user의 유형을 해석하였음

**cluster A** : **잦은 빈도로 평일 위주 다양한 구간을 이용하는 유형** -> **업무 및 생활 보조형**

**cluster B** : **잦은 빈도로 평일 위주 정해진 구간을 이용하는 유형** -> **통근 보조형**

**cluster C** : **한번 이용시 오랫동안, 관광지를 다니는 유형** -> **여행형**

**cluster D** : **낮은 빈도로 주말 위주 이용하는 유형** -> **주말피크닉형**


💡 `유형이 분류된 user (이용이력 5회 이상)는 전체 user 수에 8% 가량에 불과하지만, 전체 이용횟수의 36%가량을 차지하므로 유형세분화를 기반으로 타게팅 전략을 수립하는 것이 비즈니스적으로 유의미할 것임`


## `[STEP4.] user 유형 예측 모델 생성 및 검증`
- **클러스터링을 통해 얻은 네개의 군집**을 **정답 레이블**로 하여 각 **user의 5회 이용이력**만을 바탕으로 user변수를 생성하여 user들의 유형을 분류하는 모델을 생성함  
- 군집 분류를 위해 사용한 6개의 컬럼을 feature로 사용하였으며, user_type의 분류를 타겟으로 함  
- 비교를 위해 **full record**(각 user의 모든 이용이력), **5 record**(앞선 5회의 이용이력)으로 생성한 user 변수를 input data로 한 모델을 비교하였음

### 1) 학습과 검증 과정
- feature 데이터를 학습하기 위해, 분류에 유용한 standard scaler를 적용하였음
- 또한, 레이블 간의 불균형 문제를 해결하기 위해, 학습 데이터에 SMOTE OverSampling을 사용하였음
- train set과 test set은 8:2 구성으로 사용하였으며, train set은 10881개, test setd은 2721개 데이터를 사용하였음
- 학습에는 5 k fold validation과 GridSearchCV를 사용하였으며, 모델은 Logistic Regression과 트리 기반 6가지 모델을 사용하고 성능을 비교하였음
- 학습 결과, 250개의 분류기를 양상블 학습한 Random Forest model에서  full record와 5record에서 각각 **train acc 93.08%와 67.43%, test acc 92.61%와 67.43%** 으로 가장 좋은 성능을 보였음

### 2) 성능 평가 및 분석  
- full record와 5record 성능 비교  
  - **full record** 성능 평가  
![image](https://user-images.githubusercontent.com/65028694/149093307-714908bc-9226-41f7-b734-245f6776ca63.png)![image](https://user-images.githubusercontent.com/65028694/149146714-6d5b41b5-7c8e-45f6-adac-dd3cfa2f9f80.png)  
  - **5 record** 성능 평가  
![image](https://user-images.githubusercontent.com/65028694/149094215-74e71c00-86d3-41aa-acbc-9ded2309b06b.png)![image](https://user-images.githubusercontent.com/65028694/149146824-f28960e3-3b0e-4b89-b9bc-e7f79a0a8077.png)  
  - 성능 평가는 Random Forest 학습한 Ensemble model의 test 결과에 기초함
  - full record 데이터와 5 recond 데이터를 사용하여 각각 학습 및 추론을 수행한 결과, full record 데이터를 가지고 학습한 결과에서 뚜렷한 성능을 보인다는 것을 확인할 수 있음
  - 반면, **full record**의 경우에 비해 **5 record** 데이터는 이용자의 전체 이력을 사용하지 않고 **초기 5회 이력**만을 사용하였기 때문에 군집의 대표성을 확인하는 것에는 다소 부족해 보임

- full record와 5 record confusion matrix 결과 비교     
  <img src="https://user-images.githubusercontent.com/65028694/149147565-e4503379-8f61-4293-8e29-0253e0578f75.png" width="400" height="300">
  <img src="https://user-images.githubusercontent.com/65028694/149145778-04df5fe3-9413-47f7-95dd-a3707b58c91a.png" width="400" height="300">  

  - full record와 5 record 데이터를 사용하여 confusion matrix를 살펴본 결과, full record의 경우에 비해 5 record 데이터에서 실제 군집이 B이나, 군집을 A으로 예측한 일부 결과를 확인할 수 있음. 또한, 실제 군집이 C이나, 예측한 군집이 B 또는 C로 예측한 일부도 확인할 수 있음  
  - 위와 같은 결과를 통해, '**통근 보조형**'과 '**업무 및 생활보조형**'이 비슷한 패턴을 보이고 있음을 의미하며, '**주말 피크닉**'이 '**여행형**', '**통근 보조형**' 사이에서 일부 비슷한 양상을 보인다는 것을 확인할 수 있음  

- feature importance  변화 비교  
![image](https://user-images.githubusercontent.com/65028694/149095111-cc8c0413-774f-4576-8c63-38ce91cdab3a.png)
![image](https://user-images.githubusercontent.com/65028694/149095151-384c77e1-ffc6-45a5-b42f-d2d69999dd51.png)
  - **full record** 데이터로 학습한 결과,'interval_med','usage_time_med','attraction_mean'순으로 고르게 중요도를 차지하고 있는 반면, **5 record** 데이터로 학습한 결과, 'interval_med','usage_time_med','attraction_mean'외 다른 피쳐는 큰 차이로 적은 중요도를 차지하는 모습을 보임
  - 이것은 전체 이용 내역과 초기 이력을 기반한 군집 분류에 있어, **사용 빈도와 장-단거리 여부, 일상-여행 여부**가 중요한 요소임을 나타냄


## `결론`
>- 차량 공유의 시장규모가 커지며 이용자들의 **차량 이용 목적 및 행태** 또한 다양해졌습니다.  
>- 본 프로젝트는 쏘카 유저의 이용행태로부터 **이용특성**을 뚜렷히 나타내는 변수를 생성하고, 이에기반해 **유저 유형을 군집화** 하였습니다.  
>- 또한 **일부의 이용이력**만으로 전체 이용이력으로 부여된 **정답라벨(이용자 유형)를 예측**하는 모델을 생성하여, **유저유형을 빠르게 파악하고 대응**하는데에 도움이되고자 하였습니다.  
>- 희소한 정보를 바탕으로한 예측모형이 높은 정확도를 보이지는 않지만 classification threshold을 조정해 **presicion을 높임으로써** 보다 **확실한 예측을 활용한 유저 접근**이 가능할 것입니다. 
>- 본 프로젝트에서는 군집의 시계열(계절적) 변화 패턴을 확인하지 않았지만 향후 연구에서는 **시계열적 변화를 추적**하고 member가 아닌 **usage를 대상으로도 군집분석**을 하여 보다 이용현황을 보다 상세히 파악할 수 있을 것입니다.  
>- 유저 유형 군집화 및 예측 프레임워크에 포함된 아이디어가 보다 상세한 이용이력을 바탕으로한 **개인화 추천**에도 도움이 될 수 있기를 바랍니다.
