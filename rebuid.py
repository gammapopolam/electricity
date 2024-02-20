
from shapely import from_geojson, box, buffer, intersects, equals, touches, relate
from shapely.geometry import MultiLineString, LineString
from shapely.ops import unary_union
import json
import geopandas as gpd
import math
# TODO: RTree
# ограничивающие прямоугольники 
# каждую часть мультилинии анализируют относительно других 
# ограничения должны зависеть от масштаба
# геометрии в одном индексе, если пересечение их bbox дает наименьшую площадь
class Restrictions:
    def __init__(self, l1, l2, buffer_distance):
        self.l1=l1
        self.l2=l2
        self.l1_buff=buffer(l1, distance=buffer_distance, cap_style='flat', quad_segs=2)
        self.l2_buff=buffer(l2, distance=buffer_distance, cap_style='flat', quad_segs=2)
        self.flag = 'undefined'
    def check(self):
        if self.is_buffers_intersect()==False:
            self.flag='undefined'
        else:
            if self.is_stream()==True:
                self.flag='stream'
            if self.is_branch()==True:
                self.flag='branch'
            if self.is_intersection()==True:
                self.flag='intersection'
        return self.flag
    def to_multiline(self, flag):
        if flag=='stream':
            if self.l1.geom_type=='MultiLineString':
                if self.l2.geom_type=='MultiLineString':
                    self.multil=MultiLineString([*self.l1.geoms, *self.l2.geoms])
                elif self.l2.geom_type=='LineString':
                    self.multil=MultiLineString([*self.l1.geoms, self.l2])
            elif self.l1.geom_type=='LineString':
                if self.l2.geom_type=='MultiLineString':
                    self.multil=MultiLineString([self.l1, *self.l2.geoms])
                elif self.l2.geom_type=='LineString':
                    self.multil=MultiLineString([self.l1, self.l2])
        #print(self.multil)
        return self.multil
    def Resolve_multipart_geometry():
        pass
    def is_buffers_intersect(self):
        if intersects(self.l1_buff, self.l2_buff)==False:
            return False
        else:
            return True
    def terminus_part(): #если геометрии индекса замыкаются в одной точке
        pass
    def is_branch(self): #если геометрии в индексе разветвляются в разные стороны
        if relate(self.l1, self.l2)=='FF1F00102':
            return True
        else:
            return False
    def is_stream(self): #если геометрии в индексе идут в одном коридоре
        if relate(self.l1, self.l2)=='FF1FF0102' and angle_checker(self.l1, self.l2)=='hallway':
            return True
        else:
            return False
    def is_intersection(self):
        if relate(self.l1, self.l2)=='FF10F0102' or relate(self.l1, self.l2)=='0F1FF0102':
            return True
        else:
            return False
    def single(): #геометрия в индексе единственная
        pass
    #def 

    
def angle_checker(l1, l2):
    #print(l1, l2)
    if l1.geom_type=='MultiLineString':
        l1=list(l1.geoms[0].coords)
    else:
        l1=list(l1.coords)
    if l2.geom_type=='MultiLineString':
        l2=list(l2.geoms[0].coords)
    else:
        l2=list(l2.coords)
    m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
    m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
    angle_rad = abs(math.atan(m1) - math.atan(m2))
    angle_deg = angle_rad*180/math.pi
    #print('angle diff:', abs(angle_deg))
    if abs(angle_deg)<1:
        return 'hallway'
    elif abs(angle_deg)>0 and abs(angle_deg)<135:
        return 'branch'
    else:
        return 'undefined'
with open('tests_utm.geojson', encoding='utf-8') as file:
    TL=json.loads(file.read())

def init_gpd(TL):
    gdf=gpd.GeoDataFrame.from_features(TL['features'])
    return gdf
def explode_gpd(TL_gdf):
    line_segs = gpd.GeoSeries(TL_gdf["geometry"]
    .apply(lambda g: [g] if isinstance(g, LineString) else [p for p in g.geoms])
    .apply(lambda l: [LineString([c1, c2]) for p in l for c1, c2 in zip(p.coords, list(p.coords)[1:])])
    .explode())
    gdf_singleparts_TL=line_segs.to_frame().join(gdf_TL.drop(columns="geometry")).reset_index(drop=True)
    gdf_singleparts_TL.rename(columns={'id':'origin_id'}, inplace=True)
    return gdf_singleparts_TL
def process_parts(TL_singleparts_shapely):
    for part1 in TL_singleparts_shapely:
        l1=part1['geom']
        # l1_buff=buffer(l1, distance=50, cap_style='round', quad_segs=2)
        for part2 in TL_singleparts_shapely:
            l2=part2['geom']
            #l2_buff=buffer(l2, distance=50, cap_style='round', quad_segs=2)
            restr=Restrictions(l1, l2, 50)
            flag=restr.check()
            if flag=='stream':
                #print(restr.to_multiline(flag))
                TL_singleparts_shapely.remove(part2)
                TL_singleparts_shapely.append({'geom':restr.to_multiline(flag), 'id': part2['id']})
    return TL_singleparts_shapely
gdf_TL=init_gpd(TL)
gdf_exploded_TL=explode_gpd(gdf_TL)
