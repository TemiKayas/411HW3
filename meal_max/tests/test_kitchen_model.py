import pytest
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_meal_by_id, update_meal_stats
from meal_max.utils.sql_utils import get_db_connection
import sqlite3

######################################################
#
#    Fixtures
#
######################################################

@pytest.fixture
def mock_db_cursor(mocker):
    """Fixture to mock database connection and cursor."""
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_conn.cursor.return_value = mock_cursor

    # Patch the get_db_connection to return the mocked connection
    mocker.patch("meal_max.utils.sql_utils.get_db_connection", return_value=mock_conn)
    return mock_cursor


@pytest.fixture
def sample_meal():
    """Fixture to provide a sample meal object."""
    return Meal(1, "Sample Meal", "Cuisine Type", 15.00, "MED")


######################################################
#
#    Add and Delete Test Cases
#
######################################################

def test_create_meal_success(mock_db_cursor):
    """Test successfully creating a new meal in the database."""
    create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="LOW")
    mock_db_cursor.execute.assert_called_once_with(
        "INSERT INTO meals (meal, cuisine, price, difficulty) VALUES (?, ?, ?, ?)",
        ("Meal 1", "Cuisine 1", 10.0, "LOW")
    )


def test_create_duplicate_meal(mock_db_cursor):
    """Test attempting to create a duplicate meal raises an error."""
    mock_db_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed")
    with pytest.raises(ValueError, match="Meal with this name already exists"):
        create_meal(meal="Meal 1", cuisine="Cuisine 1", price=10.0, difficulty="LOW")

def test_delete_meal_success(mock_db_cursor):
    """Test successfully marking a meal as deleted."""
    mock_db_cursor.fetchone.return_value = (False,)  # Meal not deleted
    delete_meal(1)
    mock_db_cursor.execute.assert_any_call("UPDATE meals SET deleted = TRUE WHERE id = ?", (1,))


def test_delete_meal_already_deleted(mock_db_cursor):
    """Test attempting to delete a meal that is already marked as deleted."""
    mock_db_cursor.fetchone.return_value = (True,)  # Meal already deleted
    with pytest.raises(ValueError, match="Meal with ID 1 is already deleted"):
        delete_meal(1)


def test_delete_meal_not_found(mock_db_cursor):
    """Test attempting to delete a meal that doesn't exist."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        delete_meal(1)


#######################################################
#
#    Meal Retrieval Test Cases
#
#######################################################

def test_get_meal_by_id_success(mock_db_cursor, sample_meal):
    """Test retrieving a meal by its ID successfully."""
    mock_db_cursor.fetchone.return_value = (1, "Sample Meal", "Cuisine Type", 15.00, "MED", False)
    meal = get_meal_by_id(1)
    assert meal == sample_meal, f"Expected {sample_meal}, got {meal}"


def test_get_meal_by_id_not_found(mock_db_cursor):
    """Test retrieving a meal by an ID that doesn't exist."""
    mock_db_cursor.fetchone.return_value = None
    with pytest.raises(ValueError, match="Meal with ID 1 not found"):
        get_meal_by_id(1)


#######################################################
#
#    Meal Update Test Cases
#
#######################################################

def test_update_meal_stats_success(mock_db_cursor):
    """Test successfully updating the stats of a meal."""
    update_meal_stats(1, "win")
    mock_db_cursor.execute.assert_called_once_with(
        "UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (1,)
    )


def test_update_meal_stats_invalid_operation(mock_db_cursor):
    """Test updating meal stats with an invalid operation."""
    with pytest.raises(ValueError, match="Invalid operation: draw"):
        update_meal_stats(1, "draw")
