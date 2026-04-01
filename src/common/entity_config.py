from enum import Enum
from dataclasses import dataclass
from typing import Type, Any, Optional


@dataclass
class ModelConfig:
    """
    Configuration for a system entity.
    Defines all aspects necessary to work with a model generically.
    """
    # Identification
    name: str                          # "material", "supplier", etc.
    display_name: str                  # "Material", "Supplier", etc.
    
    # Model and methods
    model_class: Optional[Type[Any]]   # MaterialModel, SupplierModel, etc.
    get_all_method: str                # "get_all_materials"
    search_by_id_method: str           # "search_by_id"
    search_by_name_method: str         # "search_by_name"
    
    # Field configuration
    id_field_name: str                 # "material_id", "supplier_id", etc.
    name_field_name: str               # "material_name", "supplier_name", etc.
    
    # Table configuration
    column_headers: list[str]          # ["ID", "Name", "Description", "Unit"]
    column_count: int                  # Number of columns
    
    # Extraction indexes (based on model tuple order)
    id_index: int = 0                  # Index of ID in the tuple
    name_index: int = 1                # Index of name in the tuple
    
    # Search configuration
    min_search_length: int = 3         # Minimum characters for name search


class EntityType(Enum):
    """
    Enum that defines the entity types supported by the generic system.
    Each value contains a complete ModelConfig with all necessary configuration.
    """
    
    MATERIAL = ModelConfig(
        name="material",
        display_name="Material",
        model_class=None,  # Will be assigned after imports
        get_all_method="get_all_materials",
        search_by_id_method="search_by_id",
        search_by_name_method="search_by_name",
        id_field_name="material_id",
        name_field_name="material_name",
        column_headers=["id", "material_name", "description", "unit"],
        column_count=4,
        id_index=0,
        name_index=1,
        min_search_length=3,
    )
    
    SUPPLIER = ModelConfig(
        name="supplier",
        display_name="Supplier",
        model_class=None,  # Will be assigned after imports
        get_all_method="get_all_suppliers",
        search_by_id_method="search_by_supplier_id",
        search_by_name_method="search_by_supplier_name",
        id_field_name="supplier_id",
        name_field_name="supplier_name",
        column_headers=["id", "supplier_name", "contact_department", "phone", "email", "address", "notes", "is_active"],
        column_count=8,
        id_index=0,
        name_index=1,
        min_search_length=3,
    )
    
    PRODUCTION_LINE = ModelConfig(
        name="production_line",
        display_name="Production Line",
        model_class=None,  # Will be assigned after imports
        get_all_method="get_all_production_lines",
        search_by_id_method="search_by_id",
        search_by_name_method="search_by_name",
        id_field_name="line_id",
        name_field_name="line_name",
        column_headers=["id", "line_name", "description", "is_active"],
        column_count=4,
        id_index=0,
        name_index=1,
        min_search_length=3,
    )
    
    @classmethod
    def from_string(cls, entity_str: str) -> 'EntityType':
        """
        Converts a string to EntityType.
        
        Args:
            entity_str: String representing the entity type
                       ("material", "supplier", "production_line")
        
        Returns:
            Corresponding EntityType
        
        Raises:
            ValueError: If the string does not correspond to any known entity
        """
        entity_str_lower = entity_str.lower().strip()
        
        for entity in cls:
            if entity.value.name == entity_str_lower:
                return entity
        
        # Try match by enum name
        try:
            return cls[entity_str.upper()]
        except KeyError:
            pass
        
        raise ValueError(
            f"Unknown entity type: '{entity_str}'. "
            f"Valid options: {', '.join([e.value.name for e in cls])}"
        )


# Lazy import to avoid circular dependencies
def _initialize_model_classes():
    """Initializes references to model classes."""
    from src.models.material_model import MaterialModel
    from src.models.supplier_model import SupplierModel
    from src.models.production_line_model import ProductionLineModel
    
    EntityType.MATERIAL.value.model_class = MaterialModel
    EntityType.SUPPLIER.value.model_class = SupplierModel
    EntityType.PRODUCTION_LINE.value.model_class = ProductionLineModel


# Initialize model classes when importing this module
_initialize_model_classes()
