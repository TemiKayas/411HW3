import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def setup_battle():
    """Create a new instance of BattleModel for isolated test execution."""
    return BattleModel()


@pytest.fixture
def patch_meal_stats(mocker):
    """Simulates the update_meal_stats function for controlled testing."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")


"""Fixtures to generate example meals for testing various cases."""
@pytest.fixture
def test_meal_1():
    return Meal(1, 'Meal 1', 'Cuisine 1', 20.00, 'LOW')


@pytest.fixture
def test_meal_2():
    return Meal(2, 'Meal 2', 'Cuisine 2', 25.00, 'MED')


@pytest.fixture
def test_meal_collection(test_meal_1, test_meal_2):
    return [test_meal_1, test_meal_2]


##################################################
# Battle Management Test Cases
##################################################

def test_first_meal_wins(setup_battle, test_meal_1, test_meal_2, patch_meal_stats, mocker):
    """Validate that test_meal_1 wins in the battle scenario."""
    setup_battle.combatants = [test_meal_1, test_meal_2]
    # Mock scores for test_meal_1 to ensure victory
    mocker.patch.object(setup_battle, 'get_battle_score', side_effect=[90, 85])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.02) 
    victor = setup_battle.battle()
    assert victor == test_meal_1.meal, f"Expected winner to be {test_meal_1.meal}, but received {victor}"
    patch_meal_stats.assert_any_call(test_meal_1.id, 'win')
    patch_meal_stats.assert_any_call(test_meal_2.id, 'loss')
    assert len(setup_battle.combatants) == 1
    assert setup_battle.combatants[0] == test_meal_1


def test_second_meal_wins(setup_battle, test_meal_1, test_meal_2, patch_meal_stats, mocker):
    """Confirm that test_meal_2 is the battle's victor."""
    setup_battle.combatants = [test_meal_1, test_meal_2]  
    # Mock scores for test_meal_2 to secure victory
    mocker.patch.object(setup_battle, 'get_battle_score', side_effect=[85, 90])
    mocker.patch("meal_max.models.battle_model.get_random", return_value=0.05)  
    victor = setup_battle.battle()
    assert victor == test_meal_2.meal, f"Expected victor to be {test_meal_2.meal}, but received {victor}"
    patch_meal_stats.assert_any_call(test_meal_2.id, 'win')
    patch_meal_stats.assert_any_call(test_meal_1.id, 'loss')
    assert len(setup_battle.combatants) == 1
    assert setup_battle.combatants[0] == test_meal_2


def test_battle_requires_two_combatants(setup_battle, test_meal_1):
    """Assert error when attempting battle with a single combatant."""
    # Only one combatant present
    setup_battle.combatants = [test_meal_1]   
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        setup_battle.battle()


##################################################
# Meal Retrieval Test Cases
##################################################

def test_retrieve_battle_score(setup_battle, test_meal_1):
    """Check accurate calculation of battle score for a combatant meal."""
    score = setup_battle.get_battle_score(test_meal_1)
    calculated_score = (test_meal_1.price * len(test_meal_1.cuisine)) - 3
    assert score == calculated_score, f"Expected score of {calculated_score}, received {score}"


##################################################
# Combatant Management Functions
##################################################

def test_empty_combatants_single_entry(setup_battle, test_meal_1):
    """Test removal of all combatants when only one is present."""
    setup_battle.combatants = [test_meal_1]
    setup_battle.clear_combatants()
    assert len(setup_battle.combatants) == 0, "Expected an empty combatant list post-clear"


def test_empty_combatants_multiple_entries(setup_battle, test_meal_1, test_meal_2):
    """Test removal of all combatants when multiple are present."""
    setup_battle.combatants = [test_meal_1, test_meal_2]
    setup_battle.clear_combatants()
    assert len(setup_battle.combatants) == 0, "Expected an empty combatant list post-clear"


def test_empty_combatants_initial_state(setup_battle):
    """Test clearing combatants when the list is already empty."""
    setup_battle.combatants = []
    setup_battle.clear_combatants()
    assert len(setup_battle.combatants) == 0, "Expected an empty combatant list post-clear"


def test_list_all_combatants_multiple(setup_battle, test_meal_1, test_meal_2):
    """Validate retrieval of all combatants from a populated list."""
    setup_battle.combatants = [test_meal_1, test_meal_2]
    combatants = setup_battle.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].id == 1
    assert combatants[1].id == 2


def test_list_all_combatants_single_entry(setup_battle, test_meal_1):
    """Validate retrieval of all combatants when only one exists."""
    setup_battle.combatants = [test_meal_1]
    combatants = setup_battle.get_combatants()
    assert len(combatants) == 1
    assert combatants[0].id == 1


def test_prepare_dual_combatants(setup_battle, test_meal_1, test_meal_2):
    """Verify successful preparation of two combatants."""
    setup_battle.prep_combatant(test_meal_1)
    setup_battle.prep_combatant(test_meal_2)
    assert len(setup_battle.combatants) == 2
    assert setup_battle.combatants == [test_meal_1, test_meal_2]


def test_prepare_single_combatant(setup_battle, test_meal_1):
    """Verify successful preparation of a lone combatant."""
    setup_battle.prep_combatant(test_meal_1)
    assert len(setup_battle.combatants) == 1
    assert setup_battle.combatants == [test_meal_1]


def test_add_third_combatant_error(setup_battle, test_meal_1, test_meal_2):
    """Check error raised upon trying to add a third combatant."""
    setup_battle.prep_combatant(test_meal_1)
    setup_battle.prep_combatant(test_meal_2)
    assert len(setup_battle.combatants) == 2, "Only two combatants should be prepped."
    assert setup_battle.combatants == [test_meal_1, test_meal_2], "Combatants list does not match expected values."
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        setup_battle.prep_combatant(Meal(3, 'Meal 3', 'Cuisine 3', 15.00, 'HIGH'))
