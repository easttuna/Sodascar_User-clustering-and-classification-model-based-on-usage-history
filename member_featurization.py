# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

"""
<usage 데이터 member 데이터로 집계>

member_age: pass (usage 값 그대로 전달) 
member_gender: pass
member_total_distance: pass

is_vroom:  총이용대비 부름 비율(float)

usage_time: mean, std
usage_period: max
num_trips: mean, std

car_type: mode(최빈 class), Gini index (얼마나 다양하게 이용)
attraction, restaurant, shopping: mean, std, min, max
"""

# Load processed usage table
data = pd.read_csv('./data/socar_usage_processed.csv', 
                   parse_dates=['reservation_start_at', 'reservation_return_at', 'member_created_date'])

# transform hashed member identifier to int value
member_encoder = {hash:idx for hash, idx in zip(data.member_id.unique(), range(1, len(data)+1))}
data.member_id = data.member_id.map(member_encoder)

# slice usage of members having more than 5 usage
row_cnt = data.groupby('member_id')['region'].count()
valid_members =  row_cnt[row_cnt.ge(5)].index
data = data[data.member_id.isin(valid_members)]


def mode_type(car_type):
    """
    member의 전체 이용현황을 받아
    가장 이용빈도가 높았던 차종 유형을 반환
    """
    return car_type.mode()[0]

def gini_index(car_type):
    """
    member의 전체 이용현황을 받아
    이용 차종의 불순도(다양성) 반환
    """
    probs = car_type.value_counts(normalize=True).values
    gini = 1- np.power(probs, 2).sum()
    return gini

# 이용기간 구하기 위한 기준시간: member와 무관하게 보유한 데이터의 가장 마지막 usage 출발시간
BOUND = data.reservation_start_at.max()

def usage_span(reservation_dt):
    """
    데이터상 각 유저의 '이용기간'을 구함
    단순 이용빈도 이외에 기간대비 이용빈도를 계산하기 위함
    """
    global BOUND
    first_timestamp =  reservation_dt.sort_values().iloc[0]
    # 이용기간: 기준시간 - 데이터상 각 member의 첫번째 이용시작시간
    usage_span = (BOUND - first_timestamp) / np.timedelta64(1, 'D')
    return int(usage_span)


def interval_features(member_df):
    """
    각 member별 이용이력의 시간간격 리스트를 생성,
    시간간격의 평균과 표준편차를 반환
    """
    start_time = member_df.sort_values()
    intervals = start_time[1:].sub(start_time.values[:-1]).divide(np.timedelta64(1, 'D')).values
    return intervals.mean(), intervals.std()

def wd_ratio(reservation_dt):
    """
    각 member별 대여일의 평일 비율 반환
    """
    return reservation_dt.dt.weekday.map(lambda dow: 0 if dow in [5,6] else 1).mean()

# 각 이용정보 컬럼에 적용한 집계함수 매핑
agg_dict = {'reservation_start_at':[usage_span, interval_features, wd_ratio], 'region':'count',
            'member_age':'first', 'member_gender':'first', 'member_total_distance':'first', 
            'is_vroom':'sum', 'usage_time':['mean', 'std'], 'usage_period':'max', 
            'num_trips':['mean', 'std'], 'car_type':[mode_type, gini_index], 
            'attraction':['mean', 'std'], 'restaurant':['mean', 'std'], 'shopping':['mean', 'std']}

member = data.groupby('member_id').agg(agg_dict)

# 컬럼명 수정
member.columns = ['_'.join(col) for col in member.columns]
member.columns = [col[:-6] if col.startswith('member') else col for col in member.columns]
member = member.rename(columns={'reservation_start_at_usage_span':'usage_span', 'reservation_start_at_interval_features':'interval_features', 
                                'reservation_start_at_wd_ratio':'wd_ratio', 'region_count':'usage_cnt', 
                                'is_vroom_sum':'vroom_cnt', 'usage_period_max':'member_period', 
                                'car_type_mode_type':'car_type_mode', 'car_type_gini_index':'car_type_gini'})

# 추가변수 생성: 부름 이용확률, 1주(7일)당 이용건수
member['vroom_per_usage'] = member.vroom_cnt.divide(member.usage_cnt)
member['usage_per_week'] = member.usage_cnt.multiply(7).divide(member.usage_span)

# interval feature 분할
member['interval_mean'] = member['interval_features'].map(lambda features: features[0])
member['interval_std'] = member['interval_features'].map(lambda features: features[1])

use_col = ['member_age', 'member_gender', 'member_total_distance', 'member_period', 
           'wd_ratio', 'usage_per_week', 'interval_mean', 'interval_std',
           'usage_time_mean', 'usage_time_std',  'vroom_per_usage',
           'num_trips_mean', 'num_trips_std', 'car_type_mode', 'car_type_gini', 
           'attraction_mean',  'attraction_std', 'restaurant_mean', 'restaurant_std', 'shopping_mean', 'shopping_std']

member[use_col].to_csv('./data/member.csv')