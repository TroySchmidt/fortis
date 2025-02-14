import pytest
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import rasterio
from unittest.mock import MagicMock
from fortis.engine.models.flood_depth_grid import FloodDepthGrid


class MockRasterDataset():
    """Mock raster dataset that returns predetermined depth values."""
    def __init__(self):
        self.bounds = rasterio.coords.BoundingBox(
            left=-180, bottom=-90, right=180, top=90
        )
        self.nodata = -9999
        self.crs = rasterio.crs.CRS.from_epsg(4326)

        # Create a simple depth grid: depth = x coordinate value
        self._depth_values = {
            (0, 0): 0.0,    # Origin point
            (5, 5): 5.0,    # Positive coordinates
            (-5, -5): 5.0,  # Negative coordinates
            (10, 0): 10.0,  # Longitude variation
            (0, 10): 0.0,   # Latitude variation
        }

    def sample(self, coordinates, indexes=None):
        """Return depth values based on coordinates."""
        for x, y in coordinates:
            # Return the predefined value if it exists, otherwise interpolate
            value = self._depth_values.get((x, y), abs(x))
            yield (value,)

    def close(self):
        pass

@pytest.fixture
def mock_raster(monkeypatch):
    """Fixture to provide a mock raster dataset."""
    def create_mock_raster_dataset():
        ds = MagicMock(spec=rasterio.io.DatasetReader)
        ds.bounds = rasterio.coords.BoundingBox(
            left=-180, bottom=-90, right=180, top=90
        )
        ds.nodata = -9999
        ds.crs = rasterio.crs.CRS.from_epsg(4326)
        ds.__enter__.return_value = ds
        # Create a simple depth grid: depth = x coordinate value
        depth_values = {
            (0, 0): 0.0,    # Origin point
            (5, 5): 5.0,    # Positive coordinates
            (-5, -5): 5.0,  # Negative coordinates
            (10, 0): 10.0,  # Longitude variation
            (0, 10): 0.0,   # Latitude variation
        }
        def sample(coordinates, indexes=None):
            for x, y in coordinates:
                value = depth_values.get((x, y), abs(x))
                yield (value,)
        ds.sample.side_effect = sample
        ds.close.return_value = None
        return ds

    def mock_open(*args, **kwargs):
        return create_mock_raster_dataset()

    monkeypatch.setattr(rasterio, "open", mock_open)
    monkeypatch.setattr(rasterio, "open", mock_open)


def test_get_depth_single_point(mock_raster):
    """Test getting depth for a single point."""
    with FloodDepthGrid("dummy.tif") as grid:
        # Test known points
        assert grid.get_depth(0, 0) == 0.0
        assert grid.get_depth(5, 5) == 5.0
        assert grid.get_depth(10, 0) == 10.0


def test_get_depth_out_of_bounds(mock_raster):
    """Test handling of out-of-bounds coordinates."""
    with FloodDepthGrid("dummy.tif") as grid:
        with pytest.raises(ValueError, match=".*outside raster bounds.*"):
            grid.get_depth(200, 0)  # Beyond bounds


def test_get_depth_vectorized(mock_raster):
    """Test vectorized depth retrieval for multiple points."""
    # Create a GeoSeries with multiple points
    points = gpd.GeoSeries([
        Point(0, 0),   # Should return 0.0
        Point(5, 5),   # Should return 5.0
        Point(10, 0),  # Should return 10.0
    ], crs="EPSG:4326")

    with FloodDepthGrid("dummy.tif") as grid:
        depths = grid.get_depth_vectorized(points)
        
        # Verify results
        assert isinstance(depths, np.ndarray)
        assert len(depths) == len(points)
        np.testing.assert_array_almost_equal(
            depths, 
            np.array([0.0, 5.0, 10.0])
        )


def test_get_depth_vectorized_empty(mock_raster):
    """Test vectorized depth retrieval with empty GeoSeries."""
    empty_points = gpd.GeoSeries([], crs="EPSG:4326")
    
    with FloodDepthGrid("dummy.tif") as grid:
        depths = grid.get_depth_vectorized(empty_points)
        assert isinstance(depths, np.ndarray)
        assert len(depths) == 0


def test_get_depth_vectorized_invalid_input(mock_raster):
    """Test vectorized depth retrieval with invalid input."""
    with FloodDepthGrid("dummy.tif") as grid:
        with pytest.raises(TypeError, match=".*must be a GeoSeries.*"):
            grid.get_depth_vectorized([Point(0, 0)])  # List instead of GeoSeries