import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from fortis.engine.models.nsi_points import NSIPoints

def dummy_extract_and_load(self, zip_path: str) -> gpd.GeoDataFrame:
    # Create a dummy GeoDataFrame instead of extracting from a zip.
    data = {
        'id': [1, 2],
        'name': ['Point A', 'Point B'],
        'geometry': [Point(0, 0), Point(1, 1)]
    }
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gdf

def test_gdf_property(monkeypatch):
    # Use monkeypatch to replace _extract_and_load with our dummy version.
    monkeypatch.setattr(NSIPoints, "_extract_and_load", dummy_extract_and_load)
    
    # The zip_path argument is irrelevant because of monkeypatching.
    instance = NSIPoints("fake/path/to/zip.zip")
    
    # Get the GeoDataFrame via the gdf property.
    gdf = instance.gdf
    
    # Validate the dummy GeoDataFrame.
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert "id" in gdf.columns
    assert "name" in gdf.columns
    assert "geometry" in gdf.columns
    assert gdf.crs == "EPSG:4326"
    assert len(gdf) == 2