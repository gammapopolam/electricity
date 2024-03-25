import geopandas as gpd
from io_handler import *
from hallway_recognition import *
from vector_algs_handler import *
from intersection_handler import *
from shapely import unary_union, normalize
from shapely.geometry import Point
from sympy.solvers.solveset import linsolve
from sympy import *

def explode_gpd(gdf):
    line_segs = gpd.GeoSeries(gdf["geometry"]
    .apply(lambda g: [g] if isinstance(g, LineString) else [p for p in g.geoms])
    .apply(lambda l: [LineString([c1, c2]) for p in l for c1, c2 in zip(p.coords, list(p.coords)[1:])])
    .explode())
    gdf_exploded=line_segs.to_frame().join(gdf.drop(columns="geometry")).reset_index(drop=True)
    # Some mistake in gdf_exploded columns
    try:
    # FOR HOME-PC
        gdf_exploded.rename(columns={'id':'origin_id', 'geometry': 'line'}, inplace=True)
    # FOR LAPTOP
    except:
        gdf_exploded.rename(columns={'id':'origin_id', 0: 'line'}, inplace=True)

    gdf_exploded['part_id']=gdf_exploded.origin_id.astype(str)+'_'+gdf_exploded.index.astype(str)
    gdf_exploded=gdf_exploded.set_geometry('line')
    for i, val in gdf_exploded.iterrows():
        part_id=val.part_id
        line=val.line
        origin_id=val.origin_id
        gdf_exploded.iloc[i]={
            'line': line,
            'origin_id': str(origin_id),
            'part_id': part_id.split('_')[0].zfill(5)+'_'+part_id.split('_')[1].zfill(5)+'_00000',
            'simple_index': None
            }
    return gdf_exploded

def buffers_gpd(gdf, distance):
    gdf['buffer']=gdf.geometry.buffer(distance=distance, cap_style=2, join_style=2)
    # этот маневр будет стоить нам семи лет
    buffers=gpd.GeoDataFrame(geometry=gdf['buffer'])
    gdf=gdf.overlay(buffers, "intersection")
    gdf=restore_lines(gdf)
    #print(gdf.columns)
    gdf.rename(columns={'geometry': 'line'}, inplace=True)
    #print(gdf.columns)
    gdf.set_geometry('line', inplace=True)
    #print(gdf.columns)
    gdf.drop(columns=['buffer'], inplace=True)
    gdf['buffer']=gdf.geometry.buffer(distance=distance, cap_style=2, join_style=2)
    #print(gdf.columns)
    
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
        origin_id=list(gdf_slice['origin_id'])[0]
        if len(gdf_slice)>1:
            parts=[list(x.coords) for x in gdf_slice.geometry]
            #if list(gdf_slice.geometry)[0].is_empty:
            #    print(gdf_slice)
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
    return gdf
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
            
            search=HallwaySearch(l1, l1_buff, l2, l2_buff, angle)
            flag=search.solve()
            if flag=='stream':
                if isinstance(val1_part_id, str) and isinstance(val2.part_id, str):
                    part_ids=[val1_part_id, val2.part_id]
                elif isinstance(val1_part_id, str) and isinstance(val2.part_id, list):
                    part_ids=[val1_part_id, *val2.part_id]
                elif isinstance(val1_part_id, list) and isinstance(val2.part_id, str):
                    part_ids=[*val1_part_id, val2.part_id]
                elif isinstance(val1_part_id, list) and isinstance(val2.part_id, list):
                    part_ids=[*val1_part_id, *val2.part_id]
                l1=search.to_multiline(flag)
                l1_buff=normalize(unary_union([l1_buff, l2_buff]))
                val1_part_id=list(set(part_ids))
                gdf=gdf[gdf.line!=val2.line]
                gdf.at[i, 'line']=l1
                gdf.at[i, 'buffer']=l1_buff
                gdf.at[i, 'origin_id']=int(val1.origin_id)
                gdf.at[i, 'part_id']=val1_part_id
                gdf.at[i, 'simple_index']=simple_index(l1_buff, gdf, i)
    return gdf
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
def parallel_offset(gdf, gdf_source, dist):
    for j, val in gdf.iterrows():
        geometry=val.line
        if geometry.geom_type=='MultiLineString':
            parts=[list(x.coords) for x in list(geometry.geoms)]
            part_ids=[]
            flag=None
            l=len(parts)
            sides=dict()
            for k in range(l):
                sides[k]=[]
            for p in range(l):
                line_cur=parts[p]
                for h in range(l):
                    line_hall=parts[h]
                    if line_side(line_cur, line_hall)==-1:
                        sides[p].insert(0, line_side(line_cur, line_hall))
                    elif line_side(line_cur, line_hall)==1:
                        sides[p].insert(len(sides[p]), line_side(line_cur, line_hall))
                    elif line_side(line_cur, line_hall)==0:
                        sides[p].insert(len(sides[p])//2, line_side(line_cur, line_hall))
                    sides[p]=list(sorted(sides[p]))
            # сейчас в sides ключ: индекс, значение: [1,0,-1,-1] (как пример)
            distance=dist
            offset_lines=[]
            for index in range(l):
                
                side1=sides[index]
                line=parts[index]
                osp = side1.index(0)
                d = distance * (len(side1)//2 - osp)
                if l%2==0:
                    d = d - distance//2
                offset=LineString(line).offset_curve(distance=d)
                offset_part_id=get_part_id(LineString(line), gdf_source)
                #print(side1, d, offset_part_id)
                part_ids.append(offset_part_id[0])
                
                offset_lines.append(offset)
            #print(d, end=' ')
            # Раньше был оффсет по направлениям коридора
            # сейчас необходима вспомогательная функция side для всего коридора
            # список с флагами -1,0,1 ( справа, текущая, слева)
            # в зависимости от того, какое значение в результате side, помещать либо в начало либо в конец
            gdf.at[j, 'line']=MultiLineString(offset_lines)
            gdf.at[j, 'flag']=flag
            gdf.at[j, 'part_id']=part_ids
            #print(gdf.at[j, 'part_id'])
    return gdf
def get_part_id(line, gdf_source):
    for i, val in gdf_source.iterrows():
        source_line=val.line
        part_id=val.part_id
        if equals(line, source_line):
            return part_id
def unpack_multilines(gdf_offset):
    gdf_empty=gdf_offset.drop(gdf_offset.index)
    
    for i, val in gdf_offset.iterrows():
        geometry=val.line
        if geometry.geom_type=='MultiLineString':
            geoms=list(geometry.geoms)
            part_ids=val.part_id
            for j in range(len(geoms)):
                line=geoms[j]
                if len(part_ids[j].split('_'))==3:
                    part1=part_ids[j].split('_')[0]
                    part2=part_ids[j].split('_')[1]
                    part3=part_ids[j].split('_')[2]
                elif len(part_ids[j].split('_'))==2:
                    part1=part_ids[j].split('_')[0]
                    part2=part_ids[j].split('_')[1]
                    part3='0'
                part_id=f'{part1.zfill(5)}_{part2.zfill(5)}_{part3.zfill(5)}'
                gdf_line=gpd.GeoDataFrame({'line': line, 'origin_id':part_id.split('_')[0], 'direction': None, 'flag':None, 'part_id':[[part_id]]})
                gdf_empty=pd.concat([gdf_empty, gdf_line], ignore_index=True, axis=0)
        else:
            partid=val.part_id[0]
            if len(partid.split('_'))==3:
                part1=partid.split('_')[0]
                part2=partid.split('_')[1]
                part3=partid.split('_')[2]
            elif len(partid.split('_'))==2:
                part1=partid.split('_')[0]
                part2=partid.split('_')[1]
                part3='0'
            part_id=f'{part1.zfill(5)}_{part2.zfill(5)}_{part3.zfill(5)}'
            gdf_line=gpd.GeoDataFrame({'line': geometry, 'origin_id':part_id.split('_')[0], 'direction': None, 'flag':None, 'part_id':[[part_id]]})
            gdf_empty=pd.concat([gdf_empty, gdf_line], ignore_index=True, axis=0)
    gdf_fin=gdf_empty.reset_index(drop=True)
    return gdf_fin
def recover_line_dir(gdf):
    uniqs=list(sorted(gdf['origin_id'].unique()))
    for uniq in uniqs:
        gdf_origin=gdf.copy()
        gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
        gdf_origin=gdf_origin[gdf_origin['origin_id']==uniq]
        gdf_origin['part_id2']=gdf_origin['part_id'].apply(lambda x: x[0].split('_')[1])
        gdf_origin['part_id3']=gdf_origin['part_id'].apply(lambda x: x[0].split('_')[2])
        uniqs_part2=list(sorted(gdf_origin['part_id2'].unique()))
        for current in uniqs_part2:
            l=len(gdf_origin[gdf_origin['part_id2']==current])
            if l>1:
                ctr=1
                back=str(int(current)-ctr).zfill(5)
                back_geom = gdf_origin[gdf_origin['part_id2']==back]
                
                while len(back_geom)==0:
                    ctr+=1
                    back=str(int(current)-ctr).zfill(5)
                    back_geom = gdf_origin[gdf_origin['part_id2']==back]
                current_geoms=gdf_origin[gdf_origin['part_id2']==current]
                flipped=[]
                b2=Point(list(list(back_geom['line'])[0].coords)[1])
                for _, current in current_geoms.iterrows():
                    c1=Point(list(current['line'].coords)[0])
                    newdist=float(b2.distance(c1))
                    flipped.append({'part_id2': current['part_id2'], 'part_id3': current['part_id3'], 'distance': newdist, 'geometry': current['line']})
                sorted_flipped=sorted(flipped, key=lambda d: d['distance'])
                sorted_flipped2=[]
                if flipped[0]!=sorted_flipped[0]:
                    for elems in sorted_flipped:
                        l=len(sorted_flipped)
                        new_part_id3=str(l-int(elems['part_id3'])-1).zfill(5)
                        elems['part_id3']=new_part_id3
                        sorted_flipped2.append(elems)
                else:
                    sorted_flipped2=sorted_flipped
                for elems in sorted_flipped2:
                    full_part_id=f'{uniq}_{elems['part_id2']}_{elems['part_id3']}'
                    gdf.loc[gdf['part_id'].isin([[full_part_id]]), 'line']=elems['geometry']
    return gdf 
def recover_net(gdf):
    return 0

    uniqs=list(sorted(gdf['origin_id'].unique()))
    gdf_empty=gdf.drop(gdf.index)
    gdf_points=None
    for uniq in uniqs:
        #print(uniq)
        gdf_origin=gdf.copy()
        gdf_origin=gdf_origin[gdf_origin['origin_id']==uniq]
        l=len(gdf_origin)
        origin_geom=[]
        gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
        # TODO: инициализируем origin_geom, добавляем в него первый сегмент
        # в цикле для всех других сегментов смотрим:
        # нужно проанализировать точки сегментов на близость и по необходимости поменять местами координаты
        # - пересекается ли origin_geom с сегментом? 
        # - если пересекается, то добавить точки сегмента

        # - если не пересекается, то пересекаются ли прямые этих сегментов в окне? (брать у origin_geom последние две точки)
        # - если пересекаются, то добавить точки сегмента
        # - если не пересекаются, то исключить сегмент
        line_cur=canline(gdf_origin.at[0, 'line'])
        line_cur_partid=gdf_origin.at[0, 'part_id']
        origin_geom.append(line_cur.p1)
        origin_geom.append(line_cur.p2)
        gdf_origin=gdf_origin.drop(index=0)
        gdf_origin.reset_index(drop=True, inplace=True)
        while l!=0:
            line_cur=canline(LineString((origin_geom[-2], origin_geom[-1])))
            #print(gdf_origin)
            line_next_partid=gdf_origin.at[0, 'part_id']
            line_next=canline(gdf_origin.at[0, 'line'])
            print(line_cur_partid, line_next_partid)
            gdf_origin=gdf_origin.drop(index=0)
            gdf_origin.reset_index(drop=True, inplace=True)
            l=len(gdf_origin)
            p2p1=Point(line_cur.p2).distance(Point(line_next.p1))
            p2p2=Point(line_cur.p2).distance(Point(line_next.p2))
            p1p1=Point(line_cur.p1).distance(Point(line_next.p1))
            p1p2=Point(line_cur.p1).distance(Point(line_next.p2))
            if p2p1>p2p2 or p2p1>p1p1:
                #print('flip')
                line_next=canline(LineString((line_next.p2, line_next.p1)))
            #elif p2p1>p1p1:
            #    line_next=canline(LineString((line_next.p, line_next)))
            x, y = symbols('x, y')
            #print(line_cur_partid, line_next_partid, linsolve([line_cur.get_canonical(), line_next.get_canonical()], (x, y)))
            
            if line_cur_partid!=line_next_partid:
                if line_next.p1 not in origin_geom:
                    origin_geom.append(line_next.p1)
                if line_cur.geom.intersects(line_next.geom):
                    print('net-segments intersect')
                    p_int=line_cur.geom.intersection(line_next.geom)
                    print(p_int)
                    if p_int.geom_type=='Point':
                        p_int=(p_int.x, p_int.y)
                        origin_geom.pop(-1)
                        origin_geom.append(p_int)
                        if line_next.p2 not in origin_geom:
                            origin_geom.append(line_next.p2)
                    #line_cur=canline(LineString((p_int, line_next.p2)))
                    line_cur_partid=line_next_partid
                else:
                    p_int, =linsolve([line_cur.get_canonical(), line_next.get_canonical()], (x, y))
                    

                    dx1=abs(line_cur.p2[0]-p_int[0])
                    dx2=abs(line_next.p1[0]-p_int[0])
                    dy1=abs(line_cur.p2[1]-p_int[1])
                    dy2=abs(line_next.p1[1]-p_int[1])
                    dx=abs(line_cur.p2[0]-line_next.p1[0])
                    dy=abs(line_cur.p2[1]-line_next.p1[1])
                    #print(f'P1P2 endpoints: {dx, dy}')
                    #print(f'P1Pint endpoints: {dx1, dy1}')
                    #print(f'P2Pint endpoints: {dx2, dy2}')

                    if dx1<dx*2 and dx2<dx*2 and dy1<dy*2 and dy2<dy*2 and dx!=dy:
                        print('lines intersect')
                        print(p_int)
                        origin_geom.pop(-1)
                        origin_geom.append(p_int)
                        if line_next.p2 not in origin_geom:
                            origin_geom.append(line_next.p2)
                        #line_cur=canline(LineString((p_int, line_next.p2)))
                    else:
                        continue
                        #origin_geom.pop(-1)
                        #line_cur=canline(LineString((p_int, line_next.p2)))
                        #line_cur=line_next
                    line_cur_partid=line_next_partid

        gdf_line=gpd.GeoDataFrame({'line': LineString(origin_geom), 'origin_id':[uniq], 'direction': None, 'flag':None, 'part_id':None})
        gdf_empty=pd.concat([gdf_empty, gdf_line], ignore_index=True, axis=0)
    return gdf_empty
def recover_net_new(gdf):
    # Нужна новая логика для восстановления
    uniqs=list(sorted(gdf['origin_id'].unique()))
    gdf_empty=gdf.drop(gdf.index)
    gdf_points=None
    for uniq in uniqs:
        #print(uniq)
        gdf_origin=gdf.copy()
        gdf_origin=gdf_origin[gdf_origin['origin_id']==uniq]
        l=len(gdf_origin)
        origin_geom=[]
        gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
        lines=list(gdf_origin['line'])
        line_current=lines.pop(0)
        while len(lines)!=1:
            line_next=lines.pop(0)
            solved=segment_solver(line_current, line_next)
            if solved is not None:
                line_current, line_next = solved
                origin_geom.append(*list(line_current.coords))
                origin_geom.append(*list(line_next.coords))
            line_current=LineString((origin_geom[-2], origin_geom[-1]))
        line_end=lines.pop()
        origin_geom.append(list(line_end.coords)[1])
def config(scale):
    Tgraph=0.02*scale/100 # 5m for 25000
    default_hallway_offset=100 # расстояние между нитками коридора
    offset = default_hallway_offset*Tgraph/4 # 125m for 25000
    buffer = 200
    default_angle=3 # 3deg for 25000
    angle=8
    return offset, buffer, angle
offset, buffer, angle = config(25000)
gdf=importer('samples/tests_utm3.geojson', epsg=32635)
gdf_exploded=explode_gpd(gdf)
gdf_buffer=buffers_gpd(gdf_exploded, buffer)
gdf_source=gdf_buffer.copy()
#hallway search
gdf_processed=process_parts(gdf_buffer, angle)
gdf_flipped=flip_order(gdf_processed, angle)
gdf_offset=parallel_offset(gdf_flipped, gdf_source, offset)
gdf_unpacked=unpack_multilines(gdf_offset)
gdf_recover=recover_line_dir(gdf_unpacked)
exporter(gdf_recover, name='tests_recover.gpkg')
gdf_net=recover_net(gdf_recover)