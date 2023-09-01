import os

import numpy as np
from _pytest.logging import LogCaptureFixture
from _pytest.python import Metafunc
from sc2.position import Point2

from MapAnalyzer import Region
from MapAnalyzer.destructibles import (
    destructable_2x2,
    destructable_2x4,
    destructable_2x6,
    destructable_4x2,
    destructable_4x4,
    destructable_4x12,
    destructable_6x2,
    destructable_6x6,
    destructable_12x4,
    destructable_BLUR,
    destructable_ULBR,
)
from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import get_map_file_list, get_map_files_folder, mock_map_data
from tests.mocksetup import get_map_datas, get_random_point, logger

logger = logger


# From
# https://docs.pytest.org/en/latest/example/parametrize.html#a-quick-port-of-testscenarios
def pytest_generate_tests(metafunc: Metafunc) -> None:
    # noinspection PyGlobalUndefined
    global argnames
    idlist = []
    argvalues = []
    if metafunc.cls is not None:
        for scenario in metafunc.cls.scenarios:
            idlist.append(scenario[0])
            items = scenario[1].items()
            argnames = [x[0] for x in items]
            argvalues.append(([x[1] for x in items]))
        metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


def test_destructable_types() -> None:
    map_list = get_map_file_list()
    dest_types = set()
    for map in map_list:
        map_data = mock_map_data(map)
        for dest in map_data.bot.destructables:
            dest_types.add((dest.type_id, dest.name))

    rock_types = set()
    rock_types.update(destructable_ULBR)
    rock_types.update(destructable_BLUR)
    rock_types.update(destructable_6x2)
    rock_types.update(destructable_4x4)
    rock_types.update(destructable_2x4)
    rock_types.update(destructable_2x2)
    rock_types.update(destructable_2x6)
    rock_types.update(destructable_4x2)
    rock_types.update(destructable_4x12)
    rock_types.update(destructable_6x6)
    rock_types.update(destructable_12x4)

    for dest in dest_types:
        handled = False
        type_id = dest[0]
        name = dest[1].lower()
        if "mineralfield450" in name:
            handled = True
        elif "unbuildable" in name:
            handled = True
        elif "acceleration" in name:
            handled = True
        elif "inhibitor" in name:
            handled = True
        elif "dog" in name:
            handled = True
        elif "cleaningbot" in name:
            handled = True
        elif type_id in rock_types:
            handled = True

        assert handled, f"Destructable {type_id} with name {name} is not handled"


def test_climber_grid() -> None:
    """assert that we can path through climb cells with climber grid,
    but not with normal grid"""
    path = os.path.join(get_map_files_folder(), "GoldenWallLE.xz")

    map_data = mock_map_data(path)
    start = (150, 95)
    goal = (110, 40)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is None
    grid = map_data.get_climber_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is None


def test_minerals_walls() -> None:
    # attempting to path through mineral walls in goldenwall should fail
    path = os.path.join(get_map_files_folder(), "GoldenWallLE.xz")
    # logger.info(path)
    map_data = mock_map_data(path)
    start = (110, 95)
    goal = (110, 40)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is None
    # also test climber grid for nonpathables
    grid = map_data.get_climber_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is None

    # remove the mineral wall that is blocking pathing from
    # the left player's base to the bottom side of the map
    map_data.bot.destructables = map_data.bot.destructables.filter(
        lambda x: x.distance_to((46, 41)) > 5
    )
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is not None

    # attempting to path through tight pathways near destructables should work
    path = os.path.join(get_map_files_folder(), "AbyssalReefLE.xz")
    map_data = mock_map_data(path)
    start = (130, 25)
    goal = (125, 47)
    grid = map_data.get_pyastar_grid()
    path = map_data.pathfind(start=start, goal=goal, grid=grid)
    assert path is not None


class TestPathing:
    """
    Test DocString
    """

    scenarios = [
        (f"Testing {md.bot.game_info.map_name}", {"map_data": md})
        for md in get_map_datas()
    ]

    def test_region_connectivity(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        region = map_data.where_all(base.position_tuple)[0]
        destination = map_data.where_all(
            map_data.bot.enemy_start_locations[0].position
        )[0]
        all_possible_paths = map_data.region_connectivity_all_paths(
            start_region=region, goal_region=destination
        )
        for p in all_possible_paths:
            assert destination in p, f"destination = {destination}"

        bad_request = map_data.region_connectivity_all_paths(
            start_region=region, goal_region=destination, not_through=[destination]
        )
        assert bad_request == []

    def test_handle_out_of_bounds_values(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        assert isinstance(reg_start, Region), (
            f"reg_start = {reg_start},  "
            f"base = {base}, position_tuple = {base.position_tuple}"
        )
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = reg_start.center
        p1 = reg_end.center
        pts = []
        r = 10
        for i in range(50):
            pts.append(get_random_point(-500, -250, -500, -250))

        arr = map_data.get_pyastar_grid()
        for p in pts:
            arr = map_data.add_cost(p, r, arr)
        path = map_data.pathfind(p0, p1, grid=arr)
        assert path is not None, f"path = {path}"

    def test_handle_illegal_weights(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        assert isinstance(reg_start, Region), (
            f"reg_start = {reg_start},  base = {base},"
            f" position_tuple = {base.position_tuple}"
        )
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = reg_start.center
        p1 = reg_end.center
        pts = []
        r = 10
        for i in range(10):
            pts.append(get_random_point(20, 180, 20, 180))

        arr = map_data.get_pyastar_grid()
        for p in pts:
            arr = map_data.add_cost(p, r, arr, weight=-100)
        path = map_data.pathfind(p0, p1, grid=arr)
        assert path is not None, f"path = {path}"

    def test_find_lowest_cost_points(self, map_data: MapData) -> None:
        cr = 7
        safe_query_radius = 14
        expected_max_distance = 2 * safe_query_radius

        influence_grid = map_data.get_air_vs_ground_grid()
        cost_point = (50, 130)
        influence_grid = map_data.add_cost(
            position=cost_point, radius=cr, grid=influence_grid
        )
        safe_points = map_data.find_lowest_cost_points(
            from_pos=cost_point, radius=safe_query_radius, grid=influence_grid
        )
        assert (
            safe_points[0][0],
            np.integer,
        ), f"safe_points[0][0] = {safe_points[0][0]}, type {type(safe_points[0][0])}"
        assert isinstance(
            safe_points[0][1], np.integer
        ), f"safe_points[0][1] = {safe_points[0][1]}, type {type(safe_points[0][1])}"
        cost = influence_grid[safe_points[0]]
        for p in safe_points:
            assert influence_grid[p] == cost, (
                f"grid type = air_vs_ground_grid, p = {p}, "
                f"influence_grid[p] = {influence_grid[p]}, expected cost = {cost}"
            )
            assert map_data.distance(cost_point, p) < expected_max_distance

        influence_grid = map_data.get_clean_air_grid()
        cost_point = (50, 130)
        influence_grid = map_data.add_cost(
            position=cost_point, radius=cr, grid=influence_grid
        )
        safe_points = map_data.find_lowest_cost_points(
            from_pos=cost_point, radius=safe_query_radius, grid=influence_grid
        )
        cost = influence_grid[safe_points[0]]
        for p in safe_points:
            assert influence_grid[p] == cost, (
                f"grid type = clean_air_grid, p = {p}, "
                f"influence_grid[p] = {influence_grid[p]}, expected cost = {cost}"
            )
            assert map_data.distance(cost_point, p) < expected_max_distance

        influence_grid = map_data.get_pyastar_grid()
        cost_point = (50, 130)
        influence_grid = map_data.add_cost(
            position=cost_point, radius=cr, grid=influence_grid
        )
        safe_points = map_data.find_lowest_cost_points(
            from_pos=cost_point, radius=safe_query_radius, grid=influence_grid
        )
        cost = influence_grid[safe_points[0]]
        for p in safe_points:
            assert influence_grid[p] == cost, (
                f"grid type = pyastar_grid, p = {p}, "
                f"influence_grid[p] = {influence_grid[p]}, expected cost = {cost}"
            )
            assert map_data.distance(cost_point, p) < expected_max_distance

        influence_grid = map_data.get_climber_grid()
        cost_point = (50, 130)
        influence_grid = map_data.add_cost(
            position=cost_point, radius=cr, grid=influence_grid
        )
        safe_points = map_data.find_lowest_cost_points(
            from_pos=cost_point, radius=safe_query_radius, grid=influence_grid
        )
        cost = influence_grid[safe_points[0]]
        for p in safe_points:
            assert influence_grid[p] == cost, (
                f"grid type = climber_grid, p = {p}, "
                f"influence_grid[p] = {influence_grid[p]}, expected cost = {cost}"
            )
            assert map_data.distance(cost_point, p) < expected_max_distance

    def test_clean_air_grid_smoothing(self, map_data: MapData) -> None:
        default_weight = 2
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = Point2(reg_start.center)
        p1 = Point2(reg_end.center)
        grid = map_data.get_clean_air_grid(default_weight=default_weight)
        cost_points = [(87, 76), (108, 64), (97, 53)]
        cost_points = list(map(Point2, cost_points))
        for cost_point in cost_points:
            grid = map_data.add_cost(position=cost_point, radius=7, grid=grid)
        path = map_data.pathfind(start=p0, goal=p1, grid=grid, smoothing=True)
        assert len(path) < 50

    def test_clean_air_grid_no_smoothing(self, map_data: MapData) -> None:
        """
        non diagonal path should be longer,  but still below 250
        """
        default_weight = 2
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = Point2(reg_start.center)
        p1 = Point2(reg_end.center)
        grid = map_data.get_clean_air_grid(default_weight=default_weight)
        cost_points = [(87, 76), (108, 64), (97, 53)]
        cost_points = list(map(Point2, cost_points))
        for cost_point in cost_points:
            grid = map_data.add_cost(position=cost_point, radius=7, grid=grid)
        path = map_data.pathfind(start=p0, goal=p1, grid=grid, smoothing=False)
        assert len(path) < 250

    def test_air_vs_ground(self, map_data: MapData) -> None:
        default_weight = 99
        grid = map_data.get_air_vs_ground_grid(default_weight=default_weight)
        ramps = map_data.map_ramps
        path_array = map_data.pather.default_grid
        for ramp in ramps:
            for point in ramp.points:
                if path_array[point.x][point.y] == 1:
                    assert grid[point.x][point.y] == default_weight, f"point {point}"

    def test_sensitivity(self, map_data: MapData) -> None:
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = reg_start.center
        p1 = reg_end.center
        arr = map_data.get_pyastar_grid()
        path_pure = map_data.pathfind(p0, p1, grid=arr)
        path_sensitive_5 = map_data.pathfind(p0, p1, grid=arr, sensitivity=5)
        path_sensitive_1 = map_data.pathfind(p0, p1, grid=arr, sensitivity=1)
        assert len(path_sensitive_5) < len(path_pure)
        assert (p in path_pure for p in path_sensitive_5)
        assert path_sensitive_1 == path_pure

    def test_pathing_influence(
        self, map_data: MapData, caplog: LogCaptureFixture
    ) -> None:
        logger.info(map_data)
        base = map_data.bot.townhalls[0]
        reg_start = map_data.where_all(base.position_tuple)[0]
        reg_end = map_data.where_all(map_data.bot.enemy_start_locations[0].position)[0]
        p0 = reg_start.center
        p1 = reg_end.center
        pts = []
        r = 10
        for i in range(50):
            pts.append(get_random_point(0, 200, 0, 200))

        arr = map_data.get_pyastar_grid()
        for p in pts:
            arr = map_data.add_cost(p, r, arr)
        path = map_data.pathfind(p0, p1, grid=arr)
        assert path is not None
