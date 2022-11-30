from utils.istat_manager import IstatManager

import argparse
import os
import geopandas as gpd

def main(input_coverage_shapefile):
    coverage_gdf = gpd.read_file(input_coverage_shapefile)
    coverage_polygon = list(coverage_gdf["geometry"])[0]

    istat_manager = IstatManager()
    covered_cities = istat_manager.get_covered_cities(coverage_polygon)
    print(covered_cities)

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input_coverage_shapefile", required=True, type=str, help="Path to a shapefile containing the coverage of interest")
    
    args = parser.parse_args()
    
    if not args.input_coverage_shapefile.endswith("shp") or not os.path.exists(args.input_coverage_shapefile):
        parser.error("input_coverage_shapefile must be an existing shapefile.")
    
    main(args.input_coverage_shapefile)
