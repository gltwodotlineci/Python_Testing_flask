from server import app
import pytest
from unittest.mock import patch


def test_purchasePlaces_success():
    """
    Test the purchasePlaces route for successful booking."""
    client = app.test_client()
    client.testing = True

    data = {'places': '2',
            'competition': 'Competition A',
            'club': 'Club A'}
    with patch('server.competitions',
               [{'name': 'Competition A', 'numberOfPlaces': 5}]), \
            patch('server.clubs', [{'name': 'Club A', 'points': '10'}]):
        response = client.post('/purchasePlaces', data=data)
    assert response.status_code == 200
    assert b'Great-booking complete!' in response.data


def test_purchasePlaces_not_enough_places():
    """
    Test the purchasePlaces route when there are not enough places available.
    """
    client = app.test_client()
    client.testing = True

    data = {'places': '10',
            'competition': 'Competition A',
            'club': 'Club A'}
    with patch('server.competitions',
               [{'name': 'Competition A', 'numberOfPlaces': 5}]), \
            patch('server.clubs', [{'name': 'Club A', 'points': '10'}]):
        response = client.post('/purchasePlaces', data=data)
    assert response.status_code == 200
    assert b'Sorry, not enough places available' in response.data


def test_purchasePlaces_not_enough_points():
    """
    Test the purchasePlaces when the club does not have enough points.
    """
    client = app.test_client()
    client.testing = True

    data = {'places': '10',
            'competition': 'Competition A',
            'club': 'Club A'}
    with patch('server.competitions',
               [{'name': 'Competition A', 'numberofPlaces': '20'}]), \
            patch('server.clubs', [{'name': 'Club A', 'points': '9'}]):
        response = client.post('/purchasePlaces', data=data)
    print("Response Data 2: ", response.data)
    assert response.status_code == 200
    assert b"Sorry, you do not have enough points to book this competition" \
        in response.data


def test_purchasePlaces_value_error():
    """
    Test the purchasePlaces route when the input values are invalid.
    """
    client = app.test_client()
    client.testing = True

    data = {'places': '0',
            'competition': 'Competition A',
            'club': 'Club A'}
    data2, data3 = data.copy(), data.copy()
    data2['places'] = 'abc'
    data3['places'] = '0.0'
    with patch('server.competitions',
               [{'name': 'Competition A', 'numberOfPlaces': 5}]), \
            patch('server.clubs', [{'name': 'Club A', 'points': '10'}]):
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
