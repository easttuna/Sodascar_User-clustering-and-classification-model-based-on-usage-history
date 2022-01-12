# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from tqdm import tqdm


tqdm.pandas()

data = pd.read_csv('./data/socar_reservation_triplog.csv', 
                   parse_dates=[...])

# 사용하지 않는 컬럼 제거
drop_col = [...]

data = data.drop(columns=drop_col)

# 긴 컬럼명 변경
data = data.rename(columns={...})

# 결측치 제거
data = data.dropna()

# 이용시간(시간)컬럼 생성 및 30분 이상 이용만 선택
data['usage_time'] =  data[...].sub(data[...]).divide(np.timedelta64(1, 'h'))
data = data[data.usage_time.ge(0.5)]

# 가입기간(일)컬럼 생성
data['usage_period'] =  data[...].sub(data[...]).divide(np.timedelta64(1, 'D')).astype(int)

# trip 횟수 컬럼 생성
data['num_trips']  = data[...].map(lambda x: len(x.split(',')))

# int 변환
data[...] = data[...].astype(int)

# 차종 분류 -> compact(경차, 소형차) / sedan(세단) / compact_SUV (소형 SUV) / SUV(소형제외 SUV) / EV(전기차) / van (승합차)
car_type = pd.read_csv('./data/car_group.csv')
car_labeler = {name:label for name, label in zip(car_type.name, car_type.group)}
data['car_type'] = data[...].map(car_labeler)


# triplog에서 발생한 적있는 지역(시군구) 데이터프레임 생성
regions = list()
for triplog in data[...].str.split(','):
    regions.extend(triplog)
regions = [r.strip() for r in list(set(regions))]
region_df = pd.DataFrame({'name':regions})

# regions에 해당 지역특성 변수를 매핑하기 위한 '여행소비지도' 데이터 로드
# https://www.bigdata-culture.kr/bigdata/user/data_market/detail.do?id=98124fc8-5024-4b27-b9a7-5631021ed5a8
stores = pd.read_csv('./data/region_data/KC_619_DMSTC_TRV_CNSMP_STATN_BIZAEA_MAP_2019.csv')
stores['name'] = stores.sido_nm + ' ' + stores.sgg_nm
stores = stores.drop(columns=['FILE_NAME', 'base_ymd', 'hadm_cd'])
null_idx = stores[stores.name.isna()].index
stores.loc[null_idx, 'name'] = '세종특별자치시'

# regions 데이터프레임에 지역특성 정보 merge
region_df = region_df.merge(stores, how='left', on='name')

# 인구 1000명당 관광지, 식당, 쇼핑점 수로 변환
feature_cols = [col for col in region_df.columns if col[-3:] == 'cnt']
for col in feature_cols:
    region_df[col] = region_df[col] * 1000 / region_df.residnt_cnt_sum
region_df = region_df.drop(columns=['residnt_cnt_sum']) \
                     .rename(columns={'atrctn_cnt':'attraction', 'rstrt_cnt':'restaurant', 'shopng_cnt':'shopping'}) \
                     .set_index('name')


def get_trip_feature(triplog, region_table):
    """
    trip log에서 방문한 지역들의 3가지 특성정보를 region_df를 참조하여 불러온 뒤 평균냄
    해당 이용 방문지의 평균적인 특성을 나타내는 변수
    ex. 관광지만 돌아다니면 -> 인구대비 관광지 평균이 높음
    """
    triplog = triplog.split(',')
    triplog = [region.strip() for region in triplog]
    mean_features = region_table.loc[triplog, ['attraction', 'restaurant', 'shopping']].values.mean(axis=0)
    return {'attraction':mean_features[0], 'restaurant':mean_features[1], 'shopping':mean_features[2]}

# data의 각 행별로 방문지 특성변수를 종합한 데이터프레임 생성
print('mapping regional features...')
trip_feautures = data[...].progress_map(lambda log: get_trip_feature(log, region_df))
print('done')
trip_feautures = pd.DataFrame(list(trip_feautures.values))


# data와 concat
data = pd.concat([data.reset_index(drop=True), trip_feautures], axis=1)

# trip컬럼에서 각 행의 중복지역 제거
def drop_dup_regions(triplog):
    triplog = triplog.split(',')
    triplog = [region.strip() for region in set(triplog)]
    return '_'.join(triplog)

data[...] = data[...].map(drop_dup_regions)

# 처리한 테이블 저장
data.to_csv('./data/socar_usage_processed.csv', index=False)