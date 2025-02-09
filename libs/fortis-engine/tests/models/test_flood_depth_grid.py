from fortis.engine.models.flood_depth_grid import FloodDepthGrid
import rasterio

class DummyDataset:
    def __init__(self, fixed_value: float):
        self.fixed_value = fixed_value

    def sample(self, coordinates):
        # For any coordinate, yield a tuple with the fixed value.
        for _ in coordinates:
            yield (self.fixed_value,)

    def close(self):
        pass

def dummy_rasterio_open(path: str):
    # Return a DummyDataset that always returns 3.14 as flood depth
    return DummyDataset(3.14)

def test_get_depth(monkeypatch):
    # Monkeypatch rasterio.open to use our dummy implementation
    monkeypatch.setattr(rasterio, "open", dummy_rasterio_open)
    
    # Create an instance of FloodDepthGrid (the file path is irrelevant)
    with FloodDepthGrid("fake/path/to/raster.tif") as grid:
        # Test for a known point, for instance (10, 20)
        value = grid.get_depth(10.0, 20.0)
        assert isinstance(value, float)
        assert value == 3.14