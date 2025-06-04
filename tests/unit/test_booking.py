from server import app
from unittest.mock import patch
from contextlib import contextmanager
import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../')))


@pytest.fixture()
def patch_club_user():
    """
    Fixture to patch Clubs and Competitions.
    """
    @contextmanager
    def _patch(name, points, email, name_comp, numberOfPlaces, login=False):
        clubs = [{'name': name, 'points': points, 'email': email}]
        competitions = [{'name': name_comp, 'numberOfPlaces': numberOfPlaces}]
        with patch('server.competitions', competitions), \
             patch('server.clubs', clubs):
            # with client.session_transaction() as session:
            #     session['_user_id'] = email
            yield clubs, competitions
    return _patch


# Sepparer le test en 2
@pytest.mark.parametrize(
        'name, points, email, name_comp, numberOfPlaces, login',
        [('Club A', 'clb1@example.com', "10", 'Competition A', "5", True),
         ('Club b', 'clb2@example.com', "11", 'Competition A', "3", False)])
def test_book(patch_club_user,
              name,
              points,
              email,
              name_comp,
              numberOfPlaces,
              login):
    """
    Test the book route to ensure it returns the correct template.
    Also testing if the post is executed if the user is logged in.
    """
    with patch_club_user(name, email, points, name_comp,
                         numberOfPlaces, login):
        with app.test_client() as client:
            if login:
                with client.session_transaction() as session:
                    session['_user_id'] = 'john@simplylift.co'

        response = client.get('/book/Competition A/Club A')

    msg2 = f"Places available: {numberOfPlaces}"
    if login:
        assert response.status_code == 200
        assert name_comp in response.data.decode('utf-8')
        assert msg2 in response.data.decode('utf-8')
    else:
        expected_url = "urls_str"
        assert response.status_code == 302
        assert response.location == expected_url
