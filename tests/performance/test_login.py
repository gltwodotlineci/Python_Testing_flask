# from server import app
# from tests.unit.test_login_logout import club_email, mock_current_user, \
#     client_and_data, patch_session


# def test_login_benchmark(benchmark, club_email):
#     client, test_email = club_email

#     def login():
#         return client.post('/show_summary', data={'email': test_email})

#     benchmark(login)


# def test_welcome_benchmark(benchmark, mock_current_user):
#     _, client, _ = mock_current_user

#     def check_welcome():
#         return client.get('/welcome')

#     benchmark(check_welcome)


# def test_logout_benchmark(benchmark, patch_session):
#     client = app.test_client()
#     client_email = 'john@simplylift.co'

#     def logout_fc():
#         with patch_session(client_email, client):
#             response = client.get('/logout', follow_redirects=True)
#             assert response.status_code == 200
#             assert 'Welcome to the GUDLFT Registration Portal!' in\
#                 response.get_data(as_text=True)

#     benchmark(logout_fc)
