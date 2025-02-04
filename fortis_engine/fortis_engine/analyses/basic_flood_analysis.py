import geopandas as gpd
from fortis_engine.fortis_engine.models.abstract_building_points import AbstractBuildingPoints
from fortis_engine.fortis_engine.models.abstract_flood_depth_grid import AbstractFloodDepthGrid
from fortis_engine.fortis_engine.vulnerability.abstract_vulnerability_function import AbstractVulnerabilityFunction

class BasicFloodAnalysis:
    def __init__(self, buildings: AbstractBuildingPoints, vulnerability_func: AbstractVulnerabilityFunction, depth_grid: AbstractFloodDepthGrid):
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

      Exposure * Hazard * Vulnerability = Loss

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

      # Apply the depth grid to the buildings
      gdf.apply(lambda pt: self.depth_grid.get_depth(pt))

      # Apply the vulnerability function to the buildings
      self.vulnerability_func.apply_damage_percentages(self.buildings)

      # TODO: Update the strings to use FieldNames class object on each of the classes that uses pandas
      # so then we can override them but have a defined contract.
      
      # Compute the loss
      gdf["BldgLossUSD"] = gdf["BldgDmgPct"] * gdf["BldgCost"]
