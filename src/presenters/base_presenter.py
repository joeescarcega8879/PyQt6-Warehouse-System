from src.config.logger_config import logger
from src.common.enums import StatusType


class BasePresenter:
    """
    Base presenter class providing common functionality for all presenters.
    
    This class follows the DRY (Don't Repeat Yourself) principle by extracting
    common patterns found across multiple presenters including:
    - Status message handling (_emit_error, _emit_success)
    - Search functionality with ID and name patterns
    - Edit mode state management
    - Form cleanup operations
    - User information loading
    
    Subclasses should implement specific business logic while leveraging
    these common patterns.
    """
    
    def __init__(self, view, status_handler, current_user=None, **kwargs):
        """
        Initialize the base presenter.
        
        Args:
            view: The view instance this presenter controls
            status_handler: Callback function for displaying status messages
            current_user: Current logged-in user (optional for presenters that don't need it)
            **kwargs: Additional attributes assigned dynamically (e.g. main_app)
        """
        self.view = view
        self.status_handler = status_handler
        self.current_user = current_user

        # Assign any extra keyword arguments as instance attributes
        # This allows subclasses to receive extra dependencies (e.g. main_app)
        # without needing to redeclare __init__ just to store them.
        for key, value in kwargs.items():
            setattr(self, key, value)
        
        # Edit mode state management
        self._is_editing = False
        self._current_entity_id: int | None = None
    
    # Status message handlers (most duplicated pattern across all presenters)
    
    def _emit_error(self, message: str) -> None:
        """
        Display an error message to the user.
        
        Args:
            message: Error message to display
        """
        self.status_handler(message, 3000, StatusType.ERROR)
    
    def _emit_success(self, message: str) -> None:
        """
        Display a success message to the user.
        
        Args:
            message: Success message to display
        """
        self.status_handler(message, 3000, StatusType.SUCCESS)
    
    # Search functionality (common pattern with digit detection)
    
    def _handle_search_with_id_and_name(
        self,
        query: str,
        search_by_id_func,
        search_by_name_func,
        load_all_func,
        load_results_func,
        min_name_length: int = 3,
        entity_name: str = "items"
    ) -> None:
        """
        Handle search with automatic ID vs name detection.
        
        This pattern is duplicated across material_presenter, generic_presenter,
        user_presenter, and supplier_presenter. It detects if the query is a
        number (search by ID) or text (search by name).
        
        Args:
            query: Search query string
            search_by_id_func: Function to call for ID search
            search_by_name_func: Function to call for name search
            load_all_func: Function to call when query is empty (reload all)
            load_results_func: Function to call with search results
            min_name_length: Minimum length for name search (default 3)
            entity_name: Name of entity for error messages (default "items")
        """
        query = (query or "").strip()
        
        # Empty query - reload all items
        if not query:
            load_all_func()
            return
        
        # If the query is a number, search by ID first
        if query.isdigit():
            try:
                results = search_by_id_func(int(query))
                load_results_func(results)
            except Exception:
                logger.exception(f"Error searching {entity_name} by id")
                self._emit_error("Unexpected error during search")
            return
        
        # Name search requires minimum length
        if len(query) < min_name_length:
            return
        
        # For longer queries, search by name
        try:
            results = search_by_name_func(query)
            load_results_func(results)
        except Exception:
            logger.exception(f"Error searching {entity_name} by name")
            self._emit_error("Unexpected error during search")
    
    # Edit mode management (common pattern)
    
    def _enter_edit_mode(self, entity_id: int) -> None:
        """
        Enter edit mode for the given entity ID.
        
        Args:
            entity_id: ID of entity being edited
        """
        self._is_editing = True
        self._current_entity_id = entity_id
    
    def _exit_edit_mode(self) -> None:
        """
        Exit edit mode and reset state.
        """
        self._is_editing = False
        self._current_entity_id = None
    
    def _validate_edit_mode_entity_selected(self, entity_name: str = "item") -> bool:
        """
        Validate that an entity is selected when in edit mode.
        
        Args:
            entity_name: Name of entity for error message (default "item")
            
        Returns:
            True if valid, False if not
        """
        if self._current_entity_id is None:
            self._emit_error(f"Please select a valid {entity_name} to edit")
            return False
        return True
    
    # User information loading (common pattern)
    
    def _load_user_information_to_view(self) -> None:
        """
        Load current user information to the view.
        
        Common pattern found in material_presenter, user_presenter, supplier_presenter.
        Requires the view to have a load_user_information() method.
        """
        if not self.current_user:
            return
        
        user_info = {
            "username": self.current_user.username,
            "user_role": self.current_user.user_role,
        }
        
        if hasattr(self.view, "load_user_information"):
            self.view.load_user_information(user_info)
    
    # Form cleanup operations (common pattern)
    
    def _clear_form_and_reset_state(self) -> None:
        """
        Clear the form and reset edit mode state.
        
        Common pattern in _post_save_cleanup methods across presenters.
        Requires the view to have a clear_form() method.
        """
        self._exit_edit_mode()
        
        if hasattr(self.view, "clear_form"):
            self.view.clear_form()
    
    # Validation helpers
    
    @staticmethod
    def _validate_required_field(value: str | None, field_name: str) -> str | None:
        """
        Validate that a required field is not empty.
        
        Args:
            value: Field value to validate
            field_name: Name of field for error message
            
        Returns:
            Error message if invalid, None if valid
        """
        if not (value or "").strip():
            return f"{field_name} is required"
        return None
    
    @staticmethod
    def _validate_required_fields(fields: dict[str, str]) -> str | None:
        """
        Validate multiple required fields at once.
        
        Args:
            fields: Dictionary mapping field values to field names
            
        Returns:
            First error message encountered, or None if all valid
            
        Example:
            error = self._validate_required_fields({
                data.get("name"): "Material name",
                data.get("unit"): "Unit of measure"
            })
        """
        for value, field_name in fields.items():
            error = BasePresenter._validate_required_field(value, field_name)
            if error:
                return error
        return None
