from shapely import from_wkt
from shapely.geometry import MultiLineString, LineString
from vector_algs_handler import *
import pandas as pd
p21_1240_0=from_wkt('LineString (664446.84479981 6635021.41337806, 664459.08821881 6634902.76408316)')
p21_1240_1=from_wkt('LineString (664459.08821881 6634902.76408316, 664713.77546588 6632434.62489031)')
p21_1240_2=from_wkt('LineString (664743.12029608 6632150.24816408, 665407.33682048 6625713.41689244)')
print(get_direction(list(p21_1240_0.coords)))
print(get_direction(list(p21_1240_1.coords)))
print(get_direction(list(p21_1240_2.coords)))


parts=[list(x.coords) for x in [p21_1240_0, p21_1240_1, p21_1240_2]]

df=pd.DataFrame(parts, columns=['line_p1', 'line_p2'])
df['p1_x']=[df['line_p1'][i][0] for i in range(len(df))]
df['p1_y']=[df['line_p1'][i][1] for i in range(len(df))]
df['p2_x']=[df['line_p2'][i][0] for i in range(len(df))]
df['p2_y']=[df['line_p2'][i][1] for i in range(len(df))]
df_p1=df.drop(columns=['line_p1', 'line_p2', 'p2_x', 'p2_y'])
df_p2=df.drop(columns=['line_p1', 'line_p2', 'p1_x', 'p1_y'])
df_p1.rename(columns={'p1_x': 'p_x', 'p1_y': 'p_y'}, inplace=True)
df_p2.rename(columns={'p2_x': 'p_x', 'p2_y': 'p_y'}, inplace=True)
df=pd.concat([df_p1, df_p2], ignore_index=True, axis=0)
print(df)
flag=None

dir=get_direction(list(p21_1240_0.coords))
if dir<0:
    dir=dir+270
print(dir)
if dir>=45 and dir<135:
    flag='Ox_left'
    df.sort_values(by='p_x', ascending=False, inplace=True)
elif dir>=135 and dir<225:
    flag='Oy_down'
    df.sort_values(by='p_y', ascending=False, inplace=True)
elif dir>=225 and dir<315:
    flag='Ox_right'
    df.sort_values(by='p_x', ascending=True, inplace=True)
elif dir>=315 and (dir<45 or dir+360<405):
    flag='Oy_up'
    df.sort_values(by='p_y', ascending=True, inplace=True)
print(flag)
df=df.reset_index(drop=True)
print(df)

print(get_direction([[0,0], [1,1]]))
print(get_direction([[0,0], [1,0.0001]]))
print(get_direction([[0,0], [1,-1]])+360)
print(get_direction([[0,0], [0.0001,-1]])+360)
print(get_direction([[0,0], [-1,-1]])+360)
print(get_direction([[0,0], [-1,0.0001]]))
print(get_direction([[0,0], [-1,1]]))
print(get_direction([[0,0], [0.0001,1]]))