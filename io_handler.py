import geopandas as gpd
import json
import pandas as pd

def importer(name, epsg=32635):
    with open(name, encoding='utf-8') as file:
        d=json.loads(file.read())
    gdf=gpd.GeoDataFrame.from_features(d['features'])
    gdf.set_crs(epsg=epsg, inplace=True)
    return gdf

def exporter(gdf, name, driver='GPKG', keep_debug=True):
    if keep_debug:
        gdf['part_id']=gdf['part_id'].str.join(',')
        #gdf.drop('simple_index', axis=1, inplace=True)
        gdf.drop('buffer', axis=1, inplace=True)
    else:
        gdf.drop('part_id', axis=1, inplace=True)
        gdf.drop('simple_index', axis=1, inplace=True)
        gdf.drop('buffer', axis=1, inplace=True)
        gdf.drop('direction', axis=1, inplace=True)
        gdf.drop('flag', axis=1, inplace=True)
    gdf.set_geometry('line', inplace=True)
    gdf.to_file(filename=name, driver=driver)
    print(f'Exporting {name} finished')

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()