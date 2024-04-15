#%%
from rebuild2 import *
import geopandas as gpd
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

# Восстановление направления линий

# На данный момент - через current и back. Надо как то восстановить по-другому, через близость сегментов друг с другом 
# ИЛИ 
# через относительное положение между оригиналом и сдвинутым

# Глобальное восстановление сети

# Смысл заключается в том, чтобы объединить все линии разом, экстраполируя линии на их продолжение от концов. Анализ N сегмента относительно N-2, N-1, N+1, N+2
# Можно вообще забыть о том, что нам нужна связность и притягивать (snap) соседние геометрии между собой экстраполированием сегментов линиями или нахождением их пересечения

offset, buffer, angle = config(100000)
print(offset)
#%%
# Импорт данных
# Должно быть поле id, данные должны быть спроецированы
epsg=32635
gdf=importer('samples/net_utm.geojson', epsg=epsg)
# Разбиение сети на сегменты
gdf_exploded=explode_gpd(gdf)
#print(gdf_exploded)
exporter(gdf_exploded.copy(), name='coursework/exploded.gpkg', keep_debug=True, epsg=epsg)
# Буферизация, пространственный индекс и обрезка сегментов
gdf_buffer=buffers_gpd(gdf_exploded, buffer)
#print(gdf_buffer)
exporter(gdf_buffer.copy(), name='coursework/clipped.gpkg', keep_debug=True, buffer=False, epsg=epsg)
exporter(gdf_buffer.copy(), name='coursework/buffer.gpkg', keep_debug=True, buffer=True, epsg=epsg)
gdf_source=gdf_buffer.copy()
# Поиск коридоров
gdf_processed=process_parts(gdf_buffer, angle)
exporter(gdf_processed.copy(), name='coursework/processed.gpkg', keep_debug=True, buffer=False, epsg=epsg)
# Привести все сегменты коридора к одному направлению
gdf_flipped=flip_order(gdf_processed, angle)
exporter(gdf_flipped.copy(), name='coursework/flipped.gpkg', keep_debug=True, epsg=epsg)
# Параллельный сдвиг
gdf_offset=parallel_offset(gdf_flipped, gdf_source, offset)
# Распаковка коридоров в простые сдвинутые сегменты
gdf_unpacked=unpack_multilines(gdf_offset)
exporter(gdf_unpacked.copy(), name='coursework/offsetted.gpkg', keep_debug=True, epsg=epsg)
# Восстановление направления сегментов нити
gdf_recover=recover_line_dir(gdf_unpacked)

exporter(gdf_recover.copy(), name='coursework/line_recovered.gpkg', keep_debug=True, epsg=32635)
# Восстановление сети
gdf_net=recover_net(gdf_recover)
exporter(gdf_net.copy(), name='coursework/final.gpkg', keep_debug=True, epsg=32635)
#%%

gdf_net.to_crs('EPSG:4326', inplace=True)
#print(gdf_net)
import random

gdf_net['color']=gdf_net.apply(lambda x: f"#{random.randrange(0x1000000):06x}", axis=1)
print(gdf_net)
centermap=[gdf_net.geometry.centroid[0].y, gdf_net.geometry.centroid[0].x]
m=folium.Map(location=centermap, tiles='CartoDB Positron', zoom_start=9)
folium.GeoJson(gdf_net, style_function=lambda feature: {"color": feature['properties']['color'], 'weight': 3}).add_to(m)

m


# %%
