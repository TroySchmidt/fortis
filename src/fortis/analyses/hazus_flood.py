class HazusFloodAnalysis:
    def __init__(self, buildings, vulnerability_func, hazard):
      """
      Initializes a HazusFloodAnalysis object.

      Args:
          buildings (BuildingPoints): BuildingPoints object.
          vulnerability_func (VulnerabilityFunction): VulnerabilityFunction object.
          hazard (Hazard): Hazard object.
      """
      self.buildings = buildings
      self.vulnerability_func = vulnerability_func
      self.hazard = hazard

    def calculate_risk(self):
      """
      Calculates risk for each building.

      Returns:
          pandas.DataFrame or geopandas.GeoDataFrame: Building data with risk metrics.
      """
      # Extract building locations
      self.buildings.data['hazard_intensity'] = self.buildings.data.apply(
          lambda row: self.hazard.get_intensity(row['geometry'].x, row['geometry'].y), axis=1
      )

      # Calculate damage for each building
      self.buildings.data['damage'] = self.buildings.data['hazard_intensity'].apply(
          self.vulnerability_func.calculate_damage
      )

      return self.buildings.data