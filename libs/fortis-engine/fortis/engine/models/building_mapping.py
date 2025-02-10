from typing import Dict
from fortis.engine.models.field_mapping import FieldMapping


class BuildingMapping(FieldMapping["BuildingMapping"]):
    """
    Mapping class for person-related data.

    Default values for internal field names are defined during initialization.
    The properties simply fetch values from the internal mapping dictionary.
    """

    def __init__(self, overrides: Dict[str, str] = None) -> None:
        # Define default internal values.
        defaults = {
            "id": "ID",
            "occupancy_type": "OccupancyType",
            "first_floor_height": "FirstFloorHt",
            "foundation_type": "FoundationType",
            "number_stories": "NumStories",
            "area": "Area",
            "building_cost": "Cost",
            "content_cost": "ContentCostUSD",
            "inventory_cost": "InventoryCostUSD",
            # These can be added if missing below this line
            "flood_depth": "FloodDepth",
            "depth_in_structure": "DepthInStructure",
            "bddf_id": "BDDF_ID",
            "building_damage_percent": "BldgDmgPct",
            "building_loss": "BldgLossUSD",
            "cddf_id": "CDDF_ID",
            "content_damage_percent": "ContDmgPct",
            "content_loss": "ContentLossUSD",
            "iddf_id": "IDDF_ID",
            "inventory_damage_percent": "InvDmgPct",
            "inventory_loss": "InventoryLossUSD",
            "debris_finish": "DebrisFinish",
            "debris_foundation": "DebrisFoundation",
            "debris_structure": "DebrisStructure",
            "debris_total": "DebrisTotal",
        }
        # Initialize the base FieldMapping with defaults and any provided overrides.
        super().__init__(defaults=defaults, overrides=overrides)

    @property
    def id(self) -> str:
        return self.get_value("id")

    @property
    def occupancy_type(self) -> str:
        return self.get_value("occupancy_type")

    @property
    def first_floor_height(self) -> str:
        return self.get_value("first_floor_height")

    @property
    def foundation_type(self) -> str:
        return self.get_value("foundation_type")

    @property
    def number_stories(self) -> str:
        return self.get_value("number_stories")

    @property
    def area(self) -> str:
        return self.get_value("area")

    @property
    def building_cost(self) -> str:
        return self.get_value("building_cost")

    @property
    def content_cost(self) -> str:
        return self.get_value("content_cost")

    @property
    def inventory_cost(self) -> str:
        return self.get_value("inventory_cost")

    @property
    def flood_depth(self) -> str:
        return self.get_value("flood_depth")

    @property
    def depth_in_structure(self) -> str:
        return self.get_value("depth_in_structure")

    @property
    def bddf_id(self) -> str:
        return self.get_value("bddf_id")

    @property
    def building_damage_percent(self) -> str:
        return self.get_value("building_damage_percent")

    @property
    def building_loss(self) -> str:
        return self.get_value("building_loss")

    @property
    def cddf_id(self) -> str:
        return self.get_value("cddf_id")

    @property
    def content_damage_percent(self) -> str:
        return self.get_value("content_damage_percent")

    @property
    def content_loss(self) -> str:
        return self.get_value("content_loss")

    @property
    def iddf_id(self) -> str:
        return self.get_value("iddf_id")

    @property
    def inventory_damage_percent(self) -> str:
        return self.get_value("inventory_damage_percent")

    @property
    def inventory_loss(self) -> str:
        return self.get_value("inventory_loss")

    @property
    def debris_finish(self) -> str:
        return self.get_value("debris_finish")

    @property
    def debris_foundation(self) -> str:
        return self.get_value("debris_foundation")

    @property
    def debris_structure(self) -> str:
        return self.get_value("debris_structure")

    @property
    def debris_total(self) -> str:
        return self.get_value("debris_total")
