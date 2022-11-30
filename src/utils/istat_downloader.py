# TODO make this a class
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import os
import shutil

# TODO make these ENV vars
istat_link = "https://www.istat.it/storage/cartografia/confini_amministrativi/generalizzati/Limiti01012022_g.zip"
istat_towns_filename = "Com01012022_g_WGS84"
istat_towns_outpath = "data/istat/towns_borders"

def download():
    if not os.path.exists(os.path.join(istat_towns_outpath, f"towns_borders.shp")):
        with urlopen(istat_link) as zipresp:
            with ZipFile(BytesIO(zipresp.read())) as archive:
                for filename in archive.namelist():
                    if istat_towns_filename in filename:
                        file = archive.open(filename)
                        file_format = filename.split(".")[-1]
                        outfile = open(os.path.join(istat_towns_outpath, f"towns_borders.{file_format}"), 'wb')
                        shutil.copyfileobj(file, outfile)
