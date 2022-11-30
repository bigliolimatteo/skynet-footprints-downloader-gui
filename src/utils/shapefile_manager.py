import geopandas as gpd
import shapely

def filter_intersection_geometries(coverage_polygon: shapely.geometry.polygon.Polygon, input_geodataframe: gpd.GeoDataFrame):
    intersection_array = input_geodataframe.geometry.map(lambda x: x.intersects(coverage_polygon))
    return input_geodataframe[intersection_array]
