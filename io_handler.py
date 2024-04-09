import geopandas as gpd
import json
import pandas as pd
from pandas.api.types import is_string_dtype
def importer(name, epsg=32635):
    with open(name, encoding='utf-8') as file:
        d=json.loads(file.read())
    gdf=gpd.GeoDataFrame.from_features(d['features'])
    gdf.set_crs(epsg=epsg, inplace=True)
    return gdf

def exporter(gdf, name, driver='GPKG', keep_debug=True, buffer=False, epsg=32635):
    if keep_debug:
        
        if is_string_dtype(gdf['part_id'])==False:
            gdf['part_id']=gdf['part_id'].str.join(',')
        if is_string_dtype(gdf['simple_index'])==False:
            gdf['simple_index']=gdf['simple_index'].str.join(',')
            #print(gdf['simple_index'])
        #gdf.drop('simple_index', axis=1, inplace=True)
        if buffer==False:
            if 'buffer' in gdf.columns:
                gdf.drop('buffer', axis=1, inplace=True)
            gdf_new=gdf.set_geometry('line')
        else:
            gdf.drop('line', axis=1, inplace=True)
            gdf_new=gdf.set_geometry('buffer')

    else:
        gdf.drop('part_id', axis=1, inplace=True)
        gdf.drop('simple_index', axis=1, inplace=True)
        gdf.drop('buffer', axis=1, inplace=True)
        gdf.drop('direction', axis=1, inplace=True)
        gdf.drop('flag', axis=1, inplace=True)
        gdf_new=gdf.set_geometry('line')
    #print(gdf)
    #if 'geometry' in list(gdf.columns):
    #print(gdf.columns)
    gdf_new.set_crs(epsg=epsg, inplace=True)
    #print(gdf_new.columns)
    gdf_new.to_file(filename=name, driver=driver)
    print(f'Exporting {name} finished')

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()