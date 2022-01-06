import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import os


data_dir = '/home/eunji/project_dir/sodescar/data/member.csv'

### PCA

# 총 컬럼 22개
df = pd.read_csv(data_dir)
# label로 사용
df_y = df['car_type_mode']

# 문자열 데이터 임의 삭제
# 문자열 인코딩 pca 분석에 불필요할 듯
drop_col = ['member_id','member_gender','car_type_mode']

# 피쳐 18개 사용
df_x = df.drop(columns=drop_col)

# 표준화 작업
df_scaled = StandardScaler().fit_transform(df_x)

# PCA 적용
# components 피쳐 갯수만큼 설정 -> 적절한 차원수는 10으로 보임
pca = PCA(n_components=3)
pca_array = pca.fit_transform(df_scaled)

principal_df = pd.DataFrame(data=pca_array, columns=['component' + str(i) for i in range(1,4)])

# scree plot
plt.title('Scree plot')
plt.xlabel('n_components')
plt.ylabel('Cumulative Explained Variance')
plt.plot(pca.explained_variance_ratio_, 'o-')
#plt.show()


pca_pred = pd.DataFrame(pca.fit_transform(df_x))

# get predict value
pca_pred = pd.concat([pca_pred, df_y], axis=1)
#pca_pred.columns=['com1','com2','com3','labels']

# 2차원 시각화
sns.scatterplot(pca_pred[0], pca_pred[1], data=pca_pred, hue ='car_type_mode', style='car_type_mode', s=100)

# 3차원 시각화
'''
fig2 = plt.figure(figsize=(10,10))
ax = fig2.add_subplot(111, projection='3d')

ax.set_xlabel('Pricipal Component1', fontsize=15)
ax.set_ylabel('Pricipal Component2', fontsize=15)
ax.set_zlabel('Pricipal Component3', fontsize=15)
ax.set_title('3 Component PCA', fontsize=20)

colors = ["#7fc97f","#beaed4","#fdc086","#ffff99","#386cb0","#f0027f"]
labels = pca_pred['labels']

for label, color in zip(labels, colors):
    indicesToKeep = pca_pred['labels'] == label
    ax.scatter(pca_pred.loc[indicesToKeep, 'com1'],
                pca_pred.loc[indicesToKeep, 'com2'],pca_pred.loc[indicesToKeep, 'com3'], c = color, s = 10)

ax.legend(labels)
ax.grid()
'''

save_dir = './data'
pca_pred.to_csv(os.path.join(save_dir, 'pca_pred.csv'), index=False)




