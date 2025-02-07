import geopandas as gpd
from abc import ABC, abstractmethod

from fortis_engine.models.field_names import FieldNames

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
        default_fields = {
            # These first fields are required on the input data
            "ID": "ID",
            "OccupancyType": "OccupancyType",
            "FirstFloorHt": "FirstFloorHt",
            "FoundationType": "FoundationType",
            "NumStories": "NumStories",
            "Area": "Area",
            "BldgCost": "Cost",
            "ContentCost": "ContentCostUSD",
            "InventoryCost": "InventoryCostUSD",
            # These can be added if missing below this line
            "FloodDepth": "FloodDepth",
            "BDDF_ID": "BDDF_ID", 
            "BldgDmgPct": "BldgDmgPct",
            "BldgLoss": "BldgLossUSD",
            "CDDF_ID": "CDDF_ID",
            "ContDmgPct": "ContDmgPct",
            "ContentLoss": "ContentLossUSD",
            "IDDF_ID": "IDDF_ID",
            "InvDmgPct": "InvDmgPct",
            "InventoryLoss": "InventoryLossUSD",
            "DebrisFinish": "DebrisFinish",
            "DebrisFoundatioin": "DebrisFoundation",
            "DebrisStructure": "DebrisStructure",
            "DebrisTotal": "DebrisTotal",
        }
        self.fields = FieldNames(default_fields)

    @property
    @abstractmethod
    def gdf(self) -> gpd.GeoDataFrame:
        pass