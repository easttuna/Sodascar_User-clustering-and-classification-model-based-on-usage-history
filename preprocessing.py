# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 경로설정
# data = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/socar_reservation_triplog.csv', 
#                    parse_dates=['reservation_start_at', 'reservation_return_at', 'member_created_date'])

data = pd.read_csv('../data/socar_reservation_triplog.csv', 
                   parse_dates=['reservation_start_at', 'reservation_return_at', 'member_created_date'])

# 사용하지 않는 컬럼 제거
drop_col = ['reservation_id', 'zone_address', 'car_id', 'zone_name', 'zone_lat', 'zone_lng', 
            'reservation_created_lat', 'reservation_created_lng', 'zone_type1', 'zone_type2', 'zone_type3', 
             'zone_address', 'zone_lat', 'zone_lng']

data = data.drop(columns=drop_col)

# 긴 컬럼명 변경
data = data.rename(columns={'member_id_encrypted':'member_id'})

# 결측치 제거
data = data.dropna()

# 이용시간(분)컬럼 생성 및 10분 이상 이용만 선택
data['usage_time'] =  data.reservation_return_at.sub(data.reservation_start_at).divide(np.timedelta64(1, 'm'))
data = data[data.usage_time.ge(10)]

# 가입기간(일)컬럼 생성 (예약시작시간 - 가입시간)
data['usage_period'] =  data.reservation_start_at.sub(data.member_created_date).divide(np.timedelta64(1, 'D')).astype(int)


# 차종 분류 -> 추가 세분화 고려
def classify_car_type(car_name):

    NON_SUV = ['아반떼AD', '[쏘카세이브] 아반떼AD', '올뉴K3','아이오닉EV (제주)', '말리부', 
             '클리오', 'K5', 'SM6', '스팅어', '쏘나타DN8', '[쏘카세이브] K5', '쏘나타 뉴라이즈',
             '쏘나타 뉴라이즈(LPG)','K5 (LPG)', 'QM3', '[쏘카세이브] K5 (LPG)','벤츠 C200',
             'K7 (LPG)', '2016 말리부', '더뉴아반떼']

    if car_name in NON_SUV:
        return 'non_SUV'
    else:
        return 'SUV'
data['car_type'] = data.car_name.map(classify_car_type)

# # 처리한 테이블 저장
# data.to_csv('../data/socar_usage_processed.csv', index=False)