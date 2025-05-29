from server import app
import pytest
from unittest.mock import patch

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
def patch_data():
    """
    Fixture to patch the data for competitions and clubs.
    """
    competitions = [{'name': 'Competition A', 'numberOfPlaces': '5'}]
    clubs = [{'name': 'Club A', 'points': '10'}]
    with patch(
        'server.competitions', competitions), patch(
            'server.clubs', clubs):
        yield competitions, clubs


def test_purchasePlaces_success(client_and_data, patch_data):
    """
    Test the purchasePlaces route for successful booking.
    """
    client, data = client_and_data
    data['places'] = "2"
    response = client.post('/purchasePlaces', data=data)
    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data


def test_purchasePlaces_not_enough_places(client_and_data, patch_data):
    """
    Test the purchasePlaces route when there are not enough places available.
    """
    client, data = client_and_data
    response = client.post('/purchasePlaces', data=data)
    assert response.status_code == 200
    assert b'Sorry, not enough places available' in response.data


def test_purchasePlaces_not_enough_points(client_and_data, patch_data):
    """
    Test the purchasePlaces when the club does not have enough points.
    """
    client, data = client_and_data
    with patch('server.competitions',
               [{'name': 'Competition A', 'numberofPlaces': '20'}]), \
            patch('server.clubs', [{'name': 'Club A', 'points': '9'}]):
        response = client.post('/purchasePlaces', data=data)
    print("Response Data 2: ", response.data)
    assert response.status_code == 200
    assert b"Sorry, you do not have enough points to book this competition" \
        in response.data


def test_purchasePlaces_value_error(client_and_data, patch_data):
    """
    Test the purchasePlaces route when the input values are invalid.
    """
    client, data = client_and_data
    data2, data3 = data.copy(), data.copy()
    data['places'] = '0'
    data2['places'] = 'abc'
    data3['places'] = '0.0'

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
