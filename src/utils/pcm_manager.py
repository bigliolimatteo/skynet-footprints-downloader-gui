
import geopandas as gpd
import re
from unidecode import unidecode
import requests
import difflib

gh_prefix = "https://github.com/pcm-dpc"
gh_repo_prefix = "DPC-Aggregati-Strutturali"
gh_path_directory = "https://api.github.com/repos/pcm-dpc/{gh_repo_prefix}-{area_acronym}-{area_pcm_name}/contents/{area_pcm_name}"
gh_path_shpfile = "{gh_prefix}/{gh_repo_prefix}-{area_acronym}-{area_pcm_name}/raw/master/{area_pcm_name}/{region_name}/{province_name}/{town_name}.shp"

area_mapping = {"Nord-ovest": "ITC-NordOvest",
                "Nord-est": "ITH-NordEst",
                "Centro": "ITI-Centro",
                "Sud": "ITF-Sud",
                "Isole": "ITG-Isole"}

def get_town_names_from_url(url):
    response = requests.get(url)
    return [file['name'].split(".")[0] for file in response.json() if file['name'].endswith("shp")]

def get_towns_names_in_province(area_acronym, area_pcm_name, region_name, province_name, town_name):

    regions_url = gh_path_directory.format(gh_prefix=gh_prefix, 
                                            gh_repo_prefix=gh_repo_prefix,
                                            area_acronym=area_acronym,
                                            area_pcm_name=area_pcm_name)
    print(regions_url)
    regions_names = [file['name']for file in requests.get(regions_url).json()]
    preprocessed_region_name = difflib.get_close_matches(region_name, regions_names, n=1)[0]

    provinces_url = f"{regions_url}/{preprocessed_region_name}"
    provinces_names = [file['name']for file in requests.get(provinces_url).json()]
    preprocessed_province_name = difflib.get_close_matches(province_name, provinces_names, n=1)[0]

    towns_url = f"{regions_url}/{preprocessed_region_name}/{preprocessed_province_name}"
    towns_names = get_town_names_from_url(towns_url)
    preprocessed_town_name = difflib.get_close_matches(town_name, towns_names, n=1)[0]

    return preprocessed_region_name, preprocessed_province_name, preprocessed_town_name

def download_town_buildings_shp(area_istat_name, region_name, province_name, town_name):
    area_pcm_name = area_mapping[area_istat_name].split("-")[1]
    area_acronym = area_mapping[area_istat_name].split("-")[0]

    print(region_name)
    print(province_name)
    print(town_name)

    preprocessed_region_name, preprocessed_province_name, preprocessed_town_name = \
        get_towns_names_in_province(area_acronym, area_pcm_name, region_name, province_name, town_name)

    print(region_name, " - ", preprocessed_region_name)
    print(province_name, " - ", preprocessed_province_name)
    print(town_name, " - ", preprocessed_town_name)

    path = gh_path_shpfile.format(gh_prefix=gh_prefix, 
                                    gh_repo_prefix=gh_repo_prefix,
                                    area_acronym=area_acronym,
                                    area_pcm_name=area_pcm_name,
                                    region_name=preprocessed_region_name,
                                    province_name=preprocessed_province_name,
                                    town_name=preprocessed_town_name)

    print(path)
    return gpd.read_file(f"/vsicurl/{path}").to_crs("EPSG:4326")
    