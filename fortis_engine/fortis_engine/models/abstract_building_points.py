import geopandas as gpd
from abc import ABC, abstractmethod

from fortis_engine.fortis_engine.models.field_names import FieldNames

class AbstractBuildingPoints(ABC):
    def __init__(self):
        default_fields = {
            "ID": "ID",
            "OccupancyType": "OccupancyType",
            "FirstFloorHt": "FirstFloorHt",
            "NumStories": "NumStories",
            "FloodDepth": "FloodDepth",
            "BldgCost": "Cost",
            "BDDF_ID": "BDDF_ID",
            "BldgDmgPct": "BldgDmgPct",
            "BldgLoss": "BldgLossUSD",
            "ContentCost": "ContentCostUSD",
            "CDDF_ID": "CDDF_ID",
            "ContDmgPct": "ContDmgPct",
            "ContentLoss": "ContentLossUSD",
            "InventoryCost": "InventoryCostUSD",
            "IDDF_ID": "IDDF_ID",
            "InvDmgPct": "InvDmgPct",
            "InventoryLoss": "InventoryLossUSD",
        }
        self.fields = FieldNames(default_fields)

    @property
    @abstractmethod
    def gdf(self) -> gpd.GeoDataFrame:
        pass