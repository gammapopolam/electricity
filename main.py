from shapely import from_geojson, box, buffer, intersects, equals, touches, relate
from shapely.geometry import MultiLineString
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
    print(l1, l2)
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
# ШЛЯПА
def search_parallels(TL_singleparts, iter):
    for feature in TL_singleparts:
        #print(iter, feature)
        # initially, segments are features

        # if no parallel segments, make feature collection with one feature
        # if there are parallel segments for feature, add them into feature collection
        if feature['type']=='Feature':
            l=from_geojson(json.dumps(feature['geometry']))
            l_buff=buffer(l, distance=50, cap_style='flat', quad_segs=2)

            for feature2 in TL_singleparts:
                if feature2['type']=='Feature':
                    l2=from_geojson(json.dumps(feature2['geometry']))
                    if equals(l, l2):
                        break
                    else:
                        if intersects(l_buff, l2) and angle_checker(l, l2)==True and touches(l, l2)==False:
                            l2_buff=buffer(l, distance=50, cap_style='flat', quad_segs=2)
                            l_buff=unary_union([l_buff, l2_buff])
                            feature_collection={'type': 'FeatureCollection', 'features': []}
                            feature_collection['features'].append(feature)
                            feature_collection['features'].append(feature2)
                            TL_singleparts.remove(feature)
                            TL_singleparts.remove(feature2)
                            TL_singleparts.append(feature_collection)
                        elif intersects(l_buff, l2) and angle_checker(l, l2)==False:
                            continue
                        else:
                            continue
        elif feature['type']=='FeatureCollection':
            l=from_geojson(json.dumps(feature['features'][0]['geometry']))
            l_buff=unary_union([buffer(from_geojson(json.dumps(feature['features'][x]['geometry'])), distance=50, cap_style='flat', quad_segs=2) for x in range(len(feature['features']))])
            #print(l_buff)
            #for feature1 in feature['features']:

            for feature2 in TL_singleparts:
                if feature2['type']=='Feature':
                    l2=from_geojson(json.dumps(feature2['geometry']))
                    if intersects(l_buff, l2) and angle_checker(l, l2)==True:
                        l2_buff=buffer(l, distance=50, cap_style='flat', quad_segs=2)
                        l_buff=unary_union([l_buff, l2_buff])
                        TL_singleparts.remove(feature)
                        feature['features'].append(feature2)
                        TL_singleparts.append(feature)
                        TL_singleparts.remove(feature2)
                    else:
                        break
    iter=iter+1
    if iter>len(TL_singleparts*3):
        return 0
    return search_parallels(TL_singleparts, iter)
'''
def recursive_search2(TL_singleparts, TL_singleparts_2, TL_singleparts_3):
    if len(TL_singleparts)==0:
        return TL_singleparts_3
    else:
        for i in range(len(TL_singleparts)):
            current_part=TL_singleparts[i]
            TL_singleparts.remove(current_part)
            TL_singleparts_2[i]=''
            print('current', current_part)
            l=from_geojson(json.dumps(current_part['geometry']))
            l_buff=buffer(l, distance=50, cap_style='flat', quad_segs=2)
            for k in range(len(TL_singleparts_2)):
                serving_part=TL_singleparts_2[k]
                print('serving', serving_part)
                if serving_part!='':
                    l2=from_geojson(json.dumps(serving_part['geometry']))
                    if intersects(l_buff, l2) and angle_checker(l, l2):
                        l2_buff=buffer(l2, distance=50, cap_style='flat', quad_segs=2)
                        l_buff=unary_union([l_buff, l2_buff]) # return to find another in hallway or keep multilinestring?
                        TL_singleparts.remove(serving_part)
                        if current_part['geometry']['type']=='LineString':
                            new_part=current_part
                            new_part['geometry']={'type':'MultiLineString', 'coordinates': [new_part['geometry']['coordinates'], serving_part['geometry']['coordinates']]}
                        elif current_part['geometry']['type']=='MultiLineString':
                            new_part=current_part
                            new_part['geometry']['coordinates'].append(serving_part['geometry']['coordinates'])
                        TL_singleparts_3.append(new_part)
            return recursive_search2(TL_singleparts, TL_singleparts_2, TL_singleparts_3)
'''    
def search_parallels2(TL_singleparts, TL_singleparts_multi=[], TL_singleparts_branches=[]):
    #print('before popping', len(TL_singleparts))
    
    while len(TL_singleparts)!=0:
        current_part=TL_singleparts.pop()
        l=from_geojson(json.dumps(current_part['geometry']))
        l_buff=buffer(l, distance=50, cap_style='round', quad_segs=2)
        for serving_part in TL_singleparts:
            #serving_part=TL_singleparts[i]
            l2=from_geojson(json.dumps(serving_part['geometry']))
            l2_buff=buffer(l2, distance=50, cap_style='round', quad_segs=2)
            if angle_checker(l, l2)=='undefined': #if line is single neighbour
                TL_singleparts_branches.append(serving_part)
                print(TL_singleparts_branches)
                search_parallels2(TL_singleparts, TL_singleparts_multi, TL_singleparts_branches)
            #if angle_checker(l, l2)=='branch' and intersects(l_buff, l2)==True:
                #TL_singleparts.remove(serving_part)
                #TL_singleparts_multi.append(serving_part)
            if angle_checker(l, l2)=='hallway' and intersects(l_buff, l2_buff)==True:
                TL_singleparts.remove(serving_part)
                l_buff=unary_union([l_buff, l2_buff])
                if current_part['geometry']['type']=='LineString':
                    new_part=current_part
                    new_part['geometry']={'type':'MultiLineString', 'coordinates': [new_part['geometry']['coordinates'], serving_part['geometry']['coordinates']]}
                elif current_part['geometry']['type']=='MultiLineString':
                    new_part=current_part
                    TL_singleparts_multi.remove(current_part)
                    new_part['geometry']['coordinates'].append(serving_part['geometry']['coordinates'])
                TL_singleparts_multi.append(new_part)
                #print('after popping', len(TL_singleparts), f'serving id {serving_part['properties']['id']} current id {current_part['properties']['id']}')
    else:
        return TL_singleparts_multi, TL_singleparts_branches


with open('tests_utm.geojson', encoding='utf-8') as file:
    TL=json.loads(file.read())


def explode(TL):
    TL_singleparts=[]
    print('Num of features before exploding: ', len(TL['features']))
    for i in range(len(TL['features'])):
        if TL['features'][i]['geometry']['type']=='MultiLineString':
            feature=TL['features'][i]
            multiparts=TL['features'][i]['geometry']['coordinates']
            #print(len(multiparts))
            for part in multiparts:
                for j in range(len(part)-1):
                    singlepart_geometry = {'type': 'LineString', 'coordinates':[part[j], part[j+1]]}
                    singlepart=feature.copy()
                    singlepart['properties']['id']=f'{i}{j}'
                    singlepart['geometry']=singlepart_geometry
                    singlepart['geometry']['crs']={'type':'name', 'properties':{'name':'EPSG:32635'}}
                    TL_singleparts.append(singlepart)
        elif TL['features'][i]['geometry']['type']=='LineString':
            feature=TL['features'][i]
            part=TL['features'][i]['geometry']['coordinates']
            #print(len(multiparts))
            for j in range(len(part)-1):
                singlepart_geometry = {'type': 'LineString', 'coordinates':[part[j], part[j+1]]}
                singlepart=feature.copy()
                singlepart['geometry']=singlepart_geometry
                singlepart['properties']['id']=f'{i}{j}'
                singlepart['geometry']['crs']={'type':'name', 'properties':{'name':'EPSG:32635'}}
                TL_singleparts.append(singlepart)
    print('Num of features after exploding: ', len(TL_singleparts))
    return TL_singleparts
def bboxes(TL_singleparts):
    print('Get bboxes...')
    TL_singleparts_bboxes=[]
    for k in range(len(TL_singleparts)):
        feature=TL_singleparts[k]
        feature_geom=from_geojson(json.dumps(feature['geometry']))
        feature_bbox=box(*feature_geom.bounds)
        bbox=feature.copy()
        bbox['geometry']=list(feature_bbox.exterior.coords)
        TL_singleparts_bboxes.append(bbox)
    return TL_singleparts_bboxes
def to_shapely(TL_singleparts):
    TL_singleparts_shapely=[]
    for part in TL_singleparts:
        l=from_geojson(json.dumps(part['geometry']))
        data={'geom':l, 'id': part['properties']['id']}
        TL_singleparts_shapely.append(data)
    return TL_singleparts_shapely
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
def unpack_into_gdf(TL_singleparts_processed):
    val1=[]
    geom=[]
    for val in TL_singleparts_processed:
        #print(val)
        val1.append(val['id'])
        geom.append(val['geom'])
    #print(geom)
    gdf = gpd.GeoDataFrame({'val': val1, 'geometry': geom}, crs='EPSG:32635')
    #gdf.set_geometry('0')
    return gdf
TL_singleparts=explode(TL)
TL_singleparts_shapely=to_shapely(TL_singleparts)
#print(TL_singleparts_shapely)
TL_singleparts_processed=process_parts(TL_singleparts_shapely)
#print(TL_singleparts_processed)
gdf=unpack_into_gdf(TL_singleparts_processed)
print(gdf)
print(gdf.plot())
'''
TL_singleparts_parallels, TL_singleparts_branches=search_parallels2(TL_singleparts.copy())
#TL_singleparts_2
new_fc={'type':'FeatureCollection', 'features': []}
for fc in TL_singleparts_parallels:
    new_fc['features'].append(fc)
new_fc['crs']={'type':'name', 'properties':{'name':'EPSG:32635'}}
TL_singleparts_branches
new_fc2={'type':'FeatureCollection', 'features': []}
for fc in TL_singleparts_branches:
    new_fc2['features'].append(fc)
new_fc2['crs']={'type':'name', 'properties':{'name':'EPSG:32635'}}
'''
# TL_singleparts got same IDs as TL_singleparts_bboxes
# Need to index singleparts by bboxes
# After indexing, single parts turn into multipart geometry with restrictions