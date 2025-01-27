import pandas as pd
import geopandas as gpd
import fiona

class BuildingPoints:
    def __init__(self, data_source, file_type=None, **kwargs):
        """
        Initializes a BuildingPoints object.

        Args:
            data_source (str): Path to the file or URL of the data source.
            file_type (str, optional): Type of the file ('csv', 'shapefile', 'geojson', 'fgdb'). 
                                        Inferred from data_source if not provided.
            **kwargs: Additional keyword arguments for specific file reading functions.
        """
        self.data_source = data_source
        
        if file_type is None:
            if data_source.endswith('.csv'):
                file_type = 'csv'
            elif data_source.endswith('.shp'):
                file_type = 'shapefile'
            elif data_source.endswith('.geojson'):
                file_type = 'geojson'
            elif data_source.endswith('.gdb'):
                file_type = 'fgdb'
            else:
                raise ValueError("Could not infer file type from data_source. Please specify file_type.")
        
        self.file_type = file_type
        self.data = self.read_data(**kwargs)

    def read_data(self, **kwargs):
        """
        Reads building data from the specified source.

        Args:
            **kwargs: Additional keyword arguments for specific file reading functions.

        Returns:
            pandas.DataFrame or geopandas.GeoDataFrame: Building data.
        """
        if self.file_type == 'csv':
            return self.read_csv(**kwargs)
        elif self.file_type == 'shapefile':
            return self.read_shapefile(**kwargs)
        elif self.file_type == 'geojson':
            return self.read_geojson(**kwargs)
        elif self.file_type == 'fgdb':
            return self.read_fgdb(**kwargs)
        else:
            raise ValueError("Unsupported file type.")

    def read_csv(self, **kwargs):
        """
        Reads building data from a CSV file.

        Args:
            **kwargs: Additional keyword arguments for pandas.read_csv().

        Returns:
            pandas.DataFrame: Building data.
        """
        try:
            # Use 'with' statement for proper file handling
            with open(self.data_source, 'r') as file:
                df = pd.read_csv(file, **kwargs)
            # Assuming latitude and longitude columns exist, create geometry
            df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
            return df
        except Exception as e:
            raise IOError(f"Error reading CSV file: {e}")

    def read_shapefile(self, **kwargs):
        """
        Reads building data from a shapefile.

        Args:
            **kwargs: Additional keyword arguments for geopandas.read_file().

        Returns:
            geopandas.GeoDataFrame: Building data.
        """
        try:
            return gpd.read_file(self.data_source, **kwargs)
        except Exception as e:
            raise IOError(f"Error reading shapefile: {e}")

    def read_geojson(self, **kwargs):
        """
        Reads building data from a GeoJSON file.

        Args:
            **kwargs: Additional keyword arguments for geopandas.read_file().

        Returns:
            geopandas.GeoDataFrame: Building data.
        """
        try:
            return gpd.read_file(self.data_source, **kwargs)
        except Exception as e:
            raise IOError(f"Error reading GeoJSON file: {e}")

    def read_fgdb(self, **kwargs):
        """
        Reads building data from a file geodatabase.

        Args:
            **kwargs: Additional keyword arguments for geopandas.read_file().

        Returns:
            geopandas.GeoDataFrame: Building data.
        """
        try:
            return gpd.read_file(self.data_source, driver='FileGDB', **kwargs)
        except Exception as e:
            raise IOError(f"Error reading file geodatabase: {e}")