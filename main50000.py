#%%
from rebuild2 import *
import geopandas as gpd
import pandas as pd
from io_handler import *
from hallway_recognition import *
from vector_algs_handler import *
from intersection_handler import *
from config_handler import *
from shapely import unary_union, normalize
from shapely.geometry import Point, MultiLineString, LineString
import shapely
from sympy.solvers.solveset import linsolve
from sympy import *
import folium
from recover_line_direction import *
from parallel_pandas import ParallelPandas
import time


#initialize parallel-pandas
ParallelPandas.initialize(n_cpu=8, split_factor=1, disable_pr_bar=True)
# Восстановление направления линий

# На данный момент - через current и back. Надо как то восстановить по-другому, через близость сегментов друг с другом 
# ИЛИ 
# через относительное положение между оригиналом и сдвинутым

# Глобальное восстановление сети

# Смысл заключается в том, чтобы объединить все линии разом, экстраполируя линии на их продолжение от концов. Анализ N сегмента относительно N-2, N-1, N+1, N+2
# Можно вообще забыть о том, что нам нужна связность и притягивать (snap) соседние геометрии между собой экстраполированием сегментов линиями или нахождением их пересечения

offset, buffer, angle = config(50000)
print(offset)
# Импорт данных
# Должно быть поле id, данные должны быть спроецированы
epsg=32635
gdf=importer('samples/net_utm.geojson', epsg=epsg)
# Разбиение сети на сегменты
start_time = time.time()
gdf_exploded=explode_gpd(gdf)
print("Explode finished --- %s seconds ---" % (time.time() - start_time))
#print(gdf_exploded)
exporter(gdf_exploded.copy(), name='coursework/50000/exploded.gpkg', keep_debug=True, epsg=epsg)
# Буферизация, пространственный индекс и обрезка сегментов
start_time = time.time()
gdf_buffer=buffers_gpd(gdf_exploded, buffer)
print("Buffers finished --- %s seconds ---" % (time.time() - start_time))
#print(gdf_buffer)
exporter(gdf_buffer.copy(), name='coursework/50000/clipped.gpkg', keep_debug=True, buffer=False, epsg=epsg)
exporter(gdf_buffer.copy(), name='coursework/50000/buffer.gpkg', keep_debug=True, buffer=True, epsg=epsg)
#%%
gdf_source=gdf_buffer.copy()
# Поиск коридоров
start_time = time.time()
gdf_processed=process_parts(gdf_buffer, angle)
print("Processing parts finished --- %s seconds ---" % (time.time() - start_time))
exporter(gdf_processed.copy(), name='coursework/50000/processed.gpkg', keep_debug=True, buffer=False, epsg=epsg)
#%%
# Привести все сегменты коридора к одному направлению
start_time = time.time()
gdf_flipped=flip_order(gdf_processed, angle)
print("Flipping finished --- %s seconds ---" % (time.time() - start_time))
exporter(gdf_flipped.copy(), name='coursework/50000/flipped.gpkg', keep_debug=True, epsg=epsg)
# Параллельный сдвиг
start_time = time.time()
gdf_offset=parallel_offset(gdf_flipped, gdf_source, offset)
print("Parallel offsetting finished --- %s seconds ---" % (time.time() - start_time))
# Распаковка коридоров в простые сдвинутые сегменты
start_time = time.time()
gdf_unpacked=unpack_multilines(gdf_offset)
print("Unpacking finished --- %s seconds ---" % (time.time() - start_time))
exporter(gdf_unpacked.copy(), name='coursework/50000/offsetted.gpkg', keep_debug=True, epsg=epsg)
#%%
gdf_unpacked_2=unpack_multilines(gdf_offset)
# Восстановление направления сегментов нити
start_time = time.time()
gdf_origin_2=gpd.read_file('coursework/50000/exploded.gpkg')
gdf_origin_2.rename(columns ={'geometry':'line'}, inplace=True)
gdf_recover=recover_line_dir_by_origin(gdf_unpacked_2.copy(), gdf_origin_2)
print("Recovering finished --- %s seconds ---" % (time.time() - start_time))
exporter(gdf_recover.copy(), name='coursework/50000/line_recovered.gpkg', keep_debug=True, epsg=32635)
#%%
# Восстановление сети
start_time = time.time()
gdf_net=recover_net(gdf_recover, 'coursework/50000/logs.txt')
print("Recovering finished --- %s seconds ---" % (time.time() - start_time))
exporter(gdf_net.copy(), name='coursework/50000/final.gpkg', keep_debug=True, epsg=32635)