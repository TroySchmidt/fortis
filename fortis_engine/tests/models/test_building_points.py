import pytest
import pandas as pd
import geopandas as gpd
from fortis_engine.models.building_points import BuildingPoints

@pytest.fixture
def csv_data(tmp_path):
    data = {
        'longitude': [10.0, 20.0, 30.0],
        'latitude': [40.0, 50.0, 60.0]
    }
    df = pd.DataFrame(data)
    csv_file = tmp_path / "buildings.csv"
    df.to_csv(csv_file, index=False)
    return csv_file

@pytest.fixture
def shapefile_data(tmp_path):
    data = {
        'geometry': gpd.points_from_xy([10.0, 20.0, 30.0], [40.0, 50.0, 60.0])
    }
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    shapefile_path = tmp_path / "buildings.shp"
    gdf.to_file(shapefile_path)
    return shapefile_path

def test_read_csv(csv_data):
    bp = BuildingPoints(data_source=str(csv_data), file_type='csv')
    assert not bp.data.empty
    assert 'geometry' in bp.data.columns

def test_read_shapefile(shapefile_data):
    bp = BuildingPoints(data_source=str(shapefile_data), file_type='shapefile')
    assert not bp.data.empty
    assert 'geometry' in bp.data.columns

def test_read_geojson(tmp_path):
    data = {
        'geometry': gpd.points_from_xy([10.0, 20.0, 30.0], [40.0, 50.0, 60.0])
    }
    gdf = gpd.GeoDataFrame(data, geometry='geometry')
    geojson_path = tmp_path / "buildings.geojson"
    gdf.to_file(geojson_path, driver='GeoJSON')
    
    bp = BuildingPoints(data_source=str(geojson_path), file_type='geojson')
    assert not bp.data.empty
    assert 'geometry' in bp.data.columns

def test_read_fgdb(tmp_path):
    # Create a temporary file geodatabase and add data to it
    fgdb_path = tmp_path / "buildings.gdb"
    gdf = gpd.GeoDataFrame({
        'geometry': gpd.points_from_xy([10.0, 20.0, 30.0], [40.0, 50.0, 60.0])
    })
    gdf.to_file(fgdb_path, driver='FileGDB', layer='buildings')
    
    bp = BuildingPoints(data_source=str(fgdb_path), file_type='fgdb', layer='buildings')
    assert not bp.data.empty
    assert 'geometry' in bp.data.columns