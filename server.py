import json
import uuid
from flask import Flask, render_template, request, redirect, flash, url_for
from flask import make_response
from flask_login import LoginManager, UserMixin, login_required
from flask_login import logout_user, login_user, current_user
from support_booking import write_json


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


def loadBookings():
    with open('booking_places.json') as book:
        listOfBookings = json.load(book)['booking_places']
        return listOfBookings


app = Flask(__name__)
app.secret_key = 'something_special'
login_manager = LoginManager()
login_manager.init_app(app)
# Set login view
login_manager.login_view = 'index'
# Add session protection
login_manager.session_protection = "strong"

competitions = loadCompetitions()
clubs = loadClubs()
bookings = loadBookings()


class ClubUser(UserMixin):
    def __init__(self, name, email, points):
        self.name = name
        self.email = email
        self.points = points

    def get_id(self):
        return self.email


class Competition:
    def __init__(self, name, numberOfPlaces, date):
        self.name = name
        self.numberOfPlaces = numberOfPlaces
        self.date = date

    def get_id(self):
        return self.name


class BookingEvents:
    def __init__(self, club_id, competition_id, places):
        self.id = str(uuid.uuid4())
        self.club_id = club_id
        self.competition_id = competition_id
        self.places = places

    def get_id(self):
        return self.id

    def serialize(self):
        return {
            'id': str(self.id),
            'club_id': self.club_id,
            'competition_id': self.competition_id,
            'places': self.places
        }


@login_manager.user_loader
def load_user(email):
    clubs = loadClubs()
    for club in clubs:
        if club['email'] == email:
            return ClubUser(club['name'], club['email'], club['points'])
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/clubs')
def clubs_list():
    return render_template('clubs.html', clubs=clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    if email not in (x['email'] for x in clubs):
        flash('Email not found, please try again')
        return redirect(url_for('index'))
    club = [club for club in clubs if club['email'] == request.form[
        'email']][0]

    club_user = ClubUser(club['name'], email, club['points'])
    login_user(club_user)
    return redirect(url_for('welcome'))


@app.route('/welcome')
@login_required
def welcome():

    club = {'name': current_user.name,
            'email': current_user.email,
            'points': current_user.points}
    response = make_response(render_template(
        'welcome.html', club=club, competitions=competitions))
    response.headers[
        'Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.route('/book/<competition>/<club>')
@login_required
def book(competition, club):
    # Add try except.
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',
                               club=foundClub,
                               competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html',
                               club=club,
                               competitions=competitions)


def value_validator(value):
    """
    Validates if the value is a positive integer.
    """
    try:
        value = int(value)
        if value < 1:
            return False
        return True
    except ValueError:
        return False


def process_booking(places_required, club, competition):
    """
    This function is a placeholder for refactoring the booking logic.
    It should handle the logic of booking places in a more structured way.
    """
    if places_required > int(club.get('points')):
        return 'Sorry, you do not have enough points to book this competition'
    elif int(competition.get('numberOfPlaces')) < 1:
        return 'The competition you chose is not available anymore'
    elif places_required > int(competition.get('numberOfPlaces')):
        return 'Sorry, not enough places available'
    elif check_booking_limit_club(club.get('email'),
                                  competition.get('name'),
                                  bookings, places_required) is False:
        return "You can not book more than 12 places for this competition"
    return None


def check_booking_limit_club(club_id, competition_id,
                             booking_places, places_required):
    """
    Check if the club in total can't reserve more than 12 places
    for a specific competition.
    """
    booked = [b.get('places') for b in booking_places
              if b['club_id'] == club_id and
              b['competition_id'] == competition_id]
    if sum(booked) + places_required > 12:
        return False
    return True


@app.route('/purchasePlaces', methods=['POST'])
@login_required
def purchasePlaces():
    places_required = request.form['places']
    if not value_validator(places_required):
        msg = "Invalid number of places given."
        return render_template('booking.html',
                               club=request.form['club'],
                               competition=request.form['competition'],
                               message=msg)
    competition = [c for c in competitions if c['name'] == request.form[
        'competition']][0]

    club = [c for c in clubs if c['name'] == request.form['club']][0]

    placesRequired = int(request.form['places'])
    problem_booking = process_booking(placesRequired,
                                      club,
                                      competition)
    if problem_booking:
        return render_template('booking.html',
                               club=club,
                               competition=competition,
                               message=problem_booking)

    club['points'] = int(club.get('points')) - placesRequired
    new_val_competition = int(competition['numberOfPlaces'])-placesRequired
    competition['numberOfPlaces'] = new_val_competition
    booking = BookingEvents(club['email'], competition['name'], placesRequired)
    bookings.append(booking.serialize())
    write_json('booking_places.json', bookings)

    flash('Great-booking complete!')
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
