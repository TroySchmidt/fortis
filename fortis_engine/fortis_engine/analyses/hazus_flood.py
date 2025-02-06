import pandas as pd
import geopandas as gpd
from fortis_engine.fortis_engine.models.abstract_building_points import AbstractBuildingPoints
from fortis_engine.fortis_engine.models.abstract_flood_depth_grid import AbstractFloodDepthGrid

try:
    # Python 3.9+
    import importlib.resources as resources
except ImportError:
    # For earlier versions, install importlib_resources
    import importlib_resources as resources

class HazusFloodAnalysis:
    def __init__(self, buildings: AbstractBuildingPoints, vulnerability_func, depth_grid: AbstractFloodDepthGrid):
      """
      Initializes a HazusFloodAnalysis object.

      Args:
          buildings (BuildingPoints): BuildingPoints object.
          vulnerability_func (VulnerabilityFunction): VulnerabilityFunction object.
          hazard (Hazard): Hazard object.
      """
      self.buildings = buildings
      self.vulnerability_func = vulnerability_func
      self.depth_grid = depth_grid

      with resources.open_text("fortis_data.data", "flDebris.csv") as debris_file:
            self.debris = pd.read_csv(debris_file)

    def calculate_losses(self):
      """
      Calculates risk for each building.

      Returns:
          pandas.DataFrame or geopandas.GeoDataFrame: Building data with risk metrics.
      """
      # Required fields according to FAST
      # Area
      # Building Cost
      # (Content Cost can be computed if not provided)
      # First floor height
      # Foundation Type (according to Hazus but is basically around basement or no)
      # Lat, Lon, Point geometry
      # Number of stories
      # Occupancy class

      gdf: gpd.GeoDataFrame = self.buildings.gdf
      fields = self.buildings.fields

      # Apply the depth grid to the buildings
      gdf[fields.FloodDepth] = self.depth_grid.get_depth_vectorized(gdf.geometry)

      # From the flooded depth based on other attributes determine the depth in structure.
      gdf[fields.DepthInStructure] = gdf[fields.FloodDepth] - gdf[fields.FirstFloorHeight]

      # Apply the vulnerability function to the buildings

      # Do the loss calculations
      gdf[fields.BldgLoss] = gdf[fields.BldgDmgPct] * gdf[fields.BldgCost]
      gdf[fields.ContentLoss] = gdf[fields.ContDmgPct] * gdf[fields.ContentCost]
      gdf[fields.InventoryLoss] = gdf[fields.InvDmgPct] * gdf[fields.InventoryCost]

      # Debris
      weights = gdf.apply(lambda row: self.lookup_debris_weights(row[fields.FloodDepth], row[fields.OccupancyType]), axis=1)
      # Append the new columns
      gdf = gdf.join(weights)

      # Calculate the debris based on the weights
      

      # Restoration Time

    def lookup_debris_weights(self, flood_depth, occupancy):
      # Optionally filter by occupancy (or another key) if needed:
      debris_df = self.debris
      df = debris_df[debris_df['SOccup'] == occupancy]
      # Find the matching row(s)
      match = df[(flood_depth >= df['MinFloodDepth']) & (flood_depth < df['MaxFloodDepth'])]
      if not match.empty:
          # If multiple rows match (for different types like 'Footing' and 'Slab'),
          # you could either choose one or combine them as needed.
          # For this example, we'll take the first match.
          row = match.iloc[0]
          return pd.Series({
              'FinishWt': row['FinishWt'],
              'StructureWt': row['StructureWt'],
              'FoundationWt': row['FoundationWt']
          })
      # Return defaults if no match is found
      return pd.Series({
          'FinishWt': 0,
          'StructureWt': 0,
          'FoundationWt': 0
      })