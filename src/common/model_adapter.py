from typing import Any
from src.config.logger_config import logger
from src.common.entity_config import ModelConfig


class ModelAdapter:
    """
    Adapter that normalizes differences between different system models.
    
    Each model may have different method names and different return types.
    This class provides a unified interface to interact with any model.
    
    Attributes:
        config: Model configuration (ModelConfig)
        model: Model class (MaterialModel, SupplierModel, etc.)
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initializes the adapter with a model configuration.
        
        Args:
            config: ModelConfig with the model configuration
        
        Raises:
            ValueError: If model_class is not defined in the configuration
        """
        if config.model_class is None:
            raise ValueError(f"Model class not initialized for entity: {config.name}")
        
        self.config = config
        self.model = config.model_class
    
    def get_all(self) -> list[tuple]:
        """
        Gets all records from the model normalizing the return type.
        
        Handles different cases:
        - Models that return list[tuple] directly
        - Models that return tuple[list, error] (e.g. UserModel)
        
        Returns:
            List of tuples with the data, or empty list if error
        """
        try:
            method = getattr(self.model, self.config.get_all_method)
            result = method()
            
            # Normalize different return types
            if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], list):
                # UserModel case: (list, error)
                data, error = result
                if error:
                    logger.warning(f"Warning getting all {self.config.name}: {error}")
                return data
            
            # Normal case: list[tuple]
            return result if isinstance(result, list) else []
            
        except AttributeError:
            logger.error(f"Method '{self.config.get_all_method}' not found in {self.model.__name__}")
            return []
        except Exception as e:
            logger.exception(f"Error calling get_all for {self.config.name}")
            return []
    
    def search_by_id(self, entity_id: int) -> list[tuple]:
        """
        Search by ID normalizing the return type.
        
        Handles different cases:
        - Models that return list[tuple]
        - Models that return tuple | None (e.g. SupplierReceiptModel)
        - Models that return list[tuple] | None
        
        Args:
            entity_id: ID of the record to search for
        
        Returns:
            List of tuples with found data, or empty list if no results
        """
        try:
            method = getattr(self.model, self.config.search_by_id_method)
            result = method(entity_id)
            
            # Normalize different return types
            if result is None:
                return []
            
            # If it returns a single tuple instead of a list
            # Check if it's a tuple and not a list of tuples
            if isinstance(result, tuple) and len(result) > 0:
                # If the first element is a number or string, it's a data tuple
                if not isinstance(result[0], (tuple, list)):
                    return [result]
            
            # Normal case: list[tuple]
            return result if isinstance(result, list) else []
            
        except AttributeError:
            logger.error(f"Method '{self.config.search_by_id_method}' not found in {self.model.__name__}")
            return []
        except Exception as e:
            logger.exception(f"Error calling search_by_id for {self.config.name}")
            return []
    
    def search_by_name(self, name: str) -> list[tuple]:
        """
        Search by name normalizing the return type.
        
        Handles different cases:
        - Models that return list[tuple]
        - Models that return list[tuple] | None
        
        Args:
            name: Name or part of the name to search for
        
        Returns:
            List of tuples with found data, or empty list if no results
        """
        try:
            method = getattr(self.model, self.config.search_by_name_method)
            result = method(name)
            
            # Normalize different return types
            if result is None:
                return []
            
            # Normal case: list[tuple]
            return result if isinstance(result, list) else []
            
        except AttributeError:
            logger.error(f"Method '{self.config.search_by_name_method}' not found in {self.model.__name__}")
            return []
        except Exception as e:
            logger.exception(f"Error calling search_by_name for {self.config.name}")
            return []
