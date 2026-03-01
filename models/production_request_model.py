from config.logger_config import logger
from database.query_helper import QueryHelper, DatabaseError

class ProductionRequestModel:
    """
    Model class for managing production requests in the database.
    """

    @staticmethod
    def create_request(
        line_id: int, 
        requested_by: int, 
        status: str, 
        items: list[dict]) -> tuple[bool, str | None, int | None]:
        """
        Creates a new production request in the database.
        Args:
            line_id (int): The ID of the production line.
            requested_by (int): The ID of the user making the request.
            status (str): The status of the production request.
            items (list[dict]): A list of items to be produced, each represented as a dictionary.
        Returns:
            tuple[bool, str | None, int | None]: A tuple containing a boolean indicating success,
            an optional error message, and the ID of the created production request if successful.
        """

        try:
            QueryHelper.begin_transaction()

            result = QueryHelper.execute(
                """
                INSERT INTO production_requests(line_id, requested_by, status, requested_at, approved_by, approved_at, is_active)
                VALUES(:line_id, :requested_by, :status, NOW(), NULL, NULL, TRUE)
                RETURNING request_id
                """,
                {
                    "line_id": line_id,
                    "requested_by": requested_by,
                    "status": status
                }
            )

            request_id = result.get("last_insert_id")
            if not request_id:
                raise DatabaseError("Failed to retrieve the new request ID.")
            
            
            for item in items:
                QueryHelper.execute(
                    """
                    INSERT INTO production_request_items(request_id, material_id, quantity, unit)
                    VALUES(:request_id, :material_id, :quantity, :unit)
                    """,
                    {
                        "request_id": request_id,
                        "material_id": item["material_id"],
                        "quantity": item["quantity"],
                        "unit": item["unit"]
                    }
                )
            
            QueryHelper.commit()
            return True, None, request_id
        
        except DatabaseError as e:
            QueryHelper.rollback()
            logger.error(f"Error creating production request: {e}")
            return False, str(e), None
        
        except Exception as e:
            QueryHelper.rollback()
            logger.error(f"Unexpected error creating production request: {e}")
            return False, str(e), None
    
    @staticmethod
    def update_status_request(
        request_id: int, 
        status: str, 
        approved_by: int | None = None) -> tuple[bool, str | None]:
        """
        Updates the status of an existing production request.
        Args:
            request_id (int): The ID of the production request to update.
            status (str): The new status of the production request.
            approved_by (int | None): The ID of the user approving the request, if applicable.
        Returns:
            tuple[bool, str | None]: A tuple containing a boolean indicating success and an optional error message.
        """

        try:
            QueryHelper.execute(
                """
                UPDATE production_requests
                SET status = :status,
                   approved_by = :approved_by,
                   approved_at = CASE
                       WHEN :approved_by IS NOT NULL THEN NOW()
                       ELSE NULL
                   END
                WHERE request_id = :request_id
                """,
                {
                    "status": status,
                    "approved_by": approved_by,
                    "request_id": request_id
                }
            )

            return True, None
        
        except DatabaseError as e:
            logger.error(f"Error updating production request status: {e}")
            return False, str(e)
        
        except Exception as e:
            logger.error(f"Unexpected error updating production request status: {e}")
            return False, str(e)

    @staticmethod
    def deactivate_request(request_id: int) -> tuple[bool, str | None]:
        """
        Deactivates a production request in the database.
        Args:
            request_id (int): The ID of the production request to deactivate.
        Returns:
            tuple[bool, str | None]: A tuple containing a boolean indicating success and an optional error message.
        """

        try:
            QueryHelper.execute(
                """
                UPDATE production_requests
                SET is_active = FALSE
                WHERE request_id = :request_id
                """,
                {
                    "request_id": request_id
                }
            )

            return True, None
        
        except DatabaseError as e:
            logger.error(f"Error deactivating production request: {e}")
            return False, str(e)
        
        except Exception as e:
            logger.error(f"Unexpected error deactivating production request: {e}")
            return False, str(e) 
        
    @staticmethod
    def get_all_requests() -> list[tuple]:
        """
        Retrieves all production requests from the database.
        Returns:
            list[tuple]: A list of tuples representing the production requests.
        """

        try:
            rows = QueryHelper.fetch_all(
                """
                SELECT
                    pr.request_id,
                    pr.line_id,
                    pl.line_name,
                    pr.status,
                    pr.requested_at,
                    pr.requested_by,
                    u_req.username AS requested_by_name,
                    pr.approved_by,
                    u_app.username AS approved_by_name,
                    pr.approved_at,
                    pr.is_active
                FROM production_requests pr
                JOIN production_lines pl
                    ON pl.line_id = pr.line_id
                JOIN users u_req
                    ON u_req.user_id = pr.requested_by
                LEFT JOIN users u_app
                    ON u_app.user_id = pr.approved_by
                ORDER BY pr.request_id DESC
                """
            )

            return [
                (
                    row["request_id"],
                    row["line_id"],
                    row["line_name"],
                    row["status"],
                    row["requested_at"],
                    row["requested_by"],
                    row["requested_by_name"],
                    row["approved_by"],
                    row["approved_by_name"],
                    row["approved_at"],
                    row["is_active"]
                )
                for row in rows
            ]
        except DatabaseError as e:
            logger.error(f"Error retrieving production requests: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving production requests: {e}")
            return []
        
    @staticmethod
    def get_request_by_id(request_id: int) -> list[tuple]:
        """
        Retrieves a production request by its ID.
        Args:
            request_id (int): The ID of the production request to retrieve.
        Returns:
            tuple | None: A tuple representing the production request, or None if not found.
        """

        try:
            row = QueryHelper.fetch_one(
                """
                SELECT
                    pr.request_id,
                    pr.line_id,
                    pl.line_name,
                    pr.status,
                    pr.requested_at,
                    pr.requested_by,
                    u_req.username AS requested_by_name,
                    pr.approved_by,
                    u_app.username AS approved_by_name,
                    pr.approved_at,
                    pr.is_active
                FROM production_requests pr
                JOIN production_lines pl
                    ON pl.line_id = pr.line_id
                JOIN users u_req
                    ON u_req.user_id = pr.requested_by
                LEFT JOIN users u_app
                    ON u_app.user_id = pr.approved_by
                WHERE pr.request_id = :request_id
                """,
                {
                    "request_id": request_id
                }
            )

            if row:
                return [(
                    row["request_id"],
                    row["line_id"],
                    row["line_name"],
                    row["status"],
                    row["requested_at"],
                    row["requested_by"],
                    row["requested_by_name"],
                    row["approved_by"],
                    row["approved_by_name"],
                    row["approved_at"],
                    row["is_active"]
                )]
            return []
        
        except DatabaseError as e:
            logger.error(f"Error retrieving production request by ID: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving production request by ID: {e}")
            return []