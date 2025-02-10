import numpy as np
import rasterio
from .abstract_flood_depth_grid import AbstractFloodDepthGrid


class FloodDepthGrid(AbstractFloodDepthGrid):
    def __init__(self, data_source: str):
        """
        Initializes a FloodDepthGrid object.

        Args:
            data_source (str): Path to the raster file.
        """
        self.data_source = data_source
        self.data = rasterio.open(self.data_source)

    def get_depth(self, lon: float, lat: float) -> float:
        """
        Extracts flood depth value at a given location.

        Args:
            lon (float): Longitude.
            lat (float): Latitude.

        Returns:
            float: Flood depth value.
        """
        # Using sample to efficiently extract the value from the raster
        for val in self.data.sample([(lon, lat)]):
            return val[0]
        raise ValueError("Could not extract flood depth at the given point.")

    def get_depth_vectorized(self, geometry) -> np.ndarray:
        """
        Extracts flood depth for multiple locations in a vectorized way.

        Args:
            geometry (GeoSeries): A GeoSeries of Point geometries.

        Returns:
            np.ndarray: Array of flood depth values.
        """
        # Extract (x, y) tuples from the geometry
        coords = [(pt.x, pt.y) for pt in geometry]
        # Sample the raster for each coordinate
        samples = list(self.data.sample(coords))
        # Return the first band value for each sampled point as a NumPy array
        return np.array([sample[0] for sample in samples])

    def close(self):
        """Closes the raster dataset."""
        self.data.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
