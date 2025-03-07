import os
import pandas as pd
import geopandas as gpd
from fortis.engine.models.abstract_building_points import AbstractBuildingPoints

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

class NsiBuildings(AbstractBuildingPoints):
    def __init__(self, gpkg_file: str, layer_name: str = "nsi"):
        
        # Provide the overrides for the building mapping with custom field names
        overrides = {
            "id": "fd_id",
            "occupancy_type": "occtype",
            "first_floor_height": "found_ht",
            "foundation_type": "foundation_type",
            "number_stories": "num_story",
            "area": "sqft",
            "building_cost": "val_struct",
            "content_cost": "val_cont",
            "inventory_cost": "val_inv",
            # Add other fields as needed
            "flood_depth": "flood_depth",
            "depth_in_structure": "depth_in_structure",
            "bddf_id": "bddf_id",
            "building_damage_percent": "bldg_dmg_pct",
            "building_loss": "bldg_loss",
            "cddf_id": "cddf_id",
            "content_damage_percent": "cont_dmg_pct",
            "content_loss": "content_loss",
            "iddf_id": "iddf_id",
            "inventory_damage_percent": "inv_dmg_pct",
            "inventory_loss": "inv_loss",
            "debris_finish": "debris_finish",
            "debris_foundation": "debris_foundation",
            "debris_structure": "debris_structure",
            "debris_total": "debris_total",
        }

        super().__init__(overrides)

        # If gpkg_file does not have a drive letter, assume relative to cwd.
        drive, _ = os.path.splitdrive(gpkg_file)
        if not drive:
            gpkg_path = os.path.join(os.getcwd(), gpkg_file)
        else:
            gpkg_path = gpkg_file

        # Load the GeoDataFrame from the GeoPackage file
        try:
            self._gdf = gpd.read_file(gpkg_path, layer=layer_name)
            
            # Pre-process the occupancy type field to remove content after dash - vectorized
            if "occtype" in self._gdf.columns:
                # Convert all values to string first
                self._gdf["occtype"] = self._gdf["occtype"].astype(str)
                # Use vectorized string operations to split at first dash
                self._gdf["occtype"] = self._gdf["occtype"].str.split('-', n=1).str[0]
             
            # Pre-process the foundation type field to map numeric values to string codes
            if "found_type" in self._gdf.columns and "foundation_type" not in self._gdf.columns:
                foundation_type_map = {
                    1: "I",  # Pile
                    2: "P",  # Pier
                    3: "W",  # Solid Wall
                    4: "B",  # Basement
                    5: "C",  # Crawl
                    6: "F",  # Fill
                    7: "S",  # Slab
                }
                
                # Using pandas categories can be more memory efficient for large datasets
                self._gdf["foundation_type"] = pd.to_numeric(self._gdf["found_type"], errors='coerce') \
                                               .map(foundation_type_map) \
                                               .astype("category")

        except Exception as e:
            raise ValueError(f"Failed to load GeoPackage: {str(e)}")

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        return self._gdf
