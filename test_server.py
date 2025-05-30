from server import app
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


if __name__ == '__main__':
    pytest.main()
