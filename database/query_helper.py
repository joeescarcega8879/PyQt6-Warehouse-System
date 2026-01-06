import json
from config.logger_config import logger
from PyQt6.QtSql import QSqlQuery, QSqlDatabase, QSqlError

class DatabaseError(Exception):
    """Custom exception for database errors."""
    pass

class QueryHelper:
    """
    A helper class for executing SQL queries using PyQt6's QSqlQuery.
    """
    
    CONNECTION_NAME = "inventory_connection"

    @classmethod
    def _get_query(cls) -> QSqlQuery:

        """
        Retrieves a QSqlQuery object associated with the predefined database connection.

        Returns:
            QSqlQuery: An instance of QSqlQuery linked to the specified database connection.
        Raises:
            RuntimeError: If the database connection is not open.
        """

        db = QSqlDatabase.database(cls.CONNECTION_NAME)

        if not db.isOpen():
            raise RuntimeError("Database connection is not open.")
        
        return QSqlQuery(db)
    
    @classmethod
    def _prepare_query(cls, sql: str, params: dict | None = None) -> QSqlQuery:
        """
        Prepare a query with parameters.
        Args:
            sql (str): The SQL statement to prepare.
            params (dict | None): A dictionary of parameters to bind to the SQL statement.
        Returns:
            QSqlQuery: A prepared query object.
        Raises:
            DatabaseError: If SQL is empty or None.
        """
        if not sql or not sql.strip():
            raise DatabaseError("SQL statement cannot be empty.")
        
        query = cls._get_query()
        query.prepare(sql)
        
        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        
        return query
    
    @classmethod
    def execute(cls, sql: str, params: dict | None = None) -> dict:
        """
        Execute INSERT, UPDATE or DELETE statements.
        Args:
            sql (str): The SQL statement to be executed.
            params (dict | None): A dictionary of parameters to bind to the SQL statement.
        Returns:
            dict: A dictionary containing:
                - 'success' (bool): True if execution was successful
                - 'rows_affected' (int): Number of rows affected
                - 'last_insert_id' (int): Last inserted ID (for INSERT statements)
        Raises:
            DatabaseError: If the query execution fails.
        """
        query = cls._prepare_query(sql, params)

        if not query.exec():
            error_msg = cls._log_error(query.lastError(), sql)
            raise DatabaseError(error_msg)
        
        return {
            'success': True,
            'rows_affected': query.numRowsAffected(),
            'last_insert_id': query.lastInsertId()
        }
    
    @classmethod
    def fetch_all(cls, sql: str, params: dict | None = None) -> list[dict]:
        """
        Execute a SELECT statement and fetch all results.
        Args:
            sql (str): The SQL SELECT statement to be executed.
            params (dict | None): A dictionary of parameters to bind to the SQL statement.
        Returns:
            list[dict]: A list of dictionaries representing the fetched rows.
        Raises:
            DatabaseError: If the query execution fails.
        """
        query = cls._prepare_query(sql, params)
        results = []

        if not query.exec():
            error_msg = cls._log_error(query.lastError(), sql)
            raise DatabaseError(error_msg)
        
        record = query.record()
        columns = [record.fieldName(i) for i in range(record.count())]

        while query.next():
            row = {columns[i]: query.value(i) for i in range(len(columns))}
            results.append(row)

        return results
    
    @classmethod
    def fetch_one(cls, sql: str, params: dict | None = None) -> dict | None:
        """
        Execute a SELECT statement and fetch a single result.
        Args:
            sql (str): The SQL SELECT statement to be executed.
            params (dict | None): A dictionary of parameters to bind to the SQL statement.
        Returns:
            dict | None: A dictionary representing the fetched row, or None if no row was found
        """

        rows = cls.fetch_all(sql, params)
        return rows[0] if rows else None
    
    @classmethod
    def _log_error(cls, error: QSqlError, sql: str) -> str:
        """
        Logs SQL errors using the logging module.
        Args:
            error (QSqlError): The error object containing error details.
            sql (str): The SQL statement that caused the error.
        Returns:
            str: The formatted error message.
        """
        error_msg = (
            f"SQL Error:\n"
            f"Query: {sql}\n"
            f"Driver: {error.driverText()}\n"
            f"Database: {error.databaseText()}"
        )
        logger.error(error_msg)
        return error_msg
    
    @classmethod
    def _to_json_(cls, data: dict) -> str:
        """
        Convert a dictionary to a JSON string.
        Args:
            data (dict): The data to convert.
        Returns:
            str: The JSON string representation of the data.
        """
        
        try:
            return json.dumps(data)
        except (TypeError, ValueError) as e:
            logger.error(f"Error converting to JSON: {e}")
            return "{}"

    @classmethod
    def begin_transaction(cls) -> bool:
        """
        Begin a database transaction.
        Returns:
            bool: True if transaction started successfully.
        Raises:
            DatabaseError: If transaction cannot be started.
        """
        db = QSqlDatabase.database(cls.CONNECTION_NAME)
        if not db.transaction():
            raise DatabaseError("Failed to begin transaction.")
        return True
    
    @classmethod
    def commit(cls) -> bool:
        """
        Commit the current transaction.
        Returns:
            bool: True if commit was successful.
        Raises:
            DatabaseError: If commit fails.
        """
        db = QSqlDatabase.database(cls.CONNECTION_NAME)
        if not db.commit():
            raise DatabaseError("Failed to commit transaction.")
        return True
    
    @classmethod
    def rollback(cls) -> bool:
        """
        Rollback the current transaction.
        Returns:
            bool: True if rollback was successful.
        Raises:
            DatabaseError: If rollback fails.
        """
        db = QSqlDatabase.database(cls.CONNECTION_NAME)
        if not db.rollback():
            raise DatabaseError("Failed to rollback transaction.")
        return True