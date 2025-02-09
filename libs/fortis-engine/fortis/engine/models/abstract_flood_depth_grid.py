import numpy as np
import geopandas as gpd
from abc import ABC, abstractmethod

class AbstractFloodDepthGrid(ABC):
    @abstractmethod
    def get_depth(self, lon: float, lat: float) -> float:
        """Returns flood depth at a given point; must be implemented by subclasses."""
        pass

    @abstractmethod
    def get_depth_vectorized(self, geometry: gpd.GeoSeries) -> np.ndarray:
        """Returns flood depth for multiple locations in a vectorized way; must be implemented by subclasses."""
        pass