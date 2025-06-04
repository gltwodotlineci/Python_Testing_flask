import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from server import value_validator, process_booking
import pytest

# Messages as global variables for testing
msg1 = "Sorry, you do not have enough points to book this competition"
msg2 = "Sorry, not enough places available"
msg3 = "Sorry, you can not book more than 12 places at once"
msg4 = "The competition you chose is not available anymore"


@pytest.mark.parametrize("value, response",
                         [("1", True),
                          ("0", False),
                          ("-1", False),
                          ("abc", False),
                          ("5.5", False)])
def test_value_validator(value, response):
    """
    Test the value_validator function to ensure it correctly validates input.
    """
    assert value_validator(value) is response


@pytest.mark.parametrize("request_plc, points, exist_plc, message",
                         [(10, {'points': 9}, {'numberOfPlaces':12}, msg1),
                          (5, {'points': 5}, {'numberOfPlaces': 4}, msg2),
                          (13, {'points': 14}, {'numberOfPlaces': 13}, msg3),
                          (1, {'points': 1}, {'numberOfPlaces': 0}, msg4),
                          (1, {'points': 1}, {'numberOfPlaces': 1}, None)
                          ])
def test_process_booking(request_plc, points, exist_plc, message):
    """
    Helper function to process booking and return the expected message.
    """
    assert process_booking(request_plc, points, exist_plc) == message
