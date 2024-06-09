import pandas as pd
from typing import Tuple


def load_table_lat_lon(path_to_excel: str, return_excel=False):
    xls = pd.ExcelFile(path_to_excel)
    lon = pd.read_excel(xls, 'lon', header=None)
    lat = pd.read_excel(xls, 'lat', header=None)
    if return_excel:
        return xls, lat, lon
    return lat, lon
