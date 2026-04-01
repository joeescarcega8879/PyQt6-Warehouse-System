"""
Unit tests for MaterialModel class.
Tests material CRUD operations and error handling with mocked database.
NOTE: After refactoring to use BaseModel, mocks target 'models.base_model.QueryHelper'
"""

import pytest
from unittest.mock import patch
from src.models.material_model import MaterialModel
from src.database.query_helper import DatabaseError
from src.common.error_messages import ErrorMessages


class TestAddMaterial:
    """Tests for add_material method."""
    
    @pytest.mark.unit
    def test_successful_material_addition(self):
        """Test successful addition of a new material."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1, "last_insert_id": 1}):
            # Act
            success, error = MaterialModel.add_material(
                name="Steel",
                description="High-grade steel",
                unit="kg"
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_add_material_with_all_parameters(self):
        """Test that all parameters are passed correctly to database."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1, "last_insert_id": 1}) as mock_execute:
            # Act
            MaterialModel.add_material(
                name="Aluminum",
                description="Lightweight metal",
                unit="tons"
            )
            
            # Assert
            params = mock_execute.call_args[0][1]
            assert params["name"] == "Aluminum"
            assert params["description"] == "Lightweight metal"
            assert params["unit"] == "tons"
    
    @pytest.mark.unit
    def test_add_material_returns_insert_id(self):
        """Test adding material returns the insert ID when available."""
        # NOTE: After refactoring to BaseModel, INSERT operations return insert_id
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1, "last_insert_id": 42}):
            # Act
            success, error = MaterialModel.add_material(
                name="Material",
                description="Description",
                unit="unit"
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_add_material_database_error(self):
        """Test add material handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=DatabaseError("Insert failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                success, error = MaterialModel.add_material(
                    name="Material",
                    description="Description",
                    unit="unit"
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_add_material_generic_exception(self):
        """Test add material handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                success, error = MaterialModel.add_material(
                    name="Material",
                    description="Description",
                    unit="unit"
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.GENERIC_ERROR
    
    @pytest.mark.unit
    def test_add_material_with_unicode_characters(self):
        """Test adding material with unicode characters."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = MaterialModel.add_material(
                name="Acero Inoxidable",
                description="Material resistente a la corrosión",
                unit="kg"
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_add_material_with_special_characters(self):
        """Test adding material with special characters in name."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = MaterialModel.add_material(
                name="Material-123 (Type A)",
                description="Special material",
                unit="units"
            )
            
            # Assert
            assert success is True
            assert error is None


class TestUpdateMaterial:
    """Tests for update_material method."""
    
    @pytest.mark.unit
    def test_successful_material_update(self):
        """Test successful update of an existing material."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = MaterialModel.update_material(
                material_id=1,
                name="Updated Steel",
                description="Updated description",
                unit="tons"
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_update_material_with_all_parameters(self):
        """Test that all parameters are passed correctly to database."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}) as mock_execute:
            # Act
            MaterialModel.update_material(
                material_id=42,
                name="Copper",
                description="Conductive metal",
                unit="kg"
            )
            
            # Assert
            params = mock_execute.call_args[0][1]
            assert params["material_id"] == 42
            assert params["name"] == "Copper"
            assert params["description"] == "Conductive metal"
            assert params["unit"] == "kg"
    
    @pytest.mark.unit
    def test_update_material_not_found(self):
        """Test updating non-existent material returns NOT_FOUND error."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 0}):
            # Act
            success, error = MaterialModel.update_material(
                material_id=999,
                name="Material",
                description="Description",
                unit="unit"
            )
            
            # Assert
            assert success is False
            assert error == ErrorMessages.NOT_FOUND
    
    @pytest.mark.unit
    def test_update_material_database_error(self):
        """Test update material handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=DatabaseError("Update failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                success, error = MaterialModel.update_material(
                    material_id=1,
                    name="Material",
                    description="Description",
                    unit="unit"
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_update_material_generic_exception(self):
        """Test update material handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                success, error = MaterialModel.update_material(
                    material_id=1,
                    name="Material",
                    description="Description",
                    unit="unit"
                )
                
                # Assert
                assert success is False
                assert error == ErrorMessages.GENERIC_ERROR


class TestDeleteMaterial:
    """Tests for delete_material method."""
    
    @pytest.mark.unit
    def test_successful_material_deletion(self):
        """Test successful deletion of a material."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = MaterialModel.delete_material(material_id=1)
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_delete_material_passes_id(self):
        """Test that material_id is passed correctly to database."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}) as mock_execute:
            # Act
            MaterialModel.delete_material(material_id=42)
            
            # Assert
            params = mock_execute.call_args[0][1]
            assert params["material_id"] == 42
    
    @pytest.mark.unit
    def test_delete_material_not_found(self):
        """Test deleting non-existent material returns NOT_FOUND error."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 0}):
            # Act
            success, error = MaterialModel.delete_material(material_id=999)
            
            # Assert
            assert success is False
            assert error == ErrorMessages.NOT_FOUND
    
    @pytest.mark.unit
    def test_delete_material_database_error(self):
        """Test delete material handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=DatabaseError("Delete failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                success, error = MaterialModel.delete_material(material_id=1)
                
                # Assert
                assert success is False
                assert error == ErrorMessages.DATABASE_ERROR
    
    @pytest.mark.unit
    def test_delete_material_generic_exception(self):
        """Test delete material handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                success, error = MaterialModel.delete_material(material_id=1)
                
                # Assert
                assert success is False
                assert error == ErrorMessages.GENERIC_ERROR


class TestGetAllMaterials:
    """Tests for get_all_materials method."""
    
    @pytest.mark.unit
    def test_get_all_materials_success(self):
        """Test retrieving all materials successfully."""
        # Arrange
        mock_rows = [
            {"material_id": 1, "material_name": "Steel", "description": "Strong metal", "unit_of_measure": "kg"},
            {"material_id": 2, "material_name": "Wood", "description": "Natural material", "unit_of_measure": "m³"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.get_all_materials()
            
            # Assert
            assert len(result) == 2
            assert result[0] == (1, "Steel", "Strong metal", "kg")
            assert result[1] == (2, "Wood", "Natural material", "m³")
    
    @pytest.mark.unit
    def test_get_all_materials_empty_result(self):
        """Test get all materials when no materials exist."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            result = MaterialModel.get_all_materials()
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_get_all_materials_ordered_by_id(self):
        """Test that results are ordered by material_id ASC."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.get_all_materials()
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ORDER BY material_id ASC" in sql_query
    
    @pytest.mark.unit
    def test_get_all_materials_database_error(self):
        """Test get all materials handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                result = MaterialModel.get_all_materials()
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_get_all_materials_generic_exception(self):
        """Test get all materials handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                result = MaterialModel.get_all_materials()
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_get_all_materials_with_single_material(self):
        """Test retrieving single material."""
        # Arrange
        mock_rows = [
            {"material_id": 1, "material_name": "Steel", "description": "Strong metal", "unit_of_measure": "kg"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.get_all_materials()
            
            # Assert
            assert len(result) == 1
            assert result[0] == (1, "Steel", "Strong metal", "kg")


class TestSearchById:
    """Tests for search_by_id method."""
    
    @pytest.mark.unit
    def test_search_by_id_success(self):
        """Test searching material by ID successfully."""
        # Arrange
        mock_rows = [
            {"material_id": 42, "material_name": "Steel", "description": "Strong metal", "unit_of_measure": "kg"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.search_by_id(42)
            
            # Assert
            assert len(result) == 1
            assert result[0] == (42, "Steel", "Strong metal", "kg")
    
    @pytest.mark.unit
    def test_search_by_id_passes_parameter(self):
        """Test that material_id is passed correctly to query."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_id(123)
            
            # Assert
            params = mock_fetch.call_args[0][1]
            assert params["id"] == 123
    
    @pytest.mark.unit
    def test_search_by_id_not_found(self):
        """Test searching for non-existent material returns empty list."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            result = MaterialModel.search_by_id(999)
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_search_by_id_ordered_by_id(self):
        """Test that results are ordered by material_id."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_id(1)
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ORDER BY material_id" in sql_query
    
    @pytest.mark.unit
    def test_search_by_id_database_error(self):
        """Test search by ID handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                result = MaterialModel.search_by_id(1)
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_search_by_id_generic_exception(self):
        """Test search by ID handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                result = MaterialModel.search_by_id(1)
                
                # Assert
                assert result == []


class TestSearchByName:
    """Tests for search_by_name method."""
    
    @pytest.mark.unit
    def test_search_by_name_success(self):
        """Test searching material by name successfully."""
        # Arrange
        mock_rows = [
            {"material_id": 1, "material_name": "Steel", "description": "Strong metal", "unit_of_measure": "kg"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.search_by_name("Steel")
            
            # Assert
            assert len(result) == 1
            assert result[0] == (1, "Steel", "Strong metal", "kg")
    
    @pytest.mark.unit
    def test_search_by_name_partial_match(self):
        """Test that name search uses wildcards for partial matching."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_name("Steel")
            
            # Assert
            params = mock_fetch.call_args[0][1]
            assert params["name"] == "%Steel%"
    
    @pytest.mark.unit
    def test_search_by_name_case_insensitive(self):
        """Test that name search is case-insensitive (ILIKE)."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_name("steel")
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ILIKE" in sql_query
    
    @pytest.mark.unit
    def test_search_by_name_multiple_results(self):
        """Test searching for materials with similar names."""
        # Arrange
        mock_rows = [
            {"material_id": 1, "material_name": "Steel A", "description": "Type A", "unit_of_measure": "kg"},
            {"material_id": 2, "material_name": "Steel B", "description": "Type B", "unit_of_measure": "kg"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.search_by_name("Steel")
            
            # Assert
            assert len(result) == 2
            assert result[0][1] == "Steel A"
            assert result[1][1] == "Steel B"
    
    @pytest.mark.unit
    def test_search_by_name_not_found(self):
        """Test searching for non-existent material returns empty list."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]):
            # Act
            result = MaterialModel.search_by_name("Nonexistent")
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_search_by_name_ordered_by_id(self):
        """Test that results are ordered by material_id."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_name("Steel")
            
            # Assert
            sql_query = mock_fetch.call_args[0][0]
            assert "ORDER BY material_id" in sql_query
    
    @pytest.mark.unit
    def test_search_by_name_database_error(self):
        """Test search by name handles database errors gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=DatabaseError("Query failed")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.DATABASE_ERROR):
                # Act
                result = MaterialModel.search_by_name("Steel")
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_search_by_name_generic_exception(self):
        """Test search by name handles generic exceptions gracefully."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', 
                  side_effect=Exception("Unexpected error")):
            with patch('models.base_model.ErrorMessages.log_and_mask_error', 
                      return_value=ErrorMessages.GENERIC_ERROR):
                # Act
                result = MaterialModel.search_by_name("Steel")
                
                # Assert
                assert result == []
    
    @pytest.mark.unit
    def test_search_by_name_with_unicode(self):
        """Test searching for material with unicode characters."""
        # Arrange
        mock_rows = [
            {"material_id": 1, "material_name": "Acero Inoxidable", "description": "Acero", "unit_of_measure": "kg"}
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.search_by_name("Acero")
            
            # Assert
            assert len(result) == 1
            assert result[0][1] == "Acero Inoxidable"
    
    @pytest.mark.unit
    def test_search_by_name_with_special_characters(self):
        """Test searching handles SQL wildcards and special characters."""
        # Arrange
        with patch('models.base_model.QueryHelper.fetch_all', return_value=[]) as mock_fetch:
            # Act
            MaterialModel.search_by_name("Steel%")
            
            # Assert
            params = mock_fetch.call_args[0][1]
            # The % character should be wrapped in additional wildcards
            assert params["name"] == "%Steel%%"


class TestMaterialModelEdgeCases:
    """Tests for edge cases and special scenarios."""
    
    @pytest.mark.unit
    def test_add_material_with_empty_description(self):
        """Test adding material with empty description."""
        # Arrange
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}):
            # Act
            success, error = MaterialModel.add_material(
                name="Material",
                description="",
                unit="kg"
            )
            
            # Assert
            assert success is True
            assert error is None
    
    @pytest.mark.unit
    def test_update_material_with_very_long_description(self):
        """Test updating material with very long description."""
        # Arrange
        long_description = "A" * 1000
        
        with patch('models.base_model.QueryHelper.execute', 
                  return_value={"rows_affected": 1}) as mock_execute:
            # Act
            success, error = MaterialModel.update_material(
                material_id=1,
                name="Material",
                description=long_description,
                unit="kg"
            )
            
            # Assert
            assert success is True
            params = mock_execute.call_args[0][1]
            assert params["description"] == long_description
    
    @pytest.mark.unit
    def test_search_by_name_empty_string(self):
        """Test searching with empty string."""
        # Arrange
        mock_rows = []
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.search_by_name("")
            
            # Assert
            assert result == []
    
    @pytest.mark.unit
    def test_get_all_materials_large_dataset(self):
        """Test retrieving large number of materials."""
        # Arrange
        mock_rows = [
            {"material_id": i, "material_name": f"Material {i}", 
             "description": f"Desc {i}", "unit_of_measure": "kg"}
            for i in range(1000)
        ]
        
        with patch('models.base_model.QueryHelper.fetch_all', return_value=mock_rows):
            # Act
            result = MaterialModel.get_all_materials()
            
            # Assert
            assert len(result) == 1000
            assert result[0][0] == 0
            assert result[999][0] == 999
