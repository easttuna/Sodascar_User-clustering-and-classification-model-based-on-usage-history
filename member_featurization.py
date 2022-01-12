# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


# Load processed usage table
data = pd.read_csv('./data/socar_usage_processed_coord.csv', 
                   parse_dates=[...])

# transform hashed member identifier to int value
member_encoder = {hash:idx for hash, idx in zip(data.member_id.unique(), range(1, len(data)+1))}
data[...] = data[...].map(member_encoder)
data.to_csv('./data/socar_usage_processed_coord.csv', index=False)

# slice usage of members having more than 5 usage
row_cnt = data.groupby(...)['region'].count()
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
BOUND = data[...].max()
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

def interval_features(reservation_dt):
    """
    각 member별 이용이력의 시간적간격 리스트를 생성,
    시간간격의 평균과 표준편차를 반환
    """
    start_time = reservation_dt.sort_values()
    intervals = start_time[1:].sub(start_time.values[:-1]).divide(np.timedelta64(1, 'D')).values
    return intervals.mean(), np.median(intervals), intervals.std()

def wd_ratio(reservation_dt):
    """
    각 member별 대여일의 평일 비율 반환
    """
    return reservation_dt.dt.weekday.map(lambda dow: 0 if dow in [5,6] else 1).mean()

def zone_gini(zone):
    """
    각 member별 이용한 zone의 gini index 반환
    """
    probs = zone.value_counts(normalize=True).values
    gini = 1- np.power(probs, 2).sum()
    return gini

def region_gini(triplog):
    """
    각 member별 방문한 지역의 gini index 반환
    """
    triplog = triplog.map(lambda triplog: triplog.split('_'))
    regions = list()
    for region in triplog:
        regions += region
    probs = pd.Series(regions).value_counts(normalize=True).values
    gini = 1- np.power(probs, 2).sum()
    return gini 


# 각 이용정보 컬럼에 적용한 집계함수 매핑
agg_dict = {...}

member = data.groupby(...).agg(agg_dict)

# 컬럼명 수정
member.columns = ['_'.join(col) for col in member.columns]
member.columns = [col[:-6] if col.startswith('member') else col for col in member.columns]
member = member.rename(columns={...})

# 추가변수 생성: 부름 이용확률, 1주(7일)당 이용건수
member['vroom_per_usage'] = member.vroom_cnt.divide(member.usage_cnt)
member['usage_per_week'] = member.usage_cnt.multiply(7).divide(member.usage_span)

# interval feature 분할
member['interval_mean'] = member['interval_features'].map(lambda features: features[0])
member['interval_med'] = member['interval_features'].map(lambda features: features[1])
member['interval_std'] = member['interval_features'].map(lambda features: features[2])

use_col = [...]

member[use_col].to_csv('./data/member.csv')