from tests.unit.test_login_logout import club_email, patch_dt_club, \
    mock_current_user, client_and_data
from bs4 import BeautifulSoup
import pytest


msg_d = {'1': "Great-booking complete!",
         '2': "You can not book more than 12 places for this competition",
         '3': "Sorry, you do not have enough points to book this competition",
         '4': "Sorry, not enough places available",
         '5': "The competition you chose is not available anymore"}

@pytest.mark.parametrize("club_name, clb_pts, clb_email, \
                         comp_name, date, comp_plcs, places_req, msg",
                         [("clb1", "20", "exmp@oc.fr", "CompA",
                           "2020-03-27 10:00:00", "15", "2", msg_d['1']),
                          ("clb1", "20", "exmp@oc.fr", "CompA",
                           "2020-03-27 10:00:00", "15", "11", msg_d['2']),
                          ("clb1", "15", "exmp@oc.fr", "CompA",
                           "2020-03-27 10:00:00", "15", "16", msg_d['3']),
                          ("clb1", "6", "exmp@oc.fr", "CompA",
                           "2020-03-27 10:00:00", "2", "3", msg_d['4']),
                          ("clb1", "6", "exmp@oc.fr", "CompA",
                           "2020-03-27 10:00:00", "6", "6", msg_d['5'])
                           
                           ])
def test_login_book_place(club_email, patch_dt_club, mock_current_user,
                          club_name, clb_pts, clb_email, comp_name,
                          date, comp_plcs, places_req, msg):
    _, data = club_email
    mock_user, client, _ = mock_current_user

    with patch_dt_club(club_name, clb_pts, clb_email,
                       comp_name, date, comp_plcs):
        response = client.post('/showSummary', data=data)
        assert response.status_code == 302
        # make the get request of Welcome page
        response = client.get('/welcome')
        # booking page
    resp_decode = response.data.decode('utf-8')
    assert f'Points available: {mock_user.points}' in resp_decode

    # Get the booking page
    assert b'Number of Places' in response.data
    soup = BeautifulSoup(resp_decode, 'html.parser')
    book_url = soup.find_all('a')[1].get('href')

    with patch_dt_club(club_name, clb_pts, clb_email,
                       comp_name, date, comp_plcs):
        resp_booking = client.get(book_url)
    assert resp_booking.status_code == 200
    # Checking get in booking page
    assert f"Places available: {comp_plcs}" in \
        resp_booking.data.decode('utf-8')

    # booking:
    # Make an exception when competition has no places
    if msg == msg_d['5']:
        comp_plcs = "0"
    with patch_dt_club(club_name, clb_pts, clb_email, comp_name, date,
                       comp_plcs) as (clubs, competitions):
        clb, compet = clubs[0], competitions[0]

        purchase_dt = {'club': clb['name'],
                       'competition': compet['name'], 'places': places_req}
        resp_pourchase = client.post('/purchasePlaces', data=purchase_dt)

    assert resp_pourchase.status_code == 200
    resp_pourchase = resp_pourchase.data.decode('utf-8')
    # Check if we have the new data on the page
    assert msg in resp_pourchase
    if places_req == "2":
        assert f"Points available: {clb.get('points')}" in resp_pourchase
        assert comp_name in resp_pourchase
        assert f"Date: {date}" in resp_pourchase
        assert f"Number of Places: {compet['numberOfPlaces']}" \
            in resp_pourchase
