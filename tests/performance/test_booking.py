# from server import app
# from tests.unit.test_login_logout import club_email


# def test_booking_benchmark(benchmark, club_email):
#     client, _ = club_email
#     club_name, comp_name, places = "Simply Lift", "Fall Classic", "places"
#     data = {'club': club_name,
#             'competition': comp_name,
#             'number': places}

#     def book():
#         return client.post('', data=data)
#     benchmark(book)
