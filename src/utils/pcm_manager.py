
import geopandas as gpd

gh_prefix = "https://github.com/pcm-dpc"
gh_repo_prefix = "DPC-Aggregati-Strutturali"
gh_path = "{gh_prefix}/{gh_repo_prefix}-{area_acronym}-{area_pcm_name}/raw/master/{area_pcm_name}/{region_name}/{province_name}/{town_name}.shp"

area_mapping = {"Nord-ovest": "ITC-NordOvest",
                "Nord-est": "ITH-NordEst",
                "Centro": "ITI-Centro",
                "Sud": "ITF-Sud",
                "Isole": "ITG-Isole"}

def download_town_buildings_shp(area_istat_name, region_name, province_name, town_name):
    area_pcm_name = area_mapping[area_istat_name].split("-")[1]
    area_acronym = area_mapping[area_istat_name].split("-")[0]
    path = gh_path.format(gh_prefix=gh_prefix, 
                        gh_repo_prefix=gh_repo_prefix,
                        area_acronym=area_acronym,
                        area_pcm_name=area_pcm_name,
                        region_name=region_name,
                        province_name=province_name,
                        town_name=town_name)
    return gpd.read_file(f"/vsicurl/{path}").to_crs("EPSG:4326")
    