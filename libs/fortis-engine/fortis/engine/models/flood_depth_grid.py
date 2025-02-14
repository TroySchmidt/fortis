import numpy as np
import geopandas as gpd
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
        # Check if the point is within the raster bounds.  Important for efficiency and correctness.
        if not (self.data.bounds.left <= lon <= self.data.bounds.right and
                self.data.bounds.bottom <= lat <= self.data.bounds.top):
            raise ValueError(f"Coordinates ({lon}, {lat}) are outside raster bounds.")
        
        # Use sample to efficiently extract the value.
        try:
            for val in self.data.sample([(lon, lat)], indexes=1):  # Specify indexes=1 to get band 1
                # Check for NoData value.  Crucially, use the dataset's nodata value.
                if val[0] == self.data.nodata:
                    return np.nan  # Return NaN for NoData
                else:
                    return float(val[0])  # Convert to float (important if it's a numpy type)
        except rasterio.RasterioIOError as e:
            # Handle cases where the sample might fail (e.g., out of bounds).
            raise ValueError(f"Could not extract flood depth at ({lon}, {lat}): {e}")

    def get_depth_vectorized(self, geometry: gpd.GeoSeries) -> np.ndarray:
        """
        Extracts flood depth for multiple locations in a vectorized way, handling NoData.

        Args:
            geometry (GeoSeries): A GeoSeries of Point geometries (EPSG:4326).

        Returns:
            np.ndarray: Array of flood depth values (float).  Returns np.nan for NoData.

        Raises:
            TypeError: If `geometry` is not a GeoSeries or if elements are not Points.
            ValueError: If any coordinates are outside raster bounds.
            TypeError: If self.data is not a rasterio DatasetReader.
        """

        if not isinstance(self.data, rasterio.DatasetReader):
            raise TypeError("self.data must be a rasterio DatasetReader object.")

        if not isinstance(geometry, gpd.GeoSeries):
            raise TypeError("geometry must be a GeoSeries.")

        #if not all(isinstance(geom, Point) for geom in geometry):
        #    raise TypeError("All geometries in the GeoSeries must be Point objects.")
        # Ensure the GeoSeries has a CRS set
        if geometry.crs is None:
            raise ValueError("GeoSeries must have a CRS set.")
        
        # Reproject geometry IF NECESSARY.  This is the key change.
        if geometry.crs != self.data.crs:
            geometry = geometry.to_crs(self.data.crs)
        
        # Reproject geometry IF NECESSARY.  This is the key change.
        if geometry.crs != self.data.crs:
            geometry = geometry.to_crs(self.data.crs)

        # Check bounds for *all* points efficiently.
        bounds = self.data.bounds
        if not all(bounds.left <= pt.x <= bounds.right and bounds.bottom <= pt.y <= bounds.top for pt in geometry):
            raise ValueError("Some coordinates are outside the raster bounds.")


        # Extract (x, y) tuples from the geometry
        coords = [(pt.x, pt.y) for pt in geometry]

        # Sample the raster for each coordinate, specifying the band index
        try:
            samples = list(self.data.sample(coords, indexes=1))
        except rasterio.RasterioIOError as e:
            raise ValueError(f"Error during raster sampling: {e}")

        # Process the samples, handling NoData values, and convert to float
        result = np.array([float(val[0]) if val[0] != self.data.nodata else np.nan for val in samples])
        return result
    
    def get_depth_vectorized_old(self, geometry) -> np.ndarray:
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
