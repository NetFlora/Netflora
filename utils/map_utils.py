"""

File Name: autoanchor.py
Origin: Netflora (https://github.com/WongKinYiu/yolov7)

"""

import folium
import geopandas as gpd
import branca.colormap as cm
import json

with open('processing/variable.json', 'r') as file:
    variables = json.load(file)

crs = variables['crs']
algorithm = variables['algorithm']


gdf_path = f'results/shapefiles/resultados_{algorithm}.shp'

gdf = gpd.read_file(gdf_path)

def createMap():
    
    gdf_reproj = gdf.to_crs(epsg=4326)

    
    centroide = gdf_reproj.unary_union.centroid

    
    geojson_data = gdf_reproj.to_json()

   
    mapa = folium.Map(location=[centroide.y, centroide.x], zoom_start=17, tiles=None)

    
    _add_layers(mapa)

    
    paleta_cores = cm.linear.Set1_09.scale(0, gdf_reproj['class_id'].max())

    
    geojson_layer = folium.GeoJson(
        geojson_data,
        name='Shapefile',
        style_function=lambda feature: {
            'fillColor': _get_color(feature, paleta_cores),
            'color': 'black',
            'weight': 1,
            'opacity': 0.8,
            'fillOpacity': 1
        }
    ).add_to(mapa)

    
    paleta_cores.caption = 'Classes'
    paleta_cores.add_to(mapa)
    folium.LayerControl().add_to(mapa)

    return mapa

def _add_layers(mapa):
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='OpenStreetMap').add_to(mapa)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite',
        overlay=False
    ).add_to(mapa)

def _get_color(feature, paleta_cores):
    class_id = feature['properties']['class_id']
    return paleta_cores(class_id)
