from fortis_engine.fortis_engine.models.abstract_building_points import AbstractBuildingPoints
from fortis_engine.fortis_engine.models.abstract_flood_depth_grid import AbstractFloodDepthGrid


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


      # Apply the depth grid to the buildings
      # with on the flood depth grid
      # gdf["flood_depth"] = gdf["geometry"].apply(lambda pt: flood_depth_grid.get_depth(pt))

      # Apply the vulnerability function to the buildings

      # Calculate damage for each building