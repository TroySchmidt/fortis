import pytest
import numpy as np
import geopandas as gpd
from fortis.engine.analyses.basic_flood_analysis import BasicFloodAnalysis
from fortis.engine.vulnerability.abstract_vulnerability_function import AbstractVulnerabilityFunction
from fortis.engine.models.abstract_building_points import AbstractBuildingPoints


class DummyFloodDepthGrid:
    def get_depth(self, pt):
        # For testing, simply return a dummy value (or leave unimplemented if not needed).
        return 6.0

    def get_depth_vectorized(self, geometry):
        """
        Returns an array of constant depth values (6.0) with the same length as the
        provided GeoSeries (geometry).
        """
        return np.full(len(geometry), 6.0)

class DummyVulnerabilityFunction(AbstractVulnerabilityFunction):
    def apply_damage_percentages(self, building_points: AbstractBuildingPoints) -> None:
        gdf: gpd.GeoDataFrame = building_points.gdf
        # For testing, force a constant damage percentage of 0.2 for every building.
        gdf[building_points.fields.BldgDmgPct] = 0.2

# We assume conftest.py already defines small_udf_buildings;
# Here we override or add a BldgCost column.
@pytest.fixture
def building_points(small_udf_buildings):
    gdf = small_udf_buildings.gdf.copy()
    # Set a constant building cost for each row for testing:
    gdf["BldgCost"] = 100_000  
    # Update the underlying GeoDataFrame in our dummy building points.
    small_udf_buildings._gdf = gdf
    return small_udf_buildings

@pytest.fixture
def basic_flood_analysis(building_points):
    vuln = DummyVulnerabilityFunction()
    depth_grid = DummyFloodDepthGrid()
    return BasicFloodAnalysis(buildings=building_points, vulnerability_func=vuln, depth_grid=depth_grid)

def test_calculate_losses(basic_flood_analysis, building_points):
    basic_flood_analysis.calculate_losses()
    gdf = building_points.gdf
    # With DummyVulnerabilityFunction, BldgDmgPct is set to 0.2.
    # With BldgCost = 100000, we expect:
    expected_loss = 0.2 * 100_000
    assert (gdf["BldgLossUSD"] == expected_loss).all()