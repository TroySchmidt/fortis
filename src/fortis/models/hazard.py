class Hazard:
    def __init__(self, data_source):
      """
      Initializes a Hazard object.

      Args:
          data_source (str): Path to the raster file.
      """
      self.data_source = data_source
      self.data = self.read_raster()

    def read_raster(self):
      """
      Reads hazard data from a raster file.

      Returns:
          rasterio.DatasetReader: Raster data.
      """
      try:
          # Use context manager for efficient file handling
          with rasterio.open(self.data_source) as src:
              return src
      except Exception as e:
          raise IOError(f"Error reading raster file: {e}")

    def get_intensity(self, lon, lat):
      """
      Extracts hazard intensity value at a given location.

      Args:
          lon (float): Longitude.
          lat (float): Latitude.

      Returns:
          float: Hazard intensity value.
      """
      row, col = self.data.index(lon, lat)
      return self.data.read(1)