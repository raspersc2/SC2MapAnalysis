from random import randint

from _pytest.python import Metafunc
from hypothesis import given, settings
from hypothesis import strategies as st
from loguru import logger
from sc2.position import Point2

from map_analyzer.MapData import MapData
from map_analyzer.utils import get_map_file_list, mock_map_data
from tests.mocksetup import get_map_datas, random


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


@given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=100))
@settings(max_examples=5, deadline=None, verbosity=3, print_blob=True)
def test_mapdata(n, m):
    map_files = get_map_file_list()
    map_data = mock_map_data(random.choice(map_files))
    # map_data.plot_map()
    logger.info(f"Loaded Map : {map_data.bot.game_info.map_name}, n,m = {n}, {m}")
    # tuples
    points = [(i, j) for i in range(n + 1) for j in range(m + 1)]
    set_points = set(points)
    indices = map_data.points_to_indices(set_points)
    i = randint(0, n)
    j = randint(0, m)
    assert (i, j) in points
    assert (i, j) in set_points
    assert i in indices[0] and j in indices[1]
    new_points = map_data.indices_to_points(indices)
    assert new_points == set_points

    # Point2's
    points = [Point2((i, j)) for i in range(n + 1) for j in range(m + 1)]

    for point in points:
        assert point is not None
    set_points = set(points)
    indices = map_data.points_to_indices(set_points)
    i = randint(0, n)
    j = randint(0, m)
    assert (i, j) in points
    assert (i, j) in set_points
    assert i in indices[0] and j in indices[1]
    new_points = map_data.indices_to_points(indices)
    assert new_points == set_points


class TestSanity:
    """
    Test DocString
    """

    scenarios = [
        (f"Testing {md.bot.game_info.map_name}", {"map_data": md})
        for md in get_map_datas()
    ]

    def test_polygon(self, map_data: MapData) -> None:
        for polygon in map_data.polygons:
            polygon.plot(testing=True)
            assert polygon not in polygon.areas
            assert polygon.width > 0
            assert polygon.area > 0
            assert polygon.is_inside_point(polygon.center)

            extended_pts = polygon.points.union(polygon.outer_perimeter_points)
            assert polygon.points == extended_pts

            for point in extended_pts:
                assert polygon.is_inside_point(point) is True

                # https://github.com/BurnySc2/python-sc2/issues/62
                assert isinstance(point, Point2)
                assert type(point[0] == int)

            for point in polygon.corner_points:
                assert point in polygon.corner_array

    def test_regions(self, map_data: MapData) -> None:
        for region in map_data.regions.values():
            for p in region.points:
                assert region in map_data.where_all(
                    p
                ), f"expected {region}, got {map_data.where_all(p)}, point {p}"
            assert region == map_data.where(region.center)

            # coverage
            region.plot(testing=True)

    def test_ramps(self, map_data: MapData) -> None:
        for ramp in map_data.map_ramps:
            # on some maps the ramp may be hit a region edge
            # and ends up connecting to 3 regions
            # could think about whether this is desirable
            # or if we should select the 2 main regions
            # the ramp is connecting
            assert len(ramp.regions) == 2 or len(ramp.regions) == 3, f"ramp = {ramp}"

    def test_chokes(self, map_data: MapData) -> None:
        for choke in map_data.map_chokes:
            for p in choke.points:
                assert choke in map_data.where_all(p), logger.error(
                    f"<Map : {map_data}, Choke : {choke},"
                    f" where :  {map_data.where(choke.center)} point : {choke.center}>"
                )

    def test_vision_blockers(self, map_data: MapData) -> None:
        all_chokes = map_data.map_chokes
        for vb in map_data.map_vision_blockers:
            assert vb in all_chokes
            for p in vb.points:
                assert vb in map_data.where_all(p), logger.error(
                    f"<Map : {map_data}, Choke : {vb},"
                    f" where_all :  {map_data.where_all(vb.center)}"
                    f" point : {vb.center}>"
                )
