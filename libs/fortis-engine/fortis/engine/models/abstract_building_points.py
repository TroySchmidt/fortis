from typing import Dict
import geopandas as gpd
from abc import ABC, abstractmethod
from fortis.engine.models.building_mapping import BuildingMapping

class AbstractBuildingPoints(ABC):
    def __init__(self, overrides: Dict[str, str] = None):
        self.fields: BuildingMapping = BuildingMapping(overrides)

    @property
    @abstractmethod
    def gdf(self) -> gpd.GeoDataFrame:
        pass
