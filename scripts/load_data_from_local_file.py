import pandas as pd
from typing import Tuple, List


def load_table_lat_lon(path_to_excel: str, return_excel=False) -> Tuple:
    xls = pd.ExcelFile(path_to_excel)
    lon = pd.read_excel(xls, 'lon', header=None)
    lat = pd.read_excel(xls, 'lat', header=None)
    if return_excel:
        return xls, lat, lon
    return lat, lon


def get_dates_from_xls(excel: pd.ExcelFile):
    sheet_names = excel.sheet_names
    return pd.to_datetime(sheet_names[2:]), pd.to_datetime(sheet_names[2:]) + pd.to_timedelta("730 D")  # так как в данных 2020 год
