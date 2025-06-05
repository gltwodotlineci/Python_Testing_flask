from flask import url_for
from bs4 import BeautifulSoup
from unittest.mock import patch
from contextlib import contextmanager
import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../')))
from server import app


@pytest.fixture
def client_and_data():
    """
    Fixture to create a test client for the Flask app.
    This allows us to make requests to the app without running a server.
    """
    data0 = {'places': '10',
             'competition': 'Competition A',
             'club': 'Club A'}
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client, data0


@pytest.fixture()
def club_email():
    """
    Fixture to provide user data for testing.
    """
    data = {'email': 'user@example.com'}
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client, data


@pytest.fixture()
def patch_competitions_and_clubs():
    """
    Fixture to patch the competitions and clubs loading functions.
    """
    @contextmanager
    def _patch(places, points, data_places=None):
        competitions = [{'name': 'Competition A', 'numberOfPlaces': places}]
        clubs = [{'name': 'Club A', 'points': points}]
        with patch('server.competitions', competitions), \
             patch('server.clubs', clubs):
            yield competitions, clubs
    return _patch


@pytest.fixture()
def patch_dt_club():
    @contextmanager
    def _patch(name, points, email):
        clubs = [{'name': name, 'points': points, 'email': email}]
        with patch('server.clubs', clubs):
            yield clubs
    return _patch


@pytest.fixture()
def patch_session():
    """
    Fixture to patch the session
    """
    @contextmanager
    def _patch(email, client):

        with client.session_transaction() as session:
            session['_user_id'] = email
            yield email, client

    return _patch


@pytest.mark.parametrize("places, points, data_places",
                         [(4, 10, None)])
def test_purchasePlaces_not_enough_places(client_and_data,
                                          patch_competitions_and_clubs,
                                          places,
                                          points,
                                          data_places):
    """
    Test the purchasePlaces route when there are not enough places available.
    """
    client, data = client_and_data
    with patch_competitions_and_clubs(places, points) as (competitions, clubs):
        response = client.post('/purchasePlaces', data=data)

    assert response.status_code == 200
    assert b'Sorry, not enough places available' in response.data


@pytest.mark.parametrize("places, points, data_places",
                         [(5, 10, '0.0'),
                          (5, 10, 'abc')])
def test_purchasePlaces_value_error(client_and_data,
                                    patch_competitions_and_clubs,
                                    places,
                                    points,
                                    data_places):
    """
    Test the purchasePlaces route when the input values are invalid.
    """
    client, data = client_and_data
    data['places'] = data_places

    with patch_competitions_and_clubs(places, points):
        response = client.post('/purchasePlaces', data=data)

    assert response.status_code == 200
    assert b"Invalid number of places given." in response.data


@pytest.mark.parametrize("places, points, data_places",
                         [(0, 10, None)])
def test_filled_competitions(client_and_data,
                             patch_competitions_and_clubs,
                             places,
                             points,
                             data_places):
    """
    Test the purchasePlaces route when the competition is already filled.
    """
    client, data = client_and_data
    with patch_competitions_and_clubs(places, points):
        response = client.post('/purchasePlaces', data=data)

    assert response.status_code == 200
    assert b'The competition you choosed is not avaiable anymore' \
        in response.data


@pytest.mark.parametrize("name, points, email",
                         [("Club A", "10", "clb1@example.com"),
                          ("Club B", "20", "clb2@example.com"),
                          ("Club C", "30", "clb3@example.com")])
def test_clubs_list(patch_dt_club, name, points, email):
    """
    Test the clubs_list route to ensure it returns the correct template.
    """
    with patch_dt_club(name, points, email):
        response = app.test_client().get('/clubs')
    response_html = response.data.decode('utf-8')
    resp_text = BeautifulSoup(response_html, 'html.parser').get_text()
    assert response.status_code == 200
    msg1 = f"{name}: {points} points."
    msg2 = f"Contact us at: {email}"
    print("Response text:", resp_text)
    assert msg1 in resp_text
    assert msg2 in resp_text


def refacto_return_index():
    """
    It will give re response if we redirect to index page.
    """
    with app.test_request_context():
        return url_for('index', _external=True)


if __name__ == '__main__':
    pytest.main()
