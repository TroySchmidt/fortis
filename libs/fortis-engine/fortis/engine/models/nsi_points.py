import geopandas as gpd
import zipfile
import tempfile
from .abstract_building_points import AbstractBuildingPoints


class NSIPoints(AbstractBuildingPoints):
    def __init__(self, zip_path: str):
        """
        Initialize NSIPoints with the path to a zipped gpkg file.

        Args:
            zip_path (str): Full path to the zip file containing the gpkg.
        """

        self.zip_path = zip_path
        self._gdf = self._extract_and_load(zip_path)

    def _extract_and_load(self, zip_path: str) -> gpd.GeoDataFrame:
        """
        Extracts the gpkg file from the zip archive and loads it into a GeoDataFrame.

        Args:
            zip_path (str): Full path to the zip file.

        Returns:
            gpd.GeoDataFrame: Loaded geospatial data.
        """
        # Open the zip archive
        with zipfile.ZipFile(zip_path, "r") as z:
            # Look for a .gpkg file in the archive
            gpkg_files = [item for item in z.namelist() if item.endswith(".gpkg")]
            if not gpkg_files:
                raise ValueError("No gpkg file found in the zip archive")
            gpkg_file = gpkg_files[0]
            # Extract the gpkg file to a temporary directory
            temp_dir = tempfile.mkdtemp()
            extracted_path = z.extract(gpkg_file, path=temp_dir)

        # Read the extracted gpkg file into a GeoDataFrame
        return gpd.read_file(extracted_path)

    @property
    def gdf(self) -> gpd.GeoDataFrame:
        """Returns the GeoDataFrame containing the extracted data."""
        return self._gdf
