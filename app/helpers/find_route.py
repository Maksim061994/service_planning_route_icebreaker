import networkx as nx
import pandas as pd
from typing import Tuple


def add_queen_edges(G, matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] > 0:
                # Adding horizontal and vertical edges (these are already present in grid_2d_graph)
                # Adding diagonal edges
                for di, dj in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols and matrix[ni][nj] > 0:
                        G.add_edge((i, j), (ni, nj))


def get_route(
        speed_grid: pd.DataFrame,
        start_coords: Tuple[int, int], end_coords: Tuple[int, int]
):
    def get_time(sheet, p):
        if sheet.iloc[p[0], p[1]] > 0:
            return sheet.iloc[p[0], p[1]]
        else:
            return 0

    matrix = speed_grid.values
    G = nx.grid_2d_graph(len(matrix), len(matrix[0]))
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] < 0:
                G.remove_node((i, j))
    add_queen_edges(G, matrix)
    try:
        path = nx.astar_path(G, start_coords, end_coords)
    except nx.NetworkXNoPath:
        # print(f'nx.NetworkXNoPath, {start_coords=}, {end_coords=}')
        return None, 0
    except nx.NodeNotFound:
        # print(f'nx.NodeNotFound, {start_coords=}, {end_coords=}')
        return None, 0

    time_required = sum([get_time(speed_grid, p) for p in path])
    path = [[p[0], p[1], get_time(speed_grid, p)] for p in path]
    return path, time_required