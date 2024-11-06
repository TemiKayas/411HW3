import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal, update_meal_stats


@pytest.fixture
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.kitchen_model.update_meal_stats")

@pytest.fixture
def sample_meal1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 10.0, 'MED')

@pytest.fixture
def sample_meal2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 20.0, 'HIGH')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

##################################################
# Add Combatant Management Test Cases
##################################################

def test_add_combatant_to_battle(battle_model, sample_meal1):
    """Test adding a combatant to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Meal 1'

def test_add_duplicate_combatant_to_battle(battle_model, sample_meal1):
    """Test error when adding a duplicate combatant to the battle by ID."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Combatant with ID 1 already exists in the battle."):
        battle_model.prep_combatant(sample_meal1)


##################################################
# Remove Combatant Management Test Cases
##################################################

def test_remove_combatant_from_battle_by_meal_id(battle_model, sample_combatants):
    """Test removing a combatant from the battle by meal ID."""
    battle_model.combatants.extend(sample_combatants)
    assert len(battle_model.combatants) == 2

    battle_model.remove_combatant_by_meal_id(1)
    assert len(battle_model.combatants) == 1, f"Expected 1 combatant, but got {len(battle_model.combatants)}"
    assert battle_model.combatants[0].id == 2, "Expected combatant with ID 2 to remain"

def test_remove_combatant_by_position(battle_model, sample_combatants):
    """Test removing a combatant from the battle by position."""
    battle_model.combatants.extend(sample_combatants)
    assert len(battle_model.combatants) == 2

    # Remove combatant at position 1 (first combatant)
    battle_model.remove_combatant_by_position(1)
    assert len(battle_model.combatants) == 1, f"Expected 1 combatant, but got {len(battle_model.combatants)}"
    assert battle_model.combatants[0].id == 2, "Expected combatant with ID 2 to remain"

def test_clear_battle(battle_model, sample_meal1):
    """Test clearing the entire battle."""
    battle_model.prep_combatant(sample_meal1)

    battle_model.clear_battle()
    assert len(battle_model.combatants) == 0, "Battle should be empty after clearing"

def test_clear_battle_empty_battle(battle_model, caplog):
    """Test clearing the entire battle when it's empty."""
    battle_model.clear_battle()
    assert len(battle_model.combatants) == 0, "Battle should be empty after clearing"
    assert "Clearing an empty battle" in caplog.text, "Expected warning message when clearing an empty battle"


##################################################
# Tracklisting Management Test Cases
##################################################

def test_move_combatant_to_position(battle_model, sample_combatants):
    """Test moving a combatant to a specific position in the battle."""
    battle_model.combatants.extend(sample_combatants)

    battle_model.move_combatant_to_position(2, 1)  # Move Meal 2 to the first position
    assert battle_model.combatants[0].id == 2, "Expected Meal 2 to be in the first position"
    assert battle_model.combatants[1].id == 1, "Expected Meal 1 to be in the second position"

def test_swap_combatants_in_battle(battle_model, sample_combatants):
    """Test swapping the positions of two combatants in the battle."""
    battle_model.combatants.extend(sample_combatants)

    battle_model.swap_combatants(1, 2)  # Swap positions of Meal 1 and Meal 2
    assert battle_model.combatants[0].id == 2, "Expected Meal 2 to be in the first position"
    assert battle_model.combatants[1].id == 1, "Expected Meal 1 to be in the second position"

def test_swap_combatant_with_itself(battle_model, sample_meal1):
    """Test swapping the position of a combatant with itself raises an error."""
    battle_model.prep_combatant(sample_meal1)

    with pytest.raises(ValueError, match="Cannot swap a combatant with itself"):
        battle_model.swap_combatants(1, 1)  # Swap positions of Meal 1 with itself

def test_move_combatant_to_end(battle_model, sample_combatants):
    """Test moving a combatant to the end of the battle sequence."""
    battle_model.combatants.extend(sample_combatants)

    battle_model.move_combatant_to_end(1)  # Move Meal 1 to the end
    assert battle_model.combatants[1].id == 1, "Expected Meal 1 to be at the end"

def test_move_combatant_to_beginning(battle_model, sample_combatants):
    """Test moving a combatant to the beginning of the battle sequence."""
    battle_model.combatants.extend(sample_combatants)

    battle_model.move_combatant_to_beginning(2)  # Move Meal 2 to the beginning
    assert battle_model.combatants[0].id == 2, "Expected Meal 2 to be at the beginning"


##################################################
# Combatant Retrieval Test Cases
##################################################

def test_get_combatant_by_position(battle_model, sample_combatants):
    """Test successfully retrieving a combatant by their position in the battle."""
    battle_model.combatants.extend(sample_combatants)

    retrieved_combatant = battle_model.get_combatant_by_position(1)
    assert retrieved_combatant.id == 1
    assert retrieved_combatant.meal == 'Meal 1'
    assert retrieved_combatant.cuisine == 'Cuisine 1'
    assert retrieved_combatant.price == 10.0
    assert retrieved_combatant.difficulty == 'MED'

def test_get_all_combatants(battle_model, sample_combatants):
    """Test successfully retrieving all combatants from the battle."""
    battle_model.combatants.extend(sample_combatants)

    all_combatants = battle_model.get_all_combatants()
    assert len(all_combatants) == 2
    assert all_combatants[0].id == 1
    assert all_combatants[1].id == 2

def test_get_combatant_by_meal_id(battle_model, sample_meal1):
    """Test successfully retrieving a combatant by their meal ID."""
    battle_model.prep_combatant(sample_meal1)

    retrieved_combatant = battle_model.get_combatant_by_meal_id(1)

    assert retrieved_combatant.id == 1
    assert retrieved_combatant.meal == 'Meal 1'
    assert retrieved_combatant.cuisine == 'Cuisine 1'
    assert retrieved_combatant.price == 10.0
    assert retrieved_combatant.difficulty == 'MED'

def test_get_current_combatant(battle_model, sample_combatants):
    """Test successfully retrieving the current combatant in the battle."""
    battle_model.combatants.extend(sample_combatants)

    current_combatant = battle_model.get_current_combatant()
    assert current_combatant.id == 1
    assert current_combatant.meal == 'Meal 1'
    assert current_combatant.cuisine == 'Cuisine 1'
    assert current_combatant.price == 10.0
    assert current_combatant.difficulty == 'MED'

def test_get_battle_size(battle_model, sample_combatants):
    """Test getting the size of the battle (number of combatants)."""
    battle_model.combatants.extend(sample_combatants)
    assert battle_model.get_battle_size() == 2, "Expected battle size to be 2"

def test_get_total_battle_cost(battle_model, sample_combatants):
    """Test getting the total cost of all meals in the battle."""
    battle_model.combatants.extend(sample_combatants)
    assert battle_model.get_total_battle_cost() == 30.0, "Expected total battle cost to be 30.0"


##################################################
# Utility Function Test Cases
##################################################

def test_check_if_battle_ready_non_empty(battle_model, sample_combatants):
    """Test check_battle_ready does not raise error if battle is ready."""
    battle_model.combatants.extend(sample_combatants)
    try:
        battle_model.check_battle_ready()
    except ValueError:
        pytest.fail("check_battle_ready raised ValueError unexpectedly when battle was ready")

def test_check_battle_ready_empty_battle(battle_model):
    """Test check_battle_ready raises error when battle is not ready."""
    with pytest.raises(ValueError, match="Battle is not ready."):
        battle_model.check_battle_ready()

def test_validate_combatant_id(battle_model, sample_combatants):
    """Test validate_combatant_id does not raise error for valid combatant ID."""
    battle_model.combatants.extend(sample_combatants)
    try:
        battle_model.validate_combatant_id(1)
    except ValueError:
        pytest.fail("validate_combatant_id raised ValueError unexpectedly for valid combatant ID")

def test_validate_combatant_id_no_check_in_battle(battle_model):
    """Test validate_combatant_id does not raise error for valid ID when not in combatants."""
    try:
        battle_model.validate_combatant_id(1, check_in_battle=False)
    except ValueError:
        pytest.fail("validate_combatant_id raised ValueError unexpectedly for valid combatant ID")

def test_validate_combatant_id_invalid_id(battle_model):
    """Test validate_combatant_id raises error for invalid combatant ID."""
    with pytest.raises(ValueError, match="Invalid combatant id: -1"):
        battle_model.validate_combatant_id(-1)

    with pytest.raises(ValueError, match="Invalid combatant id: invalid"):
        battle_model.validate_combatant_id("invalid")

def test_validate_combatant_position(battle_model, sample_combatants):
    """Test validate_combatant_position does not raise error for valid position."""
    battle_model.combatants.extend(sample_combatants)
    try:
        battle_model.validate_combatant_position(1)
    except ValueError:
        pytest.fail("validate_combatant_position raised ValueError unexpectedly for valid position")

def test_validate_combatant_position_invalid(battle_model, sample_combatants):
    """Test validate_combatant_position raises error for invalid position."""
    battle_model.combatants.extend(sample_combatants)

    with pytest.raises(ValueError, match="Invalid combatant position: 0"):
        battle_model.validate_combatant_position(0)

    with pytest.raises(ValueError, match="Invalid combatant position: 3"):
        battle_model.validate_combatant_position(3)

    with pytest.raises(ValueError, match="Invalid combatant position: invalid"):
        battle_model.validate_combatant_position("invalid")

##################################################
# Playback Test Cases
##################################################

def test_play_current_battle(battle_model, sample_combatants, mock_update_meal_stats):
    """Test playing the current battle."""
    battle_model.combatants.extend(sample_combatants)
    
    # Mock internal get_random logic to control the winner
    with pytest.patch("meal_max.models.battle_model.get_random", return_value=0.4):
        winner = battle_model.play_current_battle()
    
    assert winner == "Meal 1", f"Expected winner to be 'Meal 1', but got {winner}"
    mock_update_meal_stats.assert_any_call(1, "win")
    mock_update_meal_stats.assert_any_call(2, "loss")

def test_rewind_battle_sequence(battle_model, sample_combatants):
    """Test rewinding the battle sequence to the first combatant."""
    battle_model.combatants.extend(sample_combatants)
    battle_model.current_combatant_index = 1  # Assume second combatant is current
    
    battle_model.rewind_battle_sequence()
    assert battle_model.current_combatant_index == 0, "Expected to rewind to the first combatant"

def test_go_to_battle_round(battle_model, sample_combatants):
    """Test moving to a specific battle round."""
    battle_model.combatants.extend(sample_combatants)
    
    battle_model.go_to_battle_round(2)  # Go to second combatant
    assert battle_model.current_combatant_index == 1, "Expected to be at second combatant"

def test_play_entire_battle_sequence(battle_model, sample_combatants, mock_update_meal_stats):
    """Test playing all battles in sequence."""
    battle_model.combatants.extend(sample_combatants)

    # Mocking randomness for controlled outcomes
    with pytest.patch("meal_max.models.battle_model.get_random", side_effect=[0.3, 0.6]):
        battle_model.play_entire_battle_sequence()

    # Ensure all battles were processed and play counts updated
    mock_update_meal_stats.assert_any_call(1, "win")
    mock_update_meal_stats.assert_any_call(2, "win")
    assert mock_update_meal_stats.call_count == len(sample_combatants)

    # Ensure combatant index resets after finishing sequence
    assert battle_model.current_combatant_index == 0, "Expected to reset to the first combatant"

def test_play_remaining_battle_sequence(battle_model, sample_combatants, mock_update_meal_stats):
    """Test playing from current combatant to the end."""
    battle_model.combatants.extend(sample_combatants)
    battle_model.current_combatant_index = 1  # Start from the second combatant
    
    # Mock randomness for remaining battles
    with pytest.patch("meal_max.models.battle_model.get_random", return_value=0.6):
        battle_model.play_remaining_battle_sequence()

    mock_update_meal_stats.assert_called_once_with(2, "win")
    assert battle_model.current_combatant_index == 0, "Expected to reset to the first combatant"
