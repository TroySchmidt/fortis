from abc import ABC, abstractmethod

class AbstractFloodDepthGrid(ABC):
    @abstractmethod
    def get_depth(self, lon: float, lat: float) -> float:
        """Returns flood depth at a given point; must be implemented by subclasses."""
        pass