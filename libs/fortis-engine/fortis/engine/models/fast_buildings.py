import os
import pandas as pd
import geopandas as gpd
from fortis.engine.models.abstract_building_points import AbstractBuildingPoints

class FastBuildings(AbstractBuildingPoints):
    def __init__(self, csv_file: str):
        
        # Provide the default overrides for the building mapping
        overrides = {
            "id": "FltyId",
            "occupancy_type": "Occ",
            # All of these below here should be the defaults but if that changes overridding
            "first_floor_height": "FirstFloorHt",
            "foundation_type": "FoundationType",
            "number_stories": "NumStories",
            "area": "Area",
            "building_cost": "Cost",
            "content_cost": "ContentCostUSD",
            "inventory_cost": "InventoryCostUSD",
            # These can be added if missing below this line
            "flood_depth": "FloodDepth",
            "depth_in_structure": "DepthInStructure",
            "bddf_id": "BDDF_ID",
            "building_damage_percent": "BldgDmgPct",
            "building_loss": "BldgLossUSD",
            "cddf_id": "CDDF_ID",
            "content_damage_percent": "ContDmgPct",
            "content_loss": "ContentLossUSD",
            "iddf_id": "IDDF_ID",
            "inventory_damage_percent": "InvDmgPct",
            "inventory_loss": "InventoryLossUSD",
            "debris_finish": "DebrisFinish",
            "debris_foundation": "DebrisFoundation",
            "debris_structure": "DebrisStructure",
            "debris_total": "DebrisTotal",
        }

        super().__init__(overrides)

        # If csv_file does not have a drive letter, assume relative to cwd.
        drive, _ = os.path.splitdrive(csv_file)
        if not drive:
            csv_path = os.path.join(os.getcwd(), csv_file)
        else:
            csv_path = csv_file

        # Load the GeoDataFrame from the CSV file
        df = pd.read_csv(csv_path)
        # Vectorized loading of the geodataframe from x y columns
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude), crs="EPSG:4326"
        )
        self._gdf = gdf

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        return self._gdf