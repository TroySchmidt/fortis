import pytest
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from fortis_engine.analyses.hazus_flood import HazusFloodAnalysis
from fortis_engine.models.abstract_building_points import AbstractBuildingPoints
from fortis_engine.vulnerability.default_flood import DefaultFloodFunction

@pytest.fixture
def vulnerability_func(small_udf_buildings):
    return DefaultFloodFunction(buildings=small_udf_buildings, vulnerability_func=None, flood_type='CV')

@pytest.fixture
def flood_depth_grid():
    class MockFloodDepthGrid:
        def get_depth(self, x, y):
            return 6.0  # Return a fixed intensity value for testing
    return MockFloodDepthGrid()

def test_calculate_losses(small_udf_buildings, vulnerability_func, flood_depth_grid):
    analysis = HazusFloodAnalysis(small_udf_buildings, vulnerability_func, flood_depth_grid)
    result = analysis.calculate_losses()
    
    assert not result.empty
    assert 'hazard_intensity' in result.columns
    assert 'damage' in result.columns
    # Verify that each record has the mocked hazard intensity value.
    assert all(result['hazard_intensity'] == 5.0)
    # Check that damage is calculated as expected from the vulnerability function.
    assert all(result['damage'] == vulnerability_func.calculate_damage(5.0))