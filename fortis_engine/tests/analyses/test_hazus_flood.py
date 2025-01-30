import pytest
import pandas as pd
import geopandas as gpd
from fortis_engine.analyses.hazus_flood import HazusFloodAnalysis
from fortis_engine.models.building_points import BuildingPoints
from fortis_engine.vulnerability.default_flood import DefaultFloodFunction
from fortis_engine.models.hazard import Hazard

@pytest.fixture
def buildings():
    data = {
        'longitude': [10.0, 20.0, 30.0],
        'latitude': [40.0, 50.0, 60.0]
    }
    df = pd.DataFrame(data)
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude))
    return BuildingPoints(data_source=gdf)

@pytest.fixture
def vulnerability_func():
    return DefaultFloodFunction()

@pytest.fixture
def hazard():
    class MockHazard:
        def get_intensity(self, x, y):
            return 5.0  # Mock intensity value for testing
    return MockHazard()

def test_calculate_risk(buildings, vulnerability_func, hazard):
    analysis = HazusFloodAnalysis(buildings, vulnerability_func, hazard)
    result = analysis.calculate_risk()
    
    assert not result.empty
    assert 'hazard_intensity' in result.columns
    assert 'damage' in result.columns
    assert all(result['hazard_intensity'] == 5.0)  # Mock intensity value
    assert all(result['damage'] == vulnerability_func.calculate_damage(5.0))