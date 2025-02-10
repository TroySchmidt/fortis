import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from fortis.engine.analyses.hazus_flood import HazusFloodAnalysis
from fortis.engine.models.abstract_building_points import AbstractBuildingPoints
from fortis.engine.vulnerability.default_flood import DefaultFloodFunction

@pytest.fixture
def vulnerability_func(small_udf_buildings):
    return DefaultFloodFunction(buildings=small_udf_buildings, vulnerability_func=None, flood_type='CV')

@pytest.fixture
def flood_depth_grid():
    class MockFloodDepthGrid:
        def get_depth(self, x, y):
            return 6.0  # Return a fixed intensity value for testing
        def get_depth_vectorized(self, geometry):
            return np.full(len(geometry), 6.0)  # Return a fixed intensity value for testing

    return MockFloodDepthGrid()

def test_calculate_losses(small_udf_buildings, vulnerability_func, flood_depth_grid):
    analysis = HazusFloodAnalysis(small_udf_buildings, vulnerability_func, flood_depth_grid)
    analysis.calculate_losses()
    
    result = small_udf_buildings.gdf

    assert not result.empty
    assert small_udf_buildings.fields.building_loss in result.columns
    # Verify that each record has the mocked hazard intensity value.
    assert all(result[small_udf_buildings.fields.flood_depth] > 0.0)
    # Check that damage is calculated as expected from the vulnerability function.
    assert all(result[small_udf_buildings.fields.building_loss] > 1.0)