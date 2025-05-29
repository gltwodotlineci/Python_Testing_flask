import json
from flask import Flask, render_template, request, redirect, flash, url_for


def loadClubs():
    with open('clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
        listOfCompetitions = json.load(comps)['competitions']
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form[
        'email']][0]
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
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


def refacto_booking_places(places_required, club, competition):
    """
    This function is a placeholder for refactoring the booking logic.
    It should handle the logic of booking places in a more structured way.
    """
    if places_required > int(club.get('points')):
        return 'Sorry, you do not have enough points to book this competition'
    elif places_required > int(competition.get('numberOfPlaces')):
        return 'Sorry, not enough places available'
    elif places_required < 1 or not places_required.is_integer():
        print("________________ ", places_required)
        return "Invalid number of places given."
    else:
        return None


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form[
        'competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    if not request.form['places'].isdigit():
        return render_template('booking.html',
                               club=club,
                               competition=competition,
                               message="Invalid number of places given.")
    placesRequired = int(request.form['places'])

    problem_booking = refacto_booking_places(placesRequired,
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

    flash('Great-booking complete!')
    return render_template('welcome.html',
                           club=club,
                           competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
