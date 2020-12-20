import numpy as np
import mapanalyzerext as ext
from typing import Optional, Tuple, Union, List
from sc2.position import Point2, Rect


class CMapChoke:
    main_line: Tuple[Tuple[float, float], Tuple[float, float]]
    lines: List[Tuple[Tuple[int, int], Tuple[int, int]]]
    side1: List[Tuple[int, int]]
    side2: List[Tuple[int, int]]
    pixels: List[Tuple[int, int]]
    min_length: float

    def __init__(self, main_line, lines, side1, side2, pixels, min_length):
        self.main_line = main_line
        self.lines = lines
        self.side1 = side1
        self.side2 = side2
        self.pixels = pixels
        self.min_length = min_length


def astar_path(
        weights: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        smoothing: bool) -> Union[np.ndarray, None]:
    # For the heuristic to be valid, each move must have a positive cost.
    if weights.min(axis=None) <= 0:
        raise ValueError("Minimum cost to move must be above 0, but got %f" % (
            weights.min(axis=None)))
    # Ensure start is within bounds.
    if (start[0] < 0 or start[0] >= weights.shape[0] or
            start[1] < 0 or start[1] >= weights.shape[1]):
        raise ValueError(f"Start of {start} lies outside grid.")
    # Ensure goal is within bounds.
    if (goal[0] < 0 or goal[0] >= weights.shape[0] or
            goal[1] < 0 or goal[1] >= weights.shape[1]):
        raise ValueError(f"Goal of {goal} lies outside grid.")

    height, width = weights.shape
    start_idx = np.ravel_multi_index(start, (height, width))
    goal_idx = np.ravel_multi_index(goal, (height, width))
    path = ext.astar(
        weights.flatten(), height, width, start_idx, goal_idx, smoothing
    )
    return path


class CMapInfo:
    climber_grid: np.ndarray
    overlord_spots: Optional[List[Point2]]
    chokes: List[CMapChoke]

    def __init__(self, walkable_grid: np.ndarray, height_map: np.ndarray, playable_area: Rect):

        # grids are transposed and the c extension atm calls the y axis the x axis and vice versa
        # so switch the playable area limits around
        c_start_y = int(playable_area.x)
        c_end_y = int(playable_area.x + playable_area.width)
        c_start_x = int(playable_area.y)
        c_end_x = int(playable_area.y + playable_area.height)

        self.climber_grid, overlord_data, choke_data = self._get_map_data(walkable_grid, height_map,
                                                                          c_start_y,
                                                                          c_end_y,
                                                                          c_start_x,
                                                                          c_end_x)

        self.overlord_spots = list(map(Point2, overlord_data))
        self.chokes = []
        for c in choke_data:
            self.chokes.append(CMapChoke(c[0], c[1], c[2], c[3], c[4], c[5]))

    @staticmethod
    def _get_map_data(walkable_grid: np.ndarray, height_map: np.ndarray,
                      start_y: int,
                      end_y: int,
                      start_x: int,
                      end_x: int):
        height, width = walkable_grid.shape
        return ext.get_map_data(walkable_grid.flatten(), height_map.flatten(), height, width,
                                start_y, end_y, start_x, end_x)

