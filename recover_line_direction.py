import geopandas as gpd
from shapely import LineString
from vector_algs_handler import *
from io_handler import *


def recover_line_dir_by_origin(gdf, gdf_origin):
    def part_id_new(part_id):
        part_id=part_id[0]
        part_id_1, part_id_2, part_id_3 = part_id.split('_')[0], part_id.split('_')[1], part_id.split('_')[2]
        flag1, flag2 = False, False
        while flag1==False:
            if part_id_1[0]=='0' and len(part_id_1)>1:
                part_id_1=part_id_1[1:]
            else:
                flag1=True
                
        while flag2==False:
            if part_id_2[0]=='0' and len(part_id_2)>1:
                part_id_2=part_id_2[1:]
            else:
                flag2=True
                
        return f'{part_id_1}_{part_id_2}'


    for i, val in gdf.iterrows():
        printProgressBar(i + 1, len(gdf), prefix = 'Recovering lines:', suffix = 'Complete', length = 50)
        line=val.line
        part_id=part_id_new(val.part_id)
        origin=gdf_origin.loc[gdf_origin['part_id']==part_id]
        line_origin=list(origin['line'])[0]
        a=get_direction(list(line.coords))
        a_origin=get_direction(list(line_origin.coords))
        if a-a_origin>90:
            new_order=LineString(list(reversed(line.coords)))
            gdf.at[i, 'line']=new_order
    return gdf