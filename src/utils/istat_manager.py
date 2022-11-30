# TODO make this a class
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import shutil
import geopandas as gpd
import shapely
import pandas as pd

import utils.shapefile_manager as shp_manager

# TODO make these ENV vars
towns_borders_link = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012022_g.zip"
towns_borders_filename = "Com01012022_g_WGS84"
towns_borders_outpath = "data/istat/towns_borders"

towns_list_link = "https://www.istat.it/storage/codici-unita-amministrative/Archivio-elenco-comuni-codici-e-denominazioni_Anno_2022.zip"
towns_list_filename = "Codici-statistici-e-denominazioni-al-30_06_2022"
towns_list_outpath = "data/istat/towns_list"

class IstatManager:

    def __init__(self):
        # TODO merge these in same download function and code a utils which can download a zip properly
        self.download_towns_border()
        self.download_towns_list()
        self.towns_borders = gpd.read_file(os.path.join(towns_borders_outpath, "towns_borders.shp")).to_crs("EPSG:4326")

    def download_towns_border(self):
        if not os.path.exists(os.path.join(towns_borders_outpath, f"towns_borders.shp")):
            with urlopen(towns_borders_link) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as archive:
                    for filename in archive.namelist():
                        if towns_borders_filename in filename:
                            file = archive.open(filename)
                            file_format = filename.split(".")[-1]
                            outfile = open(os.path.join(towns_borders_outpath, f"towns_borders.{file_format}"), 'wb')
                            shutil.copyfileobj(file, outfile)
    
    def download_towns_list(self):
        if not os.path.exists(os.path.join(towns_list_outpath, f"towns_list.csv")):
            with urlopen(towns_list_link) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as archive:
                    for filename in archive.namelist():
                        if towns_list_filename in filename:
                            towns_list_df = pd.read_excel(archive.open(filename))
                            towns_list_df.to_csv(os.path.join(towns_list_outpath, "towns_list.csv"))

    def get_covered_cities(self, coverage_polygon: shapely.geometry.polygon.Polygon):
        return shp_manager.filter_intersection_geometries(coverage_polygon, self.towns_borders)
