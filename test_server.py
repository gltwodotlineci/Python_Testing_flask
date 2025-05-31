from server import app
from bs4 import BeautifulSoup
import pytest
from unittest.mock import patch
from contextlib import contextmanager


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
def patch_login_club():
    @contextmanager
    def _patch(email):
        club_email = {'email': email}
        with patch('server.clubs', club_email):
            yield club_email
        return _patch


@pytest.mark.parametrize("places, points, data_places",
                         [(5, 10, "2"),
                          (5, 10, None),
                          (4, 10, None),
                          (13, 13, "13")])
def test_purchasePlaces_cases(client_and_data,
                              patch_competitions_and_clubs,
                              places,
                              points,
                              data_places):
    """
    Test the purchasePlaces route with different cases of places and points.
    """
    client, data = client_and_data
    if data_places:
        data['places'] = data_places
    with patch_competitions_and_clubs(places, points) as (competitions, clubs):
        response = client.post('/purchasePlaces', data=data)
    if data_places == "2":
        assert response.status_code == 200
        assert b'Great-booking complete!' in response.data
    elif data_places == "13":
        assert response.status_code == 200
        assert b'Sorry, you can not book more than 12 places at once' \
            in response.data
    elif points < int(competitions[0]['numberOfPlaces']):
        assert response.status_code == 200
        msg = b"Sorry, you do not have enough points to book this competition"
        assert msg in response.data
    elif places > int(competitions[0]['numberOfPlaces']):
        assert response.status_code == 200
        assert b'Sorry, not enough places available' in response.data


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
                         [(5, 10, '0')])
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
    data2, data3 = data.copy(), data.copy()
    data2['places'] = 'abc'
    data3['places'] = '0.0'
    with patch_competitions_and_clubs(places, points) as (competitions, clubs):
        response = client.post('/purchasePlaces', data=data)
        response2 = client.post('/purchasePlaces', data=data2)
        response3 = client.post('/purchasePlaces', data=data3)

    assert response.status_code == 200
    assert b"Invalid number of places given." in response.data
    assert response2.status_code == 200
    assert b"Invalid number of places given." in response2.data
    assert response3.status_code == 200
    assert b"Invalid number of places given." in response3.data


@pytest.mark.parametrize("places, points, data_places",
                         [(0, 10, None)])
def test_filled_competitins(client_and_data,
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


@pytest.mark.parametrize("name, points, email",
                         [("Club A", "30", "wrong_user@example.com"),
                          ("Club B", "15", "user@example.com")
                          ])
def test_club_login(patch_dt_club, club_email, name, points, email):
    """
    Test the showSummary route to ensure it handles login correctly.
    """
    client, data = club_email
    given_email = data['email']
    with patch_dt_club(name, points, email):
        response = client.post('/showSummary', data=data)

    response_html = response.data.decode('utf-8')
    resp_text = BeautifulSoup(response_html, 'html.parser').get_text()

    if email != given_email:
        msg = "You should be redirected automatically to target URL: /."
        assert msg in resp_text
        assert response.status_code == 302
    else:
        assert f"Welcome, {email}" in resp_text
        assert f"Points available: {points}" in resp_text
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main()
