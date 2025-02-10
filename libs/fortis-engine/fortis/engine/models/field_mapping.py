from typing import Dict, Any, Generic, TypeVar
import pandas as pd

T = TypeVar("T")

class FieldMapping(Generic[T]):
    """
    Provides field name mapping functionality with generics for improved type checking.

    Defaults are provided via a dictionary at initialization, and an override dictionary
    can be passed to replace these defaults. Additionally, it supports mapping internal field
    names to external column names for DataFrame renaming.
    """
    def __init__(self, defaults: Dict[str, str] = None, overrides: Dict[str, str] = None) -> None:
        # Initialize the internal values with defaults, then apply any overrides.
        self._values: Dict[str, str] = defaults.copy() if defaults else {}
        if overrides:
            self._values.update(overrides)
        # This mapping relates internal property names to external DataFrame column names.
        self._mapping: Dict[str, str] = {}
    
    def map_field(self, property_name: str, external_name: str) -> None:
        """
        Maps an internal property name to an external field name.
        Example: map_field("first_name", "firstName")
        """
        self._mapping[property_name] = external_name
        
    def get_external_name(self, property_name: str) -> str:
        """
        Returns the external field name for a given internal property name.
        If not mapped, returns the property name unchanged.
        """
        return self._mapping.get(property_name, property_name)
    
    def get_mapped_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts a dictionary by replacing internal keys with external names.
        Useful for preparing data to match an external schema.
        """
        return {self.get_external_name(k): v for k, v in data.items()}
    
    def get_value(self, property_name: str) -> str:
        """Retrieves the current value for the given internal property name."""
        return self._values.get(property_name)
    
    def set_value(self, property_name: str, value: str) -> None:
        """Sets the value for the given internal property name."""
        self._values[property_name] = value

    def get_rename_mapping(self) -> Dict[str, str]:
        """
        Produces a dictionary mapping external column names to internal property names.
        This is intended for use with pandas.DataFrame.rename(columns=...).
        """
        # Invert the mapping: external name -> internal name.
        return {external: internal for internal, external in self._mapping.items()}