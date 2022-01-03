# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""### git merge 시
작업하신 파일을 commit 하실 때는 .py 파일로 업로드 해주시길 바랍니다.

* 코드 사용 시 약간의 디버깅 작업 후 작업해주세요~~
* 미처 코드에 포함되지 않은 내용은 추가해서 커밋부탁드립니다

"""

data = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/socar_reservation_triplog.csv')
data = data.sample(frac=1, random_state=0).reset_index(drop=True)

# 사용하지 않는 컬럼 제거
data.drop(['reservation_id', 'zone_address', 'car_id', 'zone_name', 'zone_lat', 'zone_lng', 'reservation_created_lat',
           'reservation_created_lng', 'zone_type1','zone_type2','zone_type3', 'trip', 'car_name','zone_address', 'zone_lat', 'zone_lng'], 1)

# 결측치 제거
data = data.dropna()

# 멤버 아이디 기준으로 중복 제거
data.drop_duplicates(['member_id_encrypted'])

data.head()

def trip_drop_duplicate(df):

    # trip의 지역구 중복 제거
    df['trip'] = df['trip'].apply(lambda x : ','.join(list(set(x.split(',')))))
    return df.copy()

def usage_time_calculate():
    
    df['reservation_return_at'] =  pd.to_datetime(df['reservation_return_at'], format='%Y-%m-%d %H:%M:%S')
    df['reservation_start_at'] =  pd.to_datetime(df['reservation_start_at'], format='%Y-%m-%d %H:%M:%S')
    df.dropna(how='any', inplace=True)

   # 사용시간 (분), 5분 미만 데이터는 제외
    df['usage_time'] = (df[x] - df[y]).astype('timedelta64[m]')

    # 5분 이상인 것 같습니다!
    df = df.loc[df['usage_time']>5]

    return data

def usage_period_calculate():

    data['usage_period'] = (data['reservation_start_at']-data['member_created_date'])
    data['가입후_이용기간']=data['가입후_이용기간'].dt.days

    return data

def divide_car_type(df, col):

    small_car = ['아반떼AD', '[쏘카세이브] 아반떼AD', '올뉴K3','아이오닉EV (제주)', '말리부', 
             '클리오', 'K5', 'SM6', '스팅어', '쏘나타DN8', '[쏘카세이브] K5', '쏘나타 뉴라이즈',
             '쏘나타 뉴라이즈(LPG)','K5 (LPG)', 'QM3', '[쏘카세이브] K5 (LPG)','벤츠 C200',
             'K7 (LPG)', '2016 말리부', '더뉴아반떼']

    for i in data.index:
        val = df.loc[i, col]
        for j in range(0, len(small_car)):
            if val == small_car[j]:
                df.loc[i, 'car_type'] = '소형차'
            else:
                df.loc[i, 'car_type'] = 'SUV'

divide_car_type(data, 'car_name')


# 각 지역별로 가장 많은 차종 데이터 찾기
def most_popular_car(region_data):
    df = pd.read_csv("./socar_reservation_triplog.csv")
    region_car_dict= {}
    try:
        for region in region_data:
            condition = (df['region'] == region)
            parsed_data = df.loc[condition]
            car = parsed_data['car_name'].value_counts(ascending=False).index.tolist()
            # print(car)
            region_car_dict[region] = car[0]
    except Exception as e:
        print(f"Error : {e}")
    print(region_car_dict)
    return region_car_dict
result_region_and_car = most_popular_car(region_list)

car = dict()
for k, v in result_region_and_car.items():
    if v in car:
        car[v] += 1
    else:
        car[v] = 1
print(car)

# 예약 주기
def get_cycle(member_df):
    start_time = member_df.sort_values('reservation_start_at').reservation_start_at
    cycles = start_time[1:].sub(start_time.values[:-1]).divide(np.timedelta64(1, 'D')).values
    return cycles

sample = df[df.member_id.eq(df.member_id.unique()[5000])]

get_cycle(sample)


# 동일한 데이터 테이블 사용 필요
# 처음 작업하신 코드를 baseline으로 사용