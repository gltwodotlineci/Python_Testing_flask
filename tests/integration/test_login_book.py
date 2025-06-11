from tests.unit.test_login_logout import club_email, patch_dt_club, \
    mock_current_user, client_and_data
from bs4 import BeautifulSoup


def test_login_book_place(club_email, patch_dt_club, mock_current_user):
    _, data = club_email
    mock_user, client, _ = mock_current_user

    with patch_dt_club("clb1", "20", "exmp@oc.fr",
                       "CompA", "2025-07-27 10:00:00", "15"):
        response = client.post('/show_summary', data=data)
        assert response.status_code == 302
        # make the get request of Welcome page
        response = client.get('/welcome')
    resp_decode = response.data.decode('utf-8')
    assert f'Points available: {mock_user.points}' in resp_decode
    assert b'Number of Places' in response.data

    # Get the booking page
    soup = BeautifulSoup(resp_decode, 'html.parser')
    book_url = soup.find_all('a')[1].get('href')
    with patch_dt_club("clb1", "20", "exmp@oc.fr",
                       "CompA", "2025-07-27 10:00:00", "15"):
        resp_booking = client.get(book_url)
    assert resp_booking.status_code == 200
    # Checking get in booking page
    assert "Places available: 15" in resp_booking.data.decode('utf-8')

    # booking:
    with patch_dt_club("clb1", "20", "exmp@oc.fr", "CompA",
                       "2025-07-27 10:00:00", "15") as (clubs, competitions):
        clb, compet = clubs[0], competitions[0]
        purchase_dt = {'club': clb['name'],
                       'competition': compet['name'], 'places': "2"}
        resp_pourchase = client.post('/purchase_places', data=purchase_dt)

    assert resp_pourchase.status_code == 200
    resp_pourchase = resp_pourchase.data.decode('utf-8')

    # Check if we have the new data on the page
    assert "Great-booking complete!" in resp_pourchase
    assert "Points available: 18" in resp_pourchase
    assert "CompA" in resp_pourchase
    assert "Date: 2025-07-27 10:00:00" in resp_pourchase
    assert "Number of Places: 13" in resp_pourchase
