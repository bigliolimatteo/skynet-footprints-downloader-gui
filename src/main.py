from utils.istat_manager import IstatManager
import utils.pcm_manager as pcm_manager
import utils.shapefile_manager as shapefile_manager

import argparse
import os
import geopandas as gpd
import pandas as pd

def main(input_coverage_shapefile):
    coverage_gdf = gpd.read_file(input_coverage_shapefile)
    coverage_polygon = list(coverage_gdf["geometry"])[0]

    istat_manager = IstatManager()
    covered_towns = istat_manager.get_covered_towns(coverage_polygon)
    covered_towns_istat_info = istat_manager.get_istat_info_from_town_codes(covered_towns["PRO_COM"].values)
    covered_buildings_gdfs = list()
    for _, town_data in covered_towns_istat_info.iterrows():   
        tmp_town_gdf = pcm_manager.download_town_buildings_shp(town_data["area_istat_name"], town_data["region_name"], town_data["province_name"], town_data["town_name"])
        covered_buildings_gdfs.append(shapefile_manager.filter_intersection_geometries(coverage_polygon, tmp_town_gdf))
    covered_buildings_gdf = gpd.GeoDataFrame(pd.concat(covered_buildings_gdfs, ignore_index=True))
    print(covered_buildings_gdf)
    covered_buildings_gdf.to_file("test/extraction.shp")

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input_coverage_shapefile", required=True, type=str, help="Path to a shapefile containing the coverage of interest")
    
    args = parser.parse_args()
    
    if not args.input_coverage_shapefile.endswith("shp") or not os.path.exists(args.input_coverage_shapefile):
        parser.error("input_coverage_shapefile must be an existing shapefile.")
    
    main(args.input_coverage_shapefile)
