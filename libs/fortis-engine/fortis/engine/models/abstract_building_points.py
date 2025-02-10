import geopandas as gpd
from abc import ABC, abstractmethod
from fortis.engine.models.building_mapping import BuildingMapping

""" 
Foundation Types:
C: Crawl (5)
B: Basement (4)
S: Slab (7)
P: Pier (2)
I: Pile (1)
F: Fill (6)
W: Solid Wall (3)
"""


class AbstractBuildingPoints(ABC):
    def __init__(self):
        self.fields = BuildingMapping()

    @property
    @abstractmethod
    def gdf(self) -> gpd.GeoDataFrame:
        pass
