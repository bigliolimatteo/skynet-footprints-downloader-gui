# TODO make this a class
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import shutil
import geopandas as gpd
import shapely

import utils.shapefile_manager as shp_manager

# TODO make these ENV vars
istat_link = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012022_g.zip"
istat_towns_filename = "Com01012022_g_WGS84"
istat_towns_outpath = "data/istat/towns_borders"

class IstatManager:

    def __init__(self):
        self.download()
        self.towns_borders = gpd.read_file(os.path.join(istat_towns_outpath, "towns_borders.shp")).to_crs("EPSG:4326")

    def download(self):
        if not os.path.exists(os.path.join(istat_towns_outpath, f"towns_borders.shp")):
            with urlopen(istat_link) as zipresp:
                with ZipFile(BytesIO(zipresp.read())) as archive:
                    for filename in archive.namelist():
                        if istat_towns_filename in filename:
                            file = archive.open(filename)
                            file_format = filename.split(".")[-1]
                            outfile = open(os.path.join(istat_towns_outpath, f"towns_borders.{file_format}"), 'wb')
                            shutil.copyfileobj(file, outfile)

    def get_covered_cities(self, coverage_polygon: shapely.geometry.polygon.Polygon):
        return shp_manager.filter_intersection_geometries(coverage_polygon, self.towns_borders)
