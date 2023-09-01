import os

import numpy as np
from sc2.position import Point2, Rect

from MapAnalyzer.cext import CMapInfo, astar_path, astar_path_with_nyduses


def load_pathing_grid(file_name):
    file = open(file_name, "r")
    lines = file.readlines()

    h = len(lines)
    w = len(lines[0]) - 1

    res = np.zeros((h, w))
    y = 0
    for line in lines:
        x = 0
        for char in line:
            if char == "\n":
                continue
            num = int(char)
            if num == 1:
                res[y, x] = 1
            x += 1
        y += 1
    file.close()

    return res.astype(np.uint8)


def test_c_extension():
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, "pathing_grid.txt")
    walkable_grid = load_pathing_grid(abs_file_path)

    pathing_grid = np.where(walkable_grid == 0, np.inf, walkable_grid).astype(
        np.float32
    )
    path = astar_path(pathing_grid, (3, 3), (33, 38), False, False)
    assert path is not None and path.shape[0] == 56

    influenced_grid = pathing_grid.copy()
    influenced_grid[21:28, 5:20] = 100
    path2 = astar_path(influenced_grid, (3, 3), (33, 38), False, False)

    assert path2 is not None and path2.shape[0] == 59

    paths_no_nydus = astar_path_with_nyduses(
        influenced_grid, (3, 3), (33, 38), [], False, False
    )

    assert paths_no_nydus is not None and paths_no_nydus[0].shape[0] == 59

    nydus_positions = [Point2((6.5, 6.5)), Point2((29.5, 34.5))]

    influenced_grid[5:8, 5:8] = np.inf
    influenced_grid[28:31, 33:36] = np.inf

    paths_nydus = astar_path_with_nyduses(
        influenced_grid, (3, 3), (33, 38), nydus_positions, False, False
    )

    assert (
        paths_nydus is not None
        and len(paths_nydus) == 2
        and len(paths_nydus[0]) + len(paths_nydus[1]) == 7
    )

    height_map = np.where(walkable_grid == 0, 24, 8).astype(np.uint8)

    playable_area = Rect([1, 1, 38, 38])
    map_info = CMapInfo(walkable_grid, height_map, playable_area, "CExtensionTest")
    assert len(map_info.overlord_spots) == 2
    assert len(map_info.chokes) == 5

    # testing that the main line actually exists, was a previous bug
    for choke in map_info.chokes:
        assert choke.main_line[0] != choke.main_line[1]
