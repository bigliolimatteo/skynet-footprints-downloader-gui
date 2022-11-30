import utils.istat_downloader as istat_downloader 

import argparse
import os

def main():
    istat_downloader.download()

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input_coverage", required=True, type=str, help="Path to a shapefile containing the coverage of interest")
    
    args = parser.parse_args()
    
    if not args.input_coverage.endswith("shp") or not os.path.exists(args.input_coverage):
        parser.error("input_coverage must be an existing shapefile.")
    
    print(args)

    main()
