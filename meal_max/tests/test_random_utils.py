import pytest
import requests
from meal_max.utils.random_utils import get_random


RANDOM_NUMBER = 21


@pytest.fixture
def mock_random_service(mocker):
    mock_response = mocker.Mock()  # Create a mock object to replace the requests.get call.
    mock_response.text = f"{RANDOM_NUMBER}"  # Set the mock response's text attribute with the expected number.
    mocker.patch("requests.get", return_value=mock_response)  # Patch requests.get to return the mock response.
    return mock_response


def test_fetch_random_number(mock_random_service):
    """Verify retrieval of the expected random number from random.org using get_random."""
    result = get_random()
    assert result == RANDOM_NUMBER, f"Expected {RANDOM_NUMBER} as the random number, received {result}"  # Ensure the returned value matches.
    requests.get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )  # Verify that the correct URL was accessed.


def test_fetch_random_number_request_failure(mocker):
    """Simulate request failure when accessing random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))  # Mock a connection error.
    with pytest.raises(RuntimeError, match=r"Request to random\.org failed: Connection error"):
        get_random()  # Expect RuntimeError due to connection issue.


def test_fetch_random_number_timeout(mocker):
    """Simulate a timeout error for requests to random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)  # Mock a timeout exception.
    with pytest.raises(RuntimeError, match=r"Request to random\.org timed out\."):
        get_random()  # Expect RuntimeError due to timeout.


def test_fetch_random_number_invalid_response(mock_random_service):
    """Handle non-numeric response from random.org."""
    mock_random_service.text = "invalid_response"  # Set mock response to an invalid format.
    with pytest.raises(ValueError, match=r"Invalid response from random\.org: invalid_response"):
        get_random()  # Expect ValueError due to non-numeric response.

