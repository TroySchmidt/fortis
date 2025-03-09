import os
import pytest
import pandas as pd
import geopandas as gpd
from unittest import mock
from shapely.geometry import Point
from fortis.engine.models.nsi_buildings import NsiBuildings


@pytest.fixture
def sample_nsi_data():
    """Create a sample GeoDataFrame that mimics NSI building data."""
    data = {
        'id': ['NSI_1', 'NSI_2', 'NSI_3'],
        'occtype': ['RES1', 'RES3', 'COM1'],
        'bldgtype': ['W1', 'S2L', 'C1L'],
        'stories': [1, 2, 1],
        'sqft': [1500, 3000, 5000],
        'bldgcost': [150000, 300000, 750000],
        'contcost': [75000, 150000, 375000],
        'geometry': [
            Point(0, 0),
            Point(1, 1),
            Point(2, 2)
        ]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def mock_gpkg_file(sample_nsi_data, tmp_path):
    """Create a temporary GPKG file with sample data."""
    gpkg_path = tmp_path / "test_nsi.gpkg"
    sample_nsi_data.to_file(gpkg_path, driver="GPKG")
    return str(gpkg_path)

def test_nsi_buildings_real():
    buildings = NsiBuildings(r"C:\Source\fortis\examples\nsi_2022_15.gpkg")

def test_nsi_buildings_init(mock_gpkg_file):
    """Test NsiBuildings initialization from a GPKG file."""
    buildings = NsiBuildings(mock_gpkg_file)
    
    assert isinstance(buildings.gdf, gpd.GeoDataFrame)
    assert len(buildings.gdf) == 3
    assert 'id' in buildings.gdf.columns
    assert 'occtype' in buildings.gdf.columns
    assert 'sqft' in buildings.gdf.columns
    assert 'geometry' in buildings.gdf.columns


def test_nsi_buildings_properties(mock_gpkg_file):
    """Test NsiBuildings properties."""
    buildings = NsiBuildings(mock_gpkg_file)
    
    assert buildings.count == 3
    assert buildings.crs is not None
    assert buildings.bounds is not None
    assert isinstance(buildings.centroids, gpd.GeoDataFrame)


def test_nsi_buildings_losses(mock_gpkg_file):
    """Test setting and getting loss values."""
    buildings = NsiBuildings(mock_gpkg_file)
    
    # Test setting losses
    test_losses = [100, 200, 300]
    buildings.losses = test_losses
    
    # Check if losses were properly assigned
    assert 'losses' in buildings.gdf.columns
    assert buildings.gdf['losses'].tolist() == test_losses
    
    # Test getting losses
    retrieved_losses = buildings.losses
    assert retrieved_losses.tolist() == test_losses


def test_nsi_buildings_field_mapping(mock_gpkg_file):
    """Test that NSI field mappings are correct."""
    buildings = NsiBuildings(mock_gpkg_file)
    
    # Test field mappings work as expected
    assert buildings.gdf['id'].tolist() == ['NSI_1', 'NSI_2', 'NSI_3']
    assert buildings.gdf['occtype'].tolist() == ['RES1', 'RES3', 'COM1']
    assert buildings.gdf['bldgtype'].tolist() == ['W1', 'S2L', 'C1L']


def test_nsi_buildings_custom_layer(sample_nsi_data, tmp_path):
    """Test loading NSI buildings from a custom layer name."""
    # Create a GPKG with a custom layer name
    gpkg_path = tmp_path / "custom_layer.gpkg"
    sample_nsi_data.to_file(gpkg_path, driver="GPKG", layer="custom_nsi_layer")
    
    # Test loading with the custom layer name
    buildings = NsiBuildings(str(gpkg_path), layer="custom_nsi_layer")
    
    assert isinstance(buildings.gdf, gpd.GeoDataFrame)
    assert len(buildings.gdf) == 3


def test_nsi_buildings_error_handling():
    """Test error handling for invalid file paths."""
    with pytest.raises(Exception):
        NsiBuildings("non_existent_file.gpkg")
