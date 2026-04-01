from src.models.base_model import BaseModel
from src.database.query_helper import QueryHelper, DatabaseError
from src.common.error_messages import ErrorMessages


class ProductionRequestModel(BaseModel):
    """
    Model class for managing production requests in the database.
    """

    ENTITY_NAME = "production request"

    _REQUEST_COLUMNS = """
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
    """

    _REQUEST_FROM = """
        FROM production_requests pr
        JOIN production_lines pl ON pl.line_id = pr.line_id
        JOIN users u_req ON u_req.user_id = pr.requested_by
        LEFT JOIN users u_app ON u_app.user_id = pr.approved_by
    """

    @staticmethod
    def _map_row(row: dict) -> tuple:
        return (
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
            row["is_active"],
        )

    @staticmethod
    def create_request(
        line_id: int,
        requested_by: int,
        status: str,
        items: list[dict],
    ) -> tuple[bool, str | None, int | None]:
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
                {"line_id": line_id, "requested_by": requested_by, "status": status},
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
                        "unit": item["unit"],
                    },
                )

            QueryHelper.commit()
            return True, None, request_id

        except DatabaseError as e:
            QueryHelper.rollback()
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context="creating production request",
                user_message=ErrorMessages.SAVE_FAILED,
            ), None

        except Exception as e:
            QueryHelper.rollback()
            return False, ErrorMessages.log_and_mask_error(
                error=e,
                context="creating production request (unexpected error)",
                user_message=ErrorMessages.GENERIC_ERROR,
            ), None

    @staticmethod
    def update_status_request(
        request_id: int,
        status: str,
        approved_by: int | None = None,
    ) -> tuple[bool, str | None]:
        """
        Updates the status of an existing production request.
        Args:
            request_id (int): The ID of the production request to update.
            status (str): The new status of the production request.
            approved_by (int | None): The ID of the user approving the request, if applicable.
        Returns:
            tuple[bool, str | None]: A tuple containing a boolean indicating success and an optional error message.
        """
        def operation():
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
                {"status": status, "approved_by": approved_by, "request_id": request_id},
            )
            return True

        result, error = BaseModel._execute_with_error_handling(
            operation=operation,
            context="updating production request status",
            default_return=False,
            entity_name=ProductionRequestModel.ENTITY_NAME,
        )
        return result, error

    @staticmethod
    def deactivate_request(request_id: int) -> tuple[bool, str | None]:
        """
        Deactivates a production request in the database.
        Args:
            request_id (int): The ID of the production request to deactivate.
        Returns:
            tuple[bool, str | None]: A tuple containing a boolean indicating success and an optional error message.
        """
        def operation():
            QueryHelper.execute(
                """
                UPDATE production_requests
                SET is_active = FALSE
                WHERE request_id = :request_id
                """,
                {"request_id": request_id},
            )
            return True

        result, error = BaseModel._execute_with_error_handling(
            operation=operation,
            context="deactivating production request",
            default_return=False,
            entity_name=ProductionRequestModel.ENTITY_NAME,
        )
        return result, error

    @staticmethod
    def get_all_requests() -> list[tuple]:
        """
        Retrieves all production requests from the database.
        Returns:
            list[tuple]: A list of tuples representing the production requests.
        """
        rows = BaseModel._fetch_all_safe(
            sql=f"""
                SELECT {ProductionRequestModel._REQUEST_COLUMNS}
                {ProductionRequestModel._REQUEST_FROM}
                ORDER BY pr.request_id DESC
                """,
            params=None,
            context="retrieving all production requests",
        )
        return [ProductionRequestModel._map_row(row) for row in rows]

    @staticmethod
    def get_request_by_id(request_id: int) -> list[tuple]:
        """
        Retrieves a production request by its ID.
        Args:
            request_id (int): The ID of the production request to retrieve.
        Returns:
            list[tuple]: A list containing the production request tuple if found, empty list otherwise.
        """
        row = BaseModel._fetch_one_safe(
            sql=f"""
                SELECT {ProductionRequestModel._REQUEST_COLUMNS}
                {ProductionRequestModel._REQUEST_FROM}
                WHERE pr.request_id = :request_id
                """,
            params={"request_id": request_id},
            context=f"retrieving production request by ID {request_id}",
        )
        return [ProductionRequestModel._map_row(row)] if row else []
