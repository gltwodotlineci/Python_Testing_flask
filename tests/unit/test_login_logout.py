from unittest.mock import patch
from contextlib import contextmanager
from server import app
import sys
import os
import pytest
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../')))


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


@pytest.mark.parametrize("name, points, email, expected_status",
                         [("Club A", "30", "wrong_user@example.com", 302),
                          ("Club B", "15", "user@example.com", 200)
                          ])
def test_club_login(patch_dt_club, club_email,
                    name, points, email, expected_status):
    """
    Test the showSummary route to ensure it handles login correctly.
    """
    client, data = club_email
    with patch_dt_club(name, points, email):
        response = client.post('/showSummary', data=data)

    assert response.status_code == expected_status
    if response.status_code == 302:
        assert response.location.endswith('/')
    else:
        assert b'Welcome, user@example.com' in response.data


def test_logout(patch_session):
    """
    Test the logout route to ensure it redirects to the index page.
    """
    client = app.test_client()
    club_email = 'expmp1@mail.com'
    with patch_session(club_email, client):
        response = client.get('/logout')

    assert response.status_code == 302
    # assert response.location.endswith('/')
