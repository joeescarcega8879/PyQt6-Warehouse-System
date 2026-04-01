"""
Base Model class providing common patterns for all models.
Implements DRY principle and provides consistent error handling.
"""

import logging
from typing import Any, Callable, TypeVar
from src.database.query_helper import QueryHelper, DatabaseError
from src.common.error_messages import ErrorMessages

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseModel:
    """
    Base class for all models providing common functionality:
    - Standardized error handling
    - Common CRUD operation patterns
    - Search functionality
    - Logging and error masking
    """

    @staticmethod
    def _execute_with_error_handling(
        operation: Callable[[], T],
        context: str,
        default_return: T,
        entity_name: str = "entity"
    ) -> tuple[T, str | None]:
        """
        Execute a database operation with standardized error handling.
        
        Args:
            operation: Function that performs the database operation
            context: Description of the operation for logging
            default_return: Value to return on error
            entity_name: Name of the entity for error messages
            
        Returns:
            tuple[T, str | None]: (result, error_message)
                - result: Operation result if successful, default_return if failed
                - error_message: None if successful, error message if failed
        """
        try:
            result = operation()
            return result, None
            
        except DatabaseError as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return default_return, error_msg
            
        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return default_return, error_msg

    @staticmethod
    def _execute_query_safe(
        operation: Callable[[], Any],
        context: str,
        default_return: Any = None
    ) -> Any:
        """
        Execute a database query with error handling, returning default on error.
        Logs errors but doesn't expose them to caller (for fetch operations).
        
        Args:
            operation: Function that performs the query
            context: Description of the operation for logging
            default_return: Value to return on error (default: None)
            
        Returns:
            Query result if successful, default_return if error occurs
        """
        try:
            return operation()
            
        except DatabaseError as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return default_return
            
        except Exception as e:
            ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return default_return

    @staticmethod
    def _execute_insert(
        sql: str,
        params: dict,
        entity_name: str,
        context: str
    ) -> tuple[bool, str | None, int | None]:
        """
        Execute an INSERT operation with standardized error handling.
        
        Args:
            sql: SQL INSERT statement
            params: Query parameters
            entity_name: Name of the entity for error messages
            context: Description for logging
            
        Returns:
            tuple[bool, str | None, int | None]: (success, error_message, insert_id)
        """
        try:
            result = QueryHelper.execute(sql, params)
            insert_id = result.get("last_insert_id")
            return True, None, int(insert_id) if insert_id is not None else None
            
        except DatabaseError as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.DATABASE_ERROR
            )
            return False, error_msg, None
            
        except Exception as e:
            error_msg = ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.GENERIC_ERROR
            )
            return False, error_msg, None

    @staticmethod
    def _execute_update(
        sql: str,
        params: dict,
        entity_name: str,
        entity_id: int,
        context: str
    ) -> tuple[bool, str | None]:
        """
        Execute an UPDATE operation with standardized error handling.
        
        Args:
            sql: SQL UPDATE statement
            params: Query parameters
            entity_name: Name of the entity for error messages
            entity_id: ID of the entity being updated
            context: Description for logging
            
        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        try:
            result = QueryHelper.execute(sql, params)
            
            if result.get("rows_affected", 0) != 1:
                logger.warning(f"{entity_name} not found for update: ID {entity_id}")
                return False, ErrorMessages.NOT_FOUND
                
            return True, None
            
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.DATABASE_ERROR
            )
            
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def _execute_delete(
        sql: str,
        params: dict,
        entity_name: str,
        entity_id: int,
        context: str
    ) -> tuple[bool, str | None]:
        """
        Execute a DELETE operation with standardized error handling.
        
        Args:
            sql: SQL DELETE statement
            params: Query parameters
            entity_name: Name of the entity for error messages
            entity_id: ID of the entity being deleted
            context: Description for logging
            
        Returns:
            tuple[bool, str | None]: (success, error_message)
        """
        try:
            result = QueryHelper.execute(sql, params)
            
            if result.get("rows_affected", 0) != 1:
                logger.warning(f"{entity_name} not found for deletion: ID {entity_id}")
                return False, ErrorMessages.NOT_FOUND
                
            return True, None
            
        except DatabaseError as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.DATABASE_ERROR
            )
            
        except Exception as e:
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context=context,
                user_message=ErrorMessages.GENERIC_ERROR
            )

    @staticmethod
    def _fetch_all_safe(
        sql: str,
        params: dict | None,
        context: str
    ) -> list[dict]:
        """
        Safely execute a fetch_all query with error handling.
        
        Args:
            sql: SQL SELECT statement
            params: Query parameters (optional)
            context: Description for logging
            
        Returns:
            List of dictionaries with query results, empty list on error
        """
        def operation():
            return QueryHelper.fetch_all(sql, params)
            
        return BaseModel._execute_query_safe(
            operation=operation,
            context=context,
            default_return=[]
        )

    @staticmethod
    def _fetch_one_safe(
        sql: str,
        params: dict | None,
        context: str
    ) -> dict | None:
        """
        Safely execute a fetch_one query with error handling.
        
        Args:
            sql: SQL SELECT statement
            params: Query parameters (optional)
            context: Description for logging
            
        Returns:
            Dictionary with query result, None on error or not found
        """
        def operation():
            return QueryHelper.fetch_one(sql, params)
            
        return BaseModel._execute_query_safe(
            operation=operation,
            context=context,
            default_return=None
        )

    @staticmethod
    def _search_by_id_pattern(
        table_name: str,
        columns: str,
        id_column: str,
        entity_id: int,
        entity_name: str,
        row_mapper: Callable[[dict], tuple]
    ) -> list[tuple]:
        """
        Common pattern for searching by ID.
        
        Args:
            table_name: Database table name
            columns: Columns to select
            id_column: Name of the ID column
            entity_id: ID to search for
            entity_name: Name of the entity for logging
            row_mapper: Function to map row dict to tuple
            
        Returns:
            List containing single tuple if found, empty list otherwise
        """
        sql = f"""
            SELECT {columns}
            FROM {table_name}
            WHERE {id_column} = :id
            ORDER BY {id_column}
        """
        
        rows = BaseModel._fetch_all_safe(
            sql=sql,
            params={"id": entity_id},
            context=f"searching {entity_name} by ID {entity_id}"
        )
        
        return [row_mapper(row) for row in rows]

    @staticmethod
    def _search_by_name_pattern(
        table_name: str,
        columns: str,
        name_column: str,
        search_term: str,
        entity_name: str,
        row_mapper: Callable[[dict], tuple],
        order_by: str | None = None
    ) -> list[tuple]:
        """
        Common pattern for case-insensitive partial name search.
        
        Args:
            table_name: Database table name
            columns: Columns to select
            name_column: Name of the column to search
            search_term: Term to search for
            entity_name: Name of the entity for logging
            row_mapper: Function to map row dict to tuple
            order_by: Optional ORDER BY clause (default: name_column)
            
        Returns:
            List of tuples matching the search criteria
        """
        order_clause = order_by or name_column
        
        sql = f"""
            SELECT {columns}
            FROM {table_name}
            WHERE {name_column} ILIKE :name
            ORDER BY {order_clause}
        """
        
        rows = BaseModel._fetch_all_safe(
            sql=sql,
            params={"name": f"%{search_term}%"},
            context=f"searching {entity_name} by name '{search_term}'"
        )
        
        return [row_mapper(row) for row in rows]

    @staticmethod
    def _get_all_pattern(
        table_name: str,
        columns: str,
        entity_name: str,
        row_mapper: Callable[[dict], tuple],
        order_by: str = "id",
        where_clause: str | None = None,
        params: dict | None = None
    ) -> list[tuple]:
        """
        Common pattern for fetching all records.
        
        Args:
            table_name: Database table name
            columns: Columns to select
            entity_name: Name of the entity for logging
            row_mapper: Function to map row dict to tuple
            order_by: Column to order by (default: 'id')
            where_clause: Optional WHERE clause
            params: Optional query parameters
            
        Returns:
            List of tuples with all records
        """
        sql = f"SELECT {columns} FROM {table_name}"
        
        if where_clause:
            sql += f" WHERE {where_clause}"
            
        sql += f" ORDER BY {order_by} ASC"
        
        rows = BaseModel._fetch_all_safe(
            sql=sql,
            params=params,
            context=f"retrieving all {entity_name}s"
        )
        
        return [row_mapper(row) for row in rows]
