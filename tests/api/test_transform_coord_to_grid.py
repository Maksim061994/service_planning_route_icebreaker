from app.helpers.transform_coord_to_grid import coord_to_grid, grid_to_coord
from scripts.load_data_from_local_file import load_table_lat_lon


lat, lon = load_table_lat_lon('data/IntegrVelocity.xlsx')


def test_coord_to_grid_and_grid_to_cell():

    result = coord_to_grid(table_lat=lat, table_lon=lon, lat=68.5, lon=73)
    assert result == (59, 78)

    result = coord_to_grid(table_lat=lat, table_lon=lon, lat=73, lon=44)
    assert result == (47, 32)

    result = coord_to_grid(table_lat=lat, table_lon=lon, lat=71.74, lon=184.7)
    assert result == (195, 21)

    result = grid_to_coord(table_lat=lat, table_lon=lon, grid_lat=58, grid_lon=77)
    assert result == (77.0157, 53)

    result = grid_to_coord(table_lat=lat, table_lon=lon, grid_lat=75, grid_lon=50)
    assert result == (80.8018, 43)

    result = grid_to_coord(table_lat=lat, table_lon=lon, grid_lat=48, grid_lon=21)
    assert result == (74.8013, 30)



