import os
import pytest
import numpy as np
from fortis.engine.analyses.hazus_flood import HazusFloodAnalysis
from fortis.engine.models.fast_buildings import FastBuildings
from fortis.engine.models.flood_depth_grid import FloodDepthGrid
from fortis.engine.vulnerability.default_flood import DefaultFloodFunction


@pytest.fixture
def vulnerability_func(small_udf_buildings):
    return DefaultFloodFunction(
        buildings=small_udf_buildings, flood_type="CV"
    )


@pytest.fixture
def flood_depth_grid():
    class MockFloodDepthGrid:
        def get_depth(self, x, y):
            return 6.0  # Return a fixed intensity value for testing

        def get_depth_vectorized(self, geometry):
            return np.full(
                len(geometry), 6.0
            )  # Return a fixed intensity value for testing

    return MockFloodDepthGrid()


def test_calculate_losses(small_udf_buildings, vulnerability_func, flood_depth_grid):
    analysis = HazusFloodAnalysis(
        small_udf_buildings, vulnerability_func, flood_depth_grid
    )
    analysis.calculate_losses()

    result = small_udf_buildings.gdf

    assert not result.empty
    assert small_udf_buildings.fields.building_loss in result.columns
    # Verify that each record has the mocked hazard intensity value.
    assert all(result[small_udf_buildings.fields.flood_depth] > 0.0)
    # Check that damage is calculated as expected from the vulnerability function.
    assert all(result[small_udf_buildings.fields.building_loss] > 1.0)

@pytest.mark.skipif(
    not os.path.exists(os.path.join(os.path.dirname(__file__), '../../../../examples/HI_Honolulu_UDF_sample.csv')),
    reason="Example CSV file not found."
)
def test_calculate_losses_with_example_files():
    # Construct paths relative to the repository root.
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../examples'))
    csv_file = os.path.join(base_dir, "HI_Honolulu_UDF_sample.csv")
    tif_file = os.path.join(base_dir, "Oahu_10_withReef.tif")
    
    # Load buildings from the CSV file (FastBuildings handles relative vs absolute paths)
    buildings = FastBuildings(csv_file)
    buildings._gdf = buildings.gdf.head(10)

    # Create a FloodDepthGrid from the depth grid TIFF file.
    depth_grid = FloodDepthGrid(tif_file)
    
    # Use the DefaultFloodFunction with, for example, flood type "R"
    flood_function = DefaultFloodFunction(buildings, flood_type="R")
    
    # Create and run the Hazus flood analysis.
    analyzer = HazusFloodAnalysis(
        buildings=buildings,
        vulnerability_func=flood_function,
        depth_grid=depth_grid,
    )
    analyzer.calculate_losses()
    
    # Verify that the analysis was executed: the resulting GeoDataFrame is not empty,
    # and expected columns (e.g., flood_depth and building_loss) exist.
    result = buildings.gdf
    assert not result.empty
    assert buildings.fields.flood_depth in result.columns
    assert buildings.fields.building_loss in result.columns