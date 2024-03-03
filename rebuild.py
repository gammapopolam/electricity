
from shapely import intersects, relate
from shapely.geometry import MultiLineString, LineString
#from shapely.ops import unary_union
from shapely import unary_union, normalize
import json
import geopandas as gpd
import math
import pandas as pd
pd.options.mode.copy_on_write = True

class Restrictions:
    def __init__(self, l1, l1_buff, l2, l2_buff, angle):
        self.l1=l1
        self.l2=l2
        self.l1_buff=l1_buff
        self.l2_buff=l2_buff
        self.flag = 'undefined'
        self.angle=angle
    def angle_checker(self, l1, l2):
        flag='undefined'
        if l1.geom_type=='MultiLineString' and l2.geom_type=='MultiLineString':
            l1_geoms=list(l1.geoms)
            l2_geoms=list(l2.geoms)
            for geom in l1_geoms:
                l1=geom.coords
                for geom2 in l2_geoms:
                    l2=geom2.coords
                    m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                    m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                    angle_rad = abs(math.atan(m1) - math.atan(m2))
                    angle_deg = angle_rad*180/math.pi
                    #print('angle diff:', abs(angle_deg))
                    if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                        flag='hallway'
        elif l1.geom_type=='MultiLineString' and l2.geom_type=='LineString':
            l1_geoms=list(l1.geoms)
            l2=list(l2.coords)
            for geom in l1_geoms:
                l1=geom.coords
                m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                angle_rad = abs(math.atan(m1) - math.atan(m2))
                angle_deg = angle_rad*180/math.pi
                #print('angle diff:', abs(angle_deg))
                if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                    flag='hallway'
        elif l1.geom_type=='LineString' and l2.geom_type=='MultiLineString':
            l2_geoms=list(l2.geoms)
            l1=list(l1.coords)
            for geom in l2_geoms:
                l2=geom.coords
                m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
                m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
                angle_rad = abs(math.atan(m1) - math.atan(m2))
                angle_deg = angle_rad*180/math.pi
                #print('angle diff:', abs(angle_deg))
                if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                    flag='hallway'
        else:
            l1=list(l1.coords)
            l2=list(l2.coords)
            m1 = (l1[1][1]-l1[0][1])/(l1[1][0]-l1[0][0])
            m2 = (l2[1][1]-l2[0][1])/(l2[1][0]-l2[0][0])
            angle_rad = abs(math.atan(m1) - math.atan(m2))
            angle_deg = angle_rad*180/math.pi
            #print('angle diff:', abs(angle_deg))
            if abs(angle_deg)<self.angle or abs(angle_deg)>(180-self.angle):
                flag='hallway'
        return flag
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
        if intersects(self.l1_buff, self.l2_buff)==True and self.l1_buff.intersection(self.l2_buff).area>(self.l2_buff.area/100*15):
            return True
        else:
            return False
    def terminus_part():
        pass
    def is_branch(self):
        if relate(self.l1, self.l2)=='FF1F00102':
            return True
        else:
            return False
#TODO: need more tests with DE-9IM
    def is_stream(self):
        if relate(self.l1, self.l2)=='FF1FF0102' and self.angle_checker(self.l1, self.l2)=='hallway':
            return True
        #elif relate(self.l1, self.l2)=='1F1F00102' and angle_checker(self.l1, self.l2)=='hallway':
        #    return True
        elif relate(self.l1, self.l2)=='FF1F0F102' and self.angle_checker(self.l1, self.l2)=='hallway':
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
def get_direction(l1):
    dx1, dy1 = l1[1][0]-l1[0][0], l1[1][1]-l1[0][1]
    r1=math.atan2(dy1,dx1)*180/math.pi
    if dx1>0 and dy1>0:
        a1=r1
    elif dx1<0 and dy1>0:
        a1=180-r1
    elif dx1<0 and dy1<0:
        a1=r1-180
    elif dx1>0 and dy1<0:
        a1=360-r1
    return a1


def init_gpd(TL):
    gdf=gpd.GeoDataFrame.from_features(TL['features'])
    return gdf
def explode_gpd(gdf):
    line_segs = gpd.GeoSeries(gdf["geometry"]
    .apply(lambda g: [g] if isinstance(g, LineString) else [p for p in g.geoms])
    .apply(lambda l: [LineString([c1, c2]) for p in l for c1, c2 in zip(p.coords, list(p.coords)[1:])])
    .explode())
    gdf_exploded=line_segs.to_frame().join(gdf.drop(columns="geometry")).reset_index(drop=True)
    # Some mistake in gdf_exploded columns

    # FOR HOME-PC
    gdf_exploded.rename(columns={'id':'origin_id', 'geometry': 'line'}, inplace=True)
    # FOR LAPTOP
    #gdf_exploded.rename(columns={'id':'origin_id', 0: 'line'}, inplace=True)

    gdf_exploded['part_id']=gdf_exploded.origin_id.astype(str)+'_'+gdf_exploded.index.astype(str)
    gdf_exploded=gdf_exploded.set_geometry('line')
    for i, val in gdf_exploded.iterrows():
        part_id=val.part_id
        line=val.line
        origin_id=val.origin_id
        
        gdf_exploded.iloc[i]={
            'line': line,
            'origin_id': origin_id,
            'part_id': part_id
            }
    gdf_exploded['simple_index']=None
    return gdf_exploded
def buffers_gpd(gdf, distance):
    gdf['buffer']=gdf.geometry.buffer(distance=distance, cap_style=2, join_style=2)
    #print(gdf)
    # этот маневр будет стоить нам семи лет
    buffers=gpd.GeoDataFrame(geometry=gdf['buffer'])
    gdf=gdf.overlay(buffers, "union")
    
    gdf=restore_lines(gdf)
    gdf['buffer']=gdf.geometry.buffer(distance=distance, cap_style=2, join_style=2)
    #print(gdf.columns)
    gdf.rename(columns={'geometry': 'line'}, inplace=True)
    for i, val in gdf.iterrows():
        line=val.line
        buffer=val.buffer
        origin_id=val.origin_id
        part_id=val.part_id
        indexed=simple_index(buffer, gdf, i)
        gdf.at[i, 'line']=line
        gdf.at[i, 'buffer']=buffer
        gdf.at[i, 'origin_id']=origin_id
        gdf.at[i, 'part_id']=[part_id]
        gdf.at[i, 'simple_index']=indexed
    return gdf



def simple_index(buffer, gdf, i):
    gdf_slice=gdf[gdf.index!=i]
    simple_index=dict(buffer.intersects(gdf_slice['buffer']))
    for x in [x for x in simple_index.keys() if simple_index[x] == False]:
        simple_index.pop(x)
    indexed=list(simple_index.keys())
    return indexed
def restore_lines(gdf):
    # Слайсы по уникальным выражениям
    # Если длина слайса больше 1, значит определить направление линии, перевести в точки, отсортировать по возрастанию/убыванию ОХ
    uniqs=list(sorted(gdf['part_id'].unique()))
    ctr=0
    for uniq in uniqs:
        ctr+=1
        printProgressBar(ctr, len(uniqs), prefix = 'Restoring lines:', suffix = 'Complete', length = 50)
        gdf_slice=gdf[gdf['part_id']==uniq]
        #print(gdf_slice)
        origin_id=list(gdf_slice['origin_id'])[0]
        if len(gdf_slice)>1:
            parts=[list(x.coords) for x in gdf_slice.geometry]
            if list(gdf_slice.geometry)[0].is_empty:
                print(gdf_slice)
            d=get_direction(parts[0])
            df=pd.DataFrame(parts, columns=['line_p1', 'line_p2'])
            for j, val1 in df.iterrows():
                d2=get_direction([val1.line_p1, val1.line_p2])
                if abs(d-d2)>5:
                    df.at[j, 'line_p1']=val1.line_p2
                    df.at[j, 'line_p2']=val1.line_p1
            df['p1_x']=[df['line_p1'][i][0] for i in range(len(df))]
            df['p1_y']=[df['line_p1'][i][1] for i in range(len(df))]
            df['p2_x']=[df['line_p2'][i][0] for i in range(len(df))]
            df['p2_y']=[df['line_p2'][i][1] for i in range(len(df))]
            df_p1=df.drop(columns=['line_p1', 'line_p2', 'p2_x', 'p2_y'])
            df_p2=df.drop(columns=['line_p1', 'line_p2', 'p1_x', 'p1_y'])
            df_p1.rename(columns={'p1_x': 'p_x', 'p1_y': 'p_y'}, inplace=True)
            df_p2.rename(columns={'p2_x': 'p_x', 'p2_y': 'p_y'}, inplace=True)
            df_points=pd.concat([df_p1, df_p2], ignore_index=True, axis=0)
            #print(uniq, d, end=' ')
            if (d>-90 and d<90) or (d>270 and d<450) or (d<-270 and d>-450):
                flag='Ox_right'
                df_points.sort_values(by='p_x', ascending=True, inplace=True)
                
            elif (d>90 and d<270) or (d>-90 and d<-270):
                flag='Ox_left'
                df_points.sort_values(by='p_x', ascending=False, inplace=True)
            df_points.drop_duplicates(inplace=True)
            df_points.reset_index(inplace=True, drop=True)
            restored_lines=[]
            for j in range(len(df_points)-1):
                p1=(df_points.at[j, 'p_x'], df_points.at[j, 'p_y'])
                p2=(df_points.at[j+1, 'p_x'], df_points.at[j+1, 'p_y'])
                line=LineString([p1, p2])
                if line.length>100:
                    restored_lines.append(line)
            gdf=gdf[gdf['part_id']!=uniq]
            gdf_slice.drop(gdf_slice.index, inplace=True)
            for j in range(len(restored_lines)):
                part_id=f'{uniq}_{j}'
                gdf_slice.at[j,'geometry']=restored_lines[j]
                gdf_slice.at[j,'part_id']=part_id
                gdf_slice.at[j, 'origin_id']=origin_id
            gdf=pd.concat([gdf, gdf_slice]).reset_index(drop=True)
    # drop parts with smaller length
    
    return gdf
    # Я сделал это, но ценой чего...
    #TODO: delete partitions with smallest length (classification?), they make this too complicated

#TODO: due to spatialindex implementation some segments not correct. need more tests with DE-9IM

def process_parts(gdf, angle):
    l=len(gdf)
    for i, val1 in gdf.iterrows():
        printProgressBar(i + 1, l, prefix = 'Processing lines:', suffix = 'Complete', length = 50)
        l1=val1.line
        l1_buff=val1.buffer
        indexed=val1.simple_index
        gdf_slice=gdf.copy()
        gdf_slice=gdf_slice[gdf_slice.index.isin(indexed)]
        val1_part_id=val1.part_id
        while len(gdf_slice)>0:
            val2=gdf_slice.iloc[-1]
            val2_index=gdf.line[gdf.line == val2.line].index.tolist()
            gdf_slice.drop(index=val2_index, axis=0, inplace=True)
            l2=val2.line
            l2_buff=val2.buffer
            
            restr=Restrictions(l1, l1_buff, l2, l2_buff, angle)
            flag=restr.check()
            if flag=='stream':
                if isinstance(val1_part_id, str) and isinstance(val2.part_id, str):
                    part_ids=[val1_part_id, val2.part_id]
                elif isinstance(val1_part_id, str) and isinstance(val2.part_id, list):
                    part_ids=[val1_part_id, *val2.part_id]
                elif isinstance(val1_part_id, list) and isinstance(val2.part_id, str):
                    part_ids=[*val1_part_id, val2.part_id]
                elif isinstance(val1_part_id, list) and isinstance(val2.part_id, list):
                    part_ids=[*val1_part_id, *val2.part_id]
                l1=restr.to_multiline(flag)
                l1_buff=normalize(unary_union([l1_buff, l2_buff]))
                val1_part_id=list(set(part_ids))
                gdf=gdf[gdf.line!=val2.line]
                gdf.at[i, 'line']=l1
                gdf.at[i, 'buffer']=l1_buff
                gdf.at[i, 'origin_id']=int(val1.origin_id)
                gdf.at[i, 'part_id']=val1_part_id
                gdf.at[i, 'simple_index']=simple_index(l1_buff, gdf, i)
    return gdf

#TODO: remove duplicates
#origin is the object that has the biggest length of part_id
#duplicates are the objects that contain items from origin part_id

#is it significant to use?
def remove_duplicates(gdf):
    for i, val1 in gdf.iterrows():
        parts=val1.part_id
        if isinstance(parts, list):
            gdf.drop(index=gdf[gdf.part_id.isin(parts)].index, inplace=True)
    return gdf
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()
                    
def flip_order(gdf, angle):
    for i, val in gdf.iterrows():
        geometry=val.line
        if geometry.geom_type=='MultiLineString':
            base_geom=list(geometry.geoms)[0]
            geoms_slice=list(geometry.geoms).copy()
            geoms_slice.remove(base_geom)
            l1=list(base_geom.coords)
            a1 = get_direction(l1)
            #print(base_geom, end=' ')
            for geom_slice in geoms_slice:
                l2=list(geom_slice.coords)
                a2 = get_direction(l2)
                #print(a1, a2)
                if abs(a1-a2)>angle*2:
                    l2=[l2[1], l2[0]]
                    #print('flipped', a1, a2)
                else:
                    #print('not flipped', a1, a2)
                    pass
                geom_slice_index=geoms_slice.index(geom_slice)
                geoms_slice[geom_slice_index]=LineString(l2)
            geoms_slice.append(base_geom)
            gdf.at[i, 'line']=MultiLineString(geoms_slice)
            
    for i, val in gdf.iterrows():
        geometry=val.line
        if geometry.geom_type=='LineString':
            l1=list(geometry.coords)
        elif geometry.geom_type=='MultiLineString':
            l1=list(geometry.geoms[0].coords)
        direction=get_direction(l1)
        gdf.at[i, 'direction']=direction
    return gdf
def parallel_offset(gdf, dist):
    for j, val in gdf.iterrows():
        geometry=val.line
        part_ids=val.part_id
        if geometry.geom_type=='MultiLineString':
            parts=[list(x.coords) for x in list(geometry.geoms)]
            d=get_direction(parts[0])
            flag=None
            df = pd.DataFrame(parts, columns=['line_p1', 'line_p2'])
            df['p1_x']=[df['line_p1'][i][0] for i in range(len(df))]
            df['p1_y']=[df['line_p1'][i][1] for i in range(len(df))]
            df['p2_x']=[df['line_p2'][i][0] for i in range(len(df))]
            df['p2_y']=[df['line_p2'][i][1] for i in range(len(df))]
            if d<0:
                d=d+360
            #print(d, end=' ')
            if d>=45 and d<135:
                flag='Ox_left'
                df.sort_values(by='p1_x', ascending=True, inplace=True)
            elif d>=135 and d<225:
                flag='Oy_up'
                df.sort_values(by='p1_y', ascending=True, inplace=True)
            elif (d>=225 and d<315) or (d<=495 and d>405):
                flag='Ox_right'
                df.sort_values(by='p1_x', ascending=False, inplace=True)
            elif (d>=315 and d<=405) or (d>-360 and d<-270) or (d<45 and d>-45):
                flag='Oy_down'
                df.sort_values(by='p1_y', ascending=False, inplace=True)
            distance=dist
            df=df.reset_index(drop=True)
            lines=[[df['line_p1'][i], df['line_p2'][i]] for i in range(len(df))]
            offset_lines=[]
            if len(lines)%2==0:
                #print(flag, len(lines), part_ids)
                d=(distance*((len(lines)//2))-distance//2)
                for i in range(len(lines)):
                    #print(i, d)
                    offset=LineString(lines[i]).offset_curve(distance=d)
                    offset_lines.append(offset)
                    d-=distance
            elif len(lines)%2!=0:
                d=distance*(len(lines)//2)
                #print(flag, len(lines), part_ids)
                for i in range(len(lines)):
                    #d=d*i
                    #print(i, d)
                    offset=LineString(lines[i]).offset_curve(distance=d)
                    offset_lines.append(offset)
                    d-=distance
            gdf.at[j, 'line']=MultiLineString(offset_lines)
            gdf.at[j, 'flag']=flag
    return gdf
def export_rawgdf(gdf, name):
    # No buffer, no simple-index
    gdf['part_id']=gdf['part_id'].str.join(',')
    gdf.drop('simple_index', axis=1, inplace=True)
    gdf.drop('buffer', axis=1, inplace=True)
    gdf.set_geometry('line', inplace=True)
    gdf.set_crs(epsg=32635, inplace=True)
    gdf.to_file(filename=name, driver='GPKG')
    print(f'Exporting {name} finished')
def export_rawgdf_buf(gdf, name):
    # Buffer, no simple-index
    gdf['part_id']=gdf['part_id'].str.join(',')
    gdf.drop('simple_index', axis=1, inplace=True)
    gdf.drop('line', axis=1, inplace=True)
    gdf.set_geometry('buffer', inplace=True)
    gdf.set_crs(epsg=32635, inplace=True)
    gdf.to_file(filename=name, driver='GPKG')
    print(f'Exporting {name} finished')

def scaling(scale):
    Tgraph=0.02*scale/100 # 5m for 25000
    default_hallway_offset=100 # расстояние между нитками коридора
    offset = default_hallway_offset*Tgraph/4 # 125m for 25000
    buffer = offset*3/4
    default_angle=3 # 3deg for 25000
    angle=default_angle*(offset*2/default_hallway_offset)
    return offset, buffer, angle

with open('net_utm2.geojson', encoding='utf-8') as file:
    TL=json.loads(file.read())

offset, buffer, angle = scaling(20000)
print(offset, buffer, angle)
gdf_TL=init_gpd(TL)
gdf_exploded_TL=explode_gpd(gdf_TL)
print('Before buffering and cutting: ', len(gdf_exploded_TL))
gdf_buffer_TL=buffers_gpd(gdf_exploded_TL, buffer) # 3/4 of offset param
print('After buffering and cutting: ', len(gdf_buffer_TL))
export_rawgdf(gdf_buffer_TL.copy(), 'tests_cut.gpkg')
export_rawgdf_buf(gdf_buffer_TL.copy(), 'tests_buffer.gpkg')
gdf_processed=process_parts(gdf_buffer_TL, angle)
gdf_flipped=flip_order(gdf_processed, angle)
export_rawgdf(gdf_flipped.copy(), 'tests_flipped.gpkg')
gdf_offset=parallel_offset(gdf_flipped, offset)
export_rawgdf(gdf_offset.copy(), 'net_offset.gpkg')

# Hallway search can't be related to buffer size, it should be constant 
# To approve it, need more tests. Now the buffer size is 3/4 of offset parameter 

#TODO: restore lines from multilinestrings, provide info for segments by origin_id|part_id