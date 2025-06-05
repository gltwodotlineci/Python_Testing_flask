import pytest
import sys
import os
from contextlib import contextmanager
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..')))
from server import value_validator, process_booking, check_booking_limit_club

# Messages as global variables for testing
msg1 = "Sorry, you do not have enough points to book this competition"
msg2 = "Sorry, not enough places available"
msg3 = "You can not book more than 12 places for this competition"
msg4 = "The competition you chose is not available anymore"


@pytest.fixture()
def patch_booging_dt():
    @contextmanager
    def _patch():
        """
        Fixture to patch the booking places data.
        """
        bookings = [
            {'id': '1',
             "club_id": 'c1@mail.fr',
             "competition_id": 'comp1@mail.fr',
             'places': 6},
            {'id': '2', "club_id":
             'c1@mail.fr', "competition_id":
             'comp2@mail.fr',
             'places': 2},
            {'id': '3',
             "club_id": 'c1@mail.fr',
             "competition_id": 'comp1@mail.fr',
             'places': 5},
             ]
        with patch('server.bookings', bookings):
            yield bookings

    return _patch


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
                         [(10, {'points': 9}, {'numberOfPlaces': 12}, msg1),
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


@pytest.mark.parametrize("club_id, competition_id, booking_places, response",
                         [('c1@mail.fr', 'comp1@mail.fr', 2, False),
                          ('c1@mail.fr', 'comp2@mail.fr', 1, True)])
def test_check_booking_limit_club(patch_booging_dt,
                                  club_id,
                                  competition_id,
                                  booking_places,
                                  response):
    """
    Test the check_booking_limit_club function to ensure it correctly checks
    the booking limit for a club.
    """
    with patch_booging_dt() as booking:
        # Test case where booking limit is not exceeded
        assert check_booking_limit_club(
            club_id, competition_id, booking, booking_places) is response
