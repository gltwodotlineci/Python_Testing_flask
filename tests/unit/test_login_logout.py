from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from server import app
import pytest


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
def patch_dt_club():
    """
    Patching clubs data
    """
    @contextmanager
    def _patch(name, points, email, name_comp, date, nb_pl):
        clubs = [{'name': name, 'points': points, 'email': email}]
        competitions = [{'name': name_comp,
                         'date': date, 'numberOfPlaces': nb_pl}]
        with patch('server.clubs', clubs), \
             patch('server.competitions', competitions):
            yield clubs, competitions
    return _patch


@pytest.fixture
def client_and_data():
    """
    Fixture to create a test client for the Flask app.
    Basicli it will allow us to make requests to the app
    without running a server.
    """
    club = {'name': 'clb1', 'email': 'admin@irontemple.com', 'points': 4}
    competions = [{'name': 'Comp A', "date": "2020-03-27 10:00:00",
                   'numberOfPlaces': 10}]
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client, club, competions


@pytest.fixture
def mock_current_user(client_and_data):
    client, club, competitions = client_and_data
    mock_user = MagicMock()
    mock_user.name = club['name']
    mock_user.email = club['email']
    mock_user.points = club['points']
    with patch('flask_login.utils._get_user', return_value=mock_user):
        yield mock_user, client, competitions


@pytest.fixture()
def patch_session():
    """
    Fixture to patch the session
    """
    @contextmanager
    def _patch(email, client):
        with client.session_transaction() as session:
            session['_user_id'] = email
            session['_fresh'] = True
            yield email, client

    return _patch


@pytest.mark.parametrize("name, points, email,\
                          redirect_url, name_comp, date, nb_pl",
                         [("Club A", "30", "wrong_user@example.com", "/",
                           "Comp1", "date1", 3),
                          ("Club B", "15", "user@example.com", "/welcome",
                           "comp2", "date2", 2)
                          ])
def test_club_login(patch_dt_club, club_email, name, points, email,
                    redirect_url, name_comp, date, nb_pl):
    """
    Test the show_summary route to ensure it handles login correctly.
    """
    client, data = club_email
    with patch_dt_club(name, points, email, name_comp, date, nb_pl):
        response = client.post('/show_summary', data=data)

    assert response.status_code == 302
    assert response.location.endswith(redirect_url)


def test_welcome(mock_current_user):
    mock_user, client, _ = mock_current_user

    response = client.get('/welcome')
    msg1 = f"Welcome, {mock_user.email}"
    msg2 = f"Points available: {mock_user.points}"
    assert response.status_code == 200
    assert msg1 in response.data.decode('utf-8')
    assert msg2 in response.data.decode('utf-8')


def test_logout(patch_session):
    """
    Test the logout route to ensure it redirects to the index page.
    """
    client = app.test_client()
    club_email = 'john@simplylift.co'
    with patch_session(club_email, client):
        response = client.get('/logout', follow_redirects=True)

    assert response.status_code == 200
    assert 'Welcome to the GUDLFT Registration Portal!' \
        in response.get_data(as_text=True)
