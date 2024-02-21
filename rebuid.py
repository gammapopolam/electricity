
from shapely import from_geojson, intersects, equals, touches, relate
from shapely.geometry import MultiLineString, LineString
from shapely.ops import unary_union
import json
import geopandas as gpd
import math
import pandas as pd
pd.options.mode.copy_on_write = True

class Restrictions:
    def __init__(self, l1, l1_buff, l2, l2_buff):
        self.l1=l1
        self.l2=l2
        self.l1_buff=l1_buff
        self.l2_buff=l2_buff
        self.flag = 'undefined'
    def check(self):
        if self.is_buffers_intersect()==False:
            self.flag='undefined'
        else:
            if self.is_branch()==True:
                self.flag='branch'
            if self.is_stream()==True:
                self.flag='stream'
            
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
        return self.multil
    def Resolve_multipart_geometry():
        pass
    def is_buffers_intersect(self):
        if intersects(self.l1_buff, self.l2_buff)==False:
            return False
        else:
            return True
    def terminus_part():
        pass
    def is_branch(self):
        if relate(self.l1, self.l2)=='FF1F00102':
            return True
        else:
            return False
    def is_stream(self):
        if relate(self.l1, self.l2)=='FF1F00102' and angle_checker(self.l1, self.l2)=='hallway':
            return True
        elif relate(self.l1, self.l2)=='FF1FF0102' and angle_checker(self.l1, self.l2)=='hallway':
            return True
        else:
            return False
    def is_intersection(self):
        if relate(self.l1, self.l2)=='FF10F0102' or relate(self.l1, self.l2)=='0F1FF0102':
            return True
        else:
            return False
    def single():
        pass
    #def 

#TODO: update with multilinestrings, avoid using only first geom
def angle_checker(l1, l2):
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
    if abs(angle_deg)<3 or abs(angle_deg)>177:
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
def explode_gpd(gdf):
    line_segs = gpd.GeoSeries(gdf["geometry"]
    .apply(lambda g: [g] if isinstance(g, LineString) else [p for p in g.geoms])
    .apply(lambda l: [LineString([c1, c2]) for p in l for c1, c2 in zip(p.coords, list(p.coords)[1:])])
    .explode())
    gdf_exploded=line_segs.to_frame().join(gdf.drop(columns="geometry")).reset_index(drop=True)
    gdf_exploded.rename(columns={'id':'origin_id', 0: 'line'}, inplace=True)
    gdf_exploded['part_id']=gdf_exploded.index.astype(str)
    gdf_exploded=gdf_exploded.set_geometry('line')
    for i, val in gdf_exploded.iterrows():
        part_id=val.part_id
        line=val.line
        origin_id=val.origin_id
        gdf_exploded.iloc[i]={
            'line': line,
            'origin_id': origin_id,
            'part_id': [part_id]
            }
    return gdf_exploded
def buffers_gpd(gdf, distance):
    gdf['buffer']=gdf.geometry.buffer(distance=distance, cap_style=2, join_style=2)
    return gdf
def process_parts(gdf, length):
    for i, val1 in gdf.iterrows():
        l1=val1.line
        l1_buff=val1.buffer
        gdf_slice=gdf[gdf.index!=i]
        while len(gdf_slice)>0:
            val2=gdf_slice.iloc[-1]
            gdf_slice.drop(index=gdf_slice.index[-1], axis=0, inplace=True)
            l2=val2.line
            l2_buff=val2.buffer
            
            restr=Restrictions(l1, l1_buff, l2, l2_buff)
            flag=restr.check()
            #print(val1.part_id, val2.part_id, flag)
            if flag=='stream':
                if isinstance(val1.part_id, str) and isinstance(val2.part_id, str):
                    part_ids=[val1.part_id, val2.part_id]
                elif isinstance(val1.part_id, str) and isinstance(val2.part_id, list):
                    part_ids=[val1.part_id, *val2.part_id]

                elif isinstance(val1.part_id, list) and isinstance(val2.part_id, str):
                    part_ids=[*val1.part_id, val2.part_id]
                elif isinstance(val1.part_id, list) and isinstance(val2.part_id, list):
                    part_ids=[*val1.part_id, *val2.part_id]
                    
                gdf.iloc[i]={
                    'line': restr.to_multiline(flag), 
                    'buffer': unary_union([l1_buff, l2_buff]),
                    'origin_id': val1.origin_id,
                    'part_id': part_ids
                    }
    return gdf
#TODO: remove duplicates
#origin is the object that has the biggest length of part_id
#duplicates are the objects that contain items from origin part_id
def remove_duplicates(gdf):
    for i, val1 in gdf.iterrows():
        parts=val1.part_id
        if isinstance(parts, list):
            gdf.drop(index=gdf[gdf.part_id.isin(parts)].index, inplace=True)
    return gdf

gdf_TL=init_gpd(TL)
gdf_exploded_TL=explode_gpd(gdf_TL)
#print(gdf_exploded_TL.columns)
gdf_buffer_TL=buffers_gpd(gdf_exploded_TL, 50)
#gdf_buffer_TL['part_id']=gdf_buffer_TL.index.astype(str)
#exploded=gdf_buffer_TL.drop('buffer', axis=1)
#exploded.set_crs(epsg=32635, inplace=True)
#exploded.to_file(filename='exploded.gpkg', driver='GPKG')

#! NUMBERS OF PARTS IN MULTILINESTRING SET FROM LEFT TO RIGHT 

gdf_processed=process_parts(gdf_buffer_TL, len(gdf_buffer_TL))

gdf_processed_nodupl=remove_duplicates(gdf_processed)
# geopandas can't export to file with list type of column
gdf_processed_nodupl['part_id']=gdf_processed_nodupl['part_id'].str.join(',')
#print(gdf_processed_nodupl)
gdf_processed_nodupl.drop('buffer', axis=1, inplace=True)
gdf_processed_nodupl.set_crs(epsg=32635, inplace=True)
gdf_processed_nodupl.to_file(filename='tests.gpkg', driver='GPKG')
