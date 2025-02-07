import pandas as pd
import geopandas as gpd
from fortis_engine.models.abstract_building_points import AbstractBuildingPoints
from fortis_engine.models.abstract_flood_depth_grid import AbstractFloodDepthGrid

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

      with resources.files("fortis_data.data").joinpath("flDebris.csv").open("r") as debris_file:
            self.debris = pd.read_csv(debris_file)
      with resources.open_text("fortis_data.data", "flRsFnGBS.csv") as restoration_file:
            self.restoration = pd.read_csv(restoration_file)

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
      self.vulnerability_func.collect_damage_percentages()
      
      # Do the loss calculations
      gdf[fields.BldgLoss] = gdf[fields.BldgDmgPct] * gdf[fields.BldgCost]
      gdf[fields.ContentLoss] = gdf[fields.ContDmgPct] * gdf[fields.ContentCost]
      gdf[fields.InventoryLoss] = gdf[fields.InvDmgPct] * gdf[fields.InventoryCost]

      # Debris
      weights = gdf.apply(lambda row: self.lookup_debris_weights(row[fields.FloodDepth], row[fields.OccupancyType]), axis=1)
      # Append the new columns
      gdf = gdf.join(weights)

      # Calculate the debris based on the weights
      gdf[fields.DebrisFinish] = gdf[fields.Area] * gdf['FinishWt'] / 1000   
      gdf[fields.DebrisFoundation] = gdf[fields.Area] * gdf['FoundationWt'] / 1000
      gdf[fields.DebrisStructure] = gdf[fields.Area] * gdf['StructureWt'] / 1000
      gdf[fields.DebrisTotal] = gdf[fields.DebrisFinish] + gdf[fields.DebrisFoundation] + gdf[fields.DebrisStructure]

      # Restoration Time
      restoration = gdf.apply(lambda row: self.lookup_restoration_time(row[fields.FloodDepth], row[fields.OccupancyType]), axis=1)
      gdf = gdf.join(restoration)

    def lookup_debris_weights(self, flood_depth, occupancy, foundation_type):
      """
      Given a flood depth, occupancy, and foundation type, return the weight values
      from debris_df based on matching rules.

      Args:
          flood_depth (float): The flood depth of the building.
          occupancy (str): The occupancy type of the building.
          foundation_type (str): The foundation type (e.g., "S", "F", etc.)

      Returns:
          pd.Series: A series with keys ['FinishWt', 'StructureWt', 'FoundationWt'].
      """
      debris_df = self.debris

      # Determine the found type based on foundation type:
      # For Slab matching, foundation types S or F; all others as Footing.
      found_type = "Slab" if foundation_type in ["S", "F"] else "Footing"
      df = debris_df[(debris_df['SOccup'] == occupancy) & (debris_df['FoundType'] == found_type)]
      
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
    
    def lookup_restoration_time(self, flood_depth, occupancy):
      """
      Given a flood depth, occupancy, and return the weight values
      from restoration_df based on matching rules.

      Args:
          flood_depth (float): The flood depth of the building.
          occupancy (str): The occupancy type of the building.

      Returns:
          pd.Series: A series with keys ['Min_Restor_Days', 'Max_Restor_Days'].
      """
      restoration_df = self.restoration

      df = restoration_df[(restoration_df['SOccup'] == occupancy)]
      
      # Find the matching row(s)
      match = df[(flood_depth >= df['Min_Depth']) & (flood_depth < df['Max_Depth'])]
      if not match.empty:
          # If multiple rows match (for different types like 'Footing' and 'Slab'),
          # you could either choose one or combine them as needed.
          # For this example, we'll take the first match.
          row = match.iloc[0]
          return pd.Series({
              'Min_Restor_Days': row['Min_Restor_Days'],
              'Max_Restor_Days': row['Max_Restor_Days'],
          })
      # Return defaults if no match is found
      return pd.Series({
          'Min_Restor_Days': 0,
          'Max_Restor_Days': 0,
      })