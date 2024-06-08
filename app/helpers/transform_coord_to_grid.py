import pandas as pd
from typing import Tuple


def coord_to_grid(
    table_lat: pd.DataFrame, table_lon: pd.DataFrame, 
    lat: float, lon: float, 
    delta: float = 0.05
) -> Tuple[int, int]:
    # mask_lon = (table_lon >= lon - delta)&(table_lon < lon + delta) # TODO если будут адекватные lon
    mask_lon = (table_lon == round(lon))
    mask_lat = (table_lat >= lat - delta)&(table_lat < lat + delta)
    result_mask = mask_lon & mask_lat
    v1 = result_mask.sum(axis=1)
    v2 = result_mask.sum(axis=0)
    v1 = v1[v1>0]
    v2 = v2[v2>0]
    if v1.shape[0] == 0 or v2.shape[0] == 0:
        return
    return (v1.index[0], v2.index[0])


def grid_to_coord(
    table_lat: pd.DataFrame, table_lon: pd.DataFrame,
    grid_lat: int, grid_lon: int
) -> Tuple[float, float]:
    return (table_lat.iloc[grid_lat, 0], table_lon.iloc[0, grid_lon])


if __name__ == "__main__":
    from scripts.load_data_from_local_file import load_table_lat_lon
    lat, lon = load_table_lat_lon('data/IntegrVelocity.xlsx')
    print(coord_to_grid(table_lat=lat, table_lon=lon, lat=73.1, lon=72.7))
