import pandas as pd
import numpy as np
from typing import Tuple


def coord_to_grid(
    table_lat: pd.DataFrame, table_lon: pd.DataFrame, 
    lat: float, lon: float,
    delta_lon: float = 0,
    delta_lat: float = 0.05
) -> Tuple[int, int]:
    # mask_lon = (table_lon >= lon - delta)&(table_lon < lon + delta) # TODO если будут адекватные lon
    mask_lon = (table_lon == round(lon))|(table_lon == (round(lon)+delta_lon))
    mask_lat = (table_lat >= lat - delta_lat)&(table_lat < lat + delta_lat)
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


def search_coord(
        speed_grid: pd.DataFrame, lat: pd.DataFrame, lon: pd.DataFrame, d_points: dict, point_id: int
) -> Tuple[int, int]:
    for i in np.arange(0.1, 1, 0.1):
        grid = coord_to_grid(
            table_lat=lat, table_lon=lon,
            lat=d_points[point_id][0], lon=d_points[point_id][1],
            delta_lon=0, delta_lat=i
        )
        if grid is not None:
            break
    if speed_grid.iloc[grid[0], grid[1]] > 0:
        return grid
    indices = np.where(speed_grid > 0)
    distances = np.sqrt((indices[0] - grid[0]) ** 2 + (indices[1] - grid[1]) ** 2)
    nearest_index = np.argmin(distances)
    x, y = indices[0][nearest_index], indices[1][nearest_index]
    return x, y


if __name__ == "__main__":
    from scripts.load_data_from_local_file import load_table_lat_lon
    lat, lon = load_table_lat_lon('data/IntegrVelocity.xlsx')
    print(coord_to_grid(table_lat=lat, table_lon=lon, lat=73.1, lon=72.7))
