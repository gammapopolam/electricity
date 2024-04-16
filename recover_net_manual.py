#%%
import geopandas as gpd
from intersection_handler import *
from io_handler import *
import folium
import random
import shapely.geometry
def sort_nearest(line_current, lines):
    lines_slice=lines[:4]
    cur_p2=shapely.geometry.Point(list(line_current.coords)[-1])
    dists=dict()
    indexes=dict()
    for i in range(len(lines_slice)):
        line_next=lines_slice[i]
        next_p1=shapely.geometry.Point(list(line_next.coords)[0])
        dist=cur_p2.distance(next_p1)
        dists[i]=dist
        indexes[i]=line_next
    sort_dists={k: v for k, v in sorted(dists.items(), key=lambda item: item[1])}
    #print(sort_dists)
    sort_lines=[indexes[x] for x in sort_dists.keys()]
    new_order_lines=sort_lines+lines[4:]
    return new_order_lines
gdf_recover=gpd.read_file('coursework/line_recovered.gpkg')
gdf_recover.rename(columns ={'geometry':'line'}, inplace=True)
def recover_net(gdf):
    uniqs=list(sorted(gdf['origin_id'].unique()))
    gdf_empty=gdf.drop(gdf.index)
    gdf_points=None
    i=0
    logs=open('logs.txt', 'w')
    logs.close()
    
    for uniq in uniqs:
        printProgressBar(i + 1, len(uniqs), prefix = 'Recovering net:', suffix = 'Complete', length = 50)
        i+=1
        #print(uniq)
        gdf_origin=gdf.copy()
        gdf_origin=gdf_origin[gdf_origin['origin_id']==uniq]
        gdf_origin.drop_duplicates(subset='part_id', keep="first", inplace=True)
        #print(gdf_origin)
        l=len(gdf_origin)
        #print(l)
        origin_geom=[]
        gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
        lines=list(gdf_origin['line']) # correct sort

        origin_geom=[]
        if len(lines)<3:
            continue
        first=lines.pop(0)
        line=lines.pop(0)
        first, line=flip_segments(first, line, first=True)
        origin_geom.append(list(first.coords)[0])
        origin_geom.append(list(line.coords)[0])
        origin_geom.append(list(line.coords)[1])
        #lines = list(filter(lambda x: (x.length>200), lines))
        
        while len(lines)>1:
            #print(origin_geom)
            logs=open('logs.txt', 'a')
            try:
                logs_check=open('logs.txt', 'r')
                line_current = LineString((origin_geom[-2], origin_geom[-1]))
            except IndexError:
                if f'Recover {uniq}: error\n' not in logs_check.read():
                    logs.write(f'Recover {uniq}: error\n')
                    logs.close()
                    break
            else:
                if f'Recover {uniq}: success\n' not in logs_check.read():
                    logs.write(f'Recover {uniq}: success\n')
                    logs.close()
                lines=sort_nearest(line_current, lines)
                line_next=lines[0]
                #print(origin_geom)
                line_current, line_next = flip_segments(line_current, line_next)
                #print(line_current, line_next)
                #print(len(lines))
                solved=segment_solver(line_current, line_next)
                if solved is not None:
                    line_current, line_next = solved
                    origin_geom.pop()
                    origin_geom.pop()
                    lines.pop(0)
                    if list(line_current.coords)[0] not in origin_geom:
                        origin_geom.append(list(line_current.coords)[0])
                    if list(line_current.coords)[1] not in origin_geom:
                        origin_geom.append(list(line_current.coords)[1])
                    if list(line_next.coords)[1] not in origin_geom:
                        origin_geom.append(list(line_next.coords)[1])
                else:
                    origin_geom.pop()
                    continue
                '''
            while len(lines)>2:
                line_current = LineString((origin_geom[-2], origin_geom[-1]))
                line_next=lines[0]
                line_current, line_next = flip_segments(line_current, line_next)
                solved=segment_solver(line_current, line_next)
                #print('current', line_current, line_next)
                line_current1 = LineString((origin_geom[-2], origin_geom[-1]))
                line_next1=lines[1]
                line_current1, line_next1 = flip_segments(line_current1, line_next1)
                solved_test1=segment_solver(line_current1, line_next1)
                #print('test', line_current1, line_next1)
                #print(origin_geom)
                if solved is not None:
                    line_current, line_next = solved
                    if solved_test1 is not None:
                        line_current1, line_next1 = solved_test1

                        p_test = list(line_current.coords)[0]
                        p_int = list(line_next.coords)[0]
                        p_int1 = list(line_next1.coords)[0]
                        #print('test1', LineString((p_test, p_int)), LineString((p_test, p_int1)))
                        if LineString((p_test, p_int)).length<LineString((p_test, p_int1)).length:
                            #print('test false')
                            origin_geom.pop()
                            origin_geom.pop()
                            lines.pop(0)
                            if list(line_current.coords)[0] not in origin_geom:
                                origin_geom.append(list(line_current.coords)[0])
                            if list(line_current.coords)[1] not in origin_geom:
                                origin_geom.append(list(line_current.coords)[1])
                            if list(line_next.coords)[1] not in origin_geom:
                                origin_geom.append(list(line_next.coords)[1])
                        else:
                            #print('test true')
                            #line_current, line_next = line_current1, line_next1
                            origin_geom.pop()
                            origin_geom.pop()
                            lines.pop(0)
                            lines.pop(0)
                            if list(line_current1.coords)[0] not in origin_geom:
                                origin_geom.append(list(line_current1.coords)[0])
                            if list(line_current1.coords)[1] not in origin_geom:
                                origin_geom.append(list(line_current1.coords)[1])
                            if list(line_next1.coords)[1] not in origin_geom:
                                origin_geom.append(list(line_next1.coords)[1])
                    else:
                        origin_geom.pop()
                        origin_geom.pop()
                        lines.pop(0)
                        if list(line_current.coords)[0] not in origin_geom:
                            origin_geom.append(list(line_current.coords)[0])
                        if list(line_current.coords)[1] not in origin_geom:
                            origin_geom.append(list(line_current.coords)[1])
                        if list(line_next.coords)[1] not in origin_geom:
                            origin_geom.append(list(line_next.coords)[1])
                else:
                    origin_geom.pop()
                    continue
            '''
        try:
            LineString(origin_geom)
        except shapely.errors.GEOSException:
            pass
        else:
            gdf_line=gpd.GeoDataFrame({'line': LineString(origin_geom), 'origin_id':[uniq], 'direction': None, 'flag':None, 'part_id':None})
            gdf_line.set_geometry('line', inplace=True)
            gdf_line.set_crs(epsg='32635', inplace=True)
            gdf_empty=pd.concat([gdf_empty, gdf_line], ignore_index=True, axis=0)
    #logs.close()
    return gdf_empty

def recover_net_old(gdf, uniq):
    uniqs=list(sorted(gdf['origin_id'].unique()))
    gdf_empty=gdf.drop(gdf.index)
    gdf_points=None

    #print(uniq)
    gdf_origin=gdf.copy()
    gdf_origin=gdf_origin[gdf_origin['origin_id']==uniq]
    gdf_origin.drop_duplicates(subset='part_id', keep="first", inplace=True)
    #print(gdf_origin)
    l=len(gdf_origin)
    #print(l)
    origin_geom=[]
    gdf_origin.sort_values(by='part_id', ascending=True, inplace=True,ignore_index=True)
    lines=list(gdf_origin['line']) # correct sort

    origin_geom=[]
    first=lines.pop(0)
    line=lines.pop(0)
    #first, line=flip_segments(first, line, first=True)
    origin_geom.append(list(first.coords)[0])
    origin_geom.append(list(line.coords)[0])
    origin_geom.append(list(line.coords)[1])
    #lines = list(filter(lambda x: (x.length>200), lines))
    
    while len(lines)>1:
        print(LineString(origin_geom), lines[0])
        line_current = LineString((origin_geom[-2], origin_geom[-1]))
        line_next=lines[0]
        #print(origin_geom)
        #line_current, line_next = flip_segments(line_current, line_next)
        #print(line_current, line_next)
        #print(len(lines))
        solved=segment_solver(line_current, line_next)
        if solved is not None:
            line_current, line_next = solved
            origin_geom.pop()
            origin_geom.pop()
            lines.pop(0)
            if list(line_current.coords)[0] not in origin_geom:
                origin_geom.append(list(line_current.coords)[0])
            if list(line_current.coords)[1] not in origin_geom:
                origin_geom.append(list(line_current.coords)[1])
            if list(line_next.coords)[1] not in origin_geom:
                origin_geom.append(list(line_next.coords)[1])
        else:
            origin_geom.pop()
            continue
    try:
        LineString(origin_geom)
    except shapely.errors.GEOSException:
        pass
    else:
        gdf_line=gpd.GeoDataFrame({'line': LineString(origin_geom), 'origin_id':[uniq], 'direction': None, 'flag':None, 'part_id':None})
        gdf_line.set_geometry('line', inplace=True)
        gdf_line.set_crs(epsg='32635', inplace=True)
        gdf_empty=pd.concat([gdf_empty, gdf_line], ignore_index=True, axis=0)
    #logs.close()
    return gdf_empty
gdf_net=recover_net(gdf_recover)

exporter(gdf_net.copy(), name='coursework/final.gpkg', keep_debug=True, epsg=32635)

#%%
gdf_net.set_geometry('line', inplace=True)
gdf_net.to_crs('EPSG:4326', inplace=True)
centermap=[gdf_net.line[0].centroid.y, gdf_net.line[0].centroid.x]
m=folium.Map(location=centermap, tiles='CartoDB Positron', zoom_start=9)
folium.GeoJson(gdf_net.line).add_to(m)
gdf_recover_4326=gdf_recover.set_geometry('line')
gdf_recover_4326['color']=gdf_recover_4326.apply(lambda x: f"#{random.randrange(0x1000000):06x}", axis=1)

gdf_recover_4326.to_crs('EPSG:4326')

folium.GeoJson(gdf_recover_4326[gdf_recover_4326['origin_id']=='00006'])
m
# %%
gdf_net
# %%
