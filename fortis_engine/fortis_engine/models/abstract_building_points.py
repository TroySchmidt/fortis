import geopandas as gpd
from abc import ABC, abstractmethod

class AbstractBuildingPoints(ABC):
    @property
    @abstractmethod
    def gdf(self) -> gpd.GeoDataFrame:
        pass