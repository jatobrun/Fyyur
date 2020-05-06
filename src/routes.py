#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from sqlalchemy.sql import func
import json
import dateutil.parser
import babel
from flask import (Flask, render_template, 
                  request, Response, flash,
                  redirect, url_for, abort, 
                  jsonify)
from flask_wtf import Form
from src.forms import *
import datetime
import sys
from sqlalchemy import desc
from src.models import Venue, Artist, Show
from src import app, db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
  return render_template('pages/home.html', artists = artists, venues = venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  data = []
  c = 0
  element = {}
  for row in Venue.query.order_by(Venue.state).all():
    if c == 0: 
      print('primer if')
      element = {'state':row.state,
                'city':row.city,
                'venues':[{'id': row.id, 'name':row.name,
                'num_shows': Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == row.id).count()         
               }]
      }
      print(data)
      c += 1
    elif element['city'] == row.city:
      element['venues'].append({'id': row.id, 'name': row.name,
      'num_shows': Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == row.id).count()
      })
    else:
      data.append(element)
      element = {}
      element = {'state':row.state,
                'city':row.city,
                'venues':[{'id': row.id, 'name':row.name,
                'num_shows': Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == row.id).count()         
               }]
      }
  data.append(element)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form['search_term']
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  current_time = datetime.datetime.now()

  sub_query = db.session.query(Show.venue_id, func.coalesce(func.count('*'), 0).label('num_upcoming_shows')). \
        filter(Show.date > current_time).group_by(Show.venue_id).subquery()

  result = db.session.query(Venue.id.label('id'), Venue.name.label('name'), sub_query.c.num_upcoming_shows). \
        outerjoin(sub_query, Venue.id == sub_query.c.venue_id).filter(Venue.name.ilike(f'%{search}%')).order_by(Venue.name)

  data = []
  for elem in result:
    data.append({"id": elem.id, "name": elem.name, "num_upcoming_shows": elem.num_upcoming_shows})

  response = {"count": result.count(), "data": data}

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  search = Venue.query.filter(Venue.id == venue_id).first()
  print(search)
  past_shows_count = Show.query.filter(Show.date < str(datetime.datetime.now())).filter(Show.venue_id == venue_id).count()
  upcoming_shows_count = Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == venue_id).count()
  data = {
    "id": search.id,
    "name": search.name,
    "genres": search.genres.split(','),
    "address": search.address,
    "city": search.city,
    "state": search.state,
    "phone": search.phone,
    "website": search.website,
    "facebook_link": search.facebook_link,
    "seeking_talent": search.seeking_talent,
    "image_link": search.image_link,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    "past_shows":[],
    'upcoming_shows':[]
  }
  if past_shows_count > 0:
    for show in Show.query.filter(Show.date < str(datetime.datetime.now())).filter(Show.venue_id == search.id):
      artist = Artist.query.filter(Artist.id == show.artist_id).first()
      element = {
        'artist_id': artist.id, 
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.date.strftime("%Y-%m-%d, %H:%M:%S")
        }
      data['past_shows'].append(element)
  
  if upcoming_shows_count > 0:
    for show in Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == search.id):
      artist = Artist.query.filter(Artist.id == show.artist_id).first()
      element = {
        'artist_id': artist.id, 
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.date.strftime("%Y-%m-%d, %H:%M:%S")
        }
      data['upcoming_shows'].append(element)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  error = False
  body = {}
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = ','.join(form.genres.data)
    website = form.website.data
    seeking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    venue = Venue(name = name, city = city, state = state, address = address, phone = phone, facebook_link = facebook_link, genres = genres, website= website, seeking_description = seeking_description, seeking_talent =seeking_talent, image_link = image_link)
    db.session.add(venue)
    db.session.commit()
    body['name'] = venue.name
    body['city'] = venue.city
    body['state'] = venue.state
    body['address'] = venue.address
    body['phone'] = venue.phone
    body['facebook_link'] = venue.facebook_link
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    print(body)
    return redirect(url_for('index'))


# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('venues'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  data = []
  for artist in Artist.query.all():
    element =  { 'id': artist.id, 'name': artist.name}
    data.append(element)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  search = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  count = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).count()
  response = {'count': count, 'data': []}
  for artist in search:
    element = {'id': artist.id, 'name': artist.name,
              'num_shows': Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.venue_id == artist.id).count()}
    response['data'].append(element)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  search = Artist.query.filter(Artist.id == artist_id).first()
  past_shows_count = Show.query.filter(Show.date < str(datetime.datetime.now())).filter(Show.artist_id == artist_id).count()
  upcoming_shows_count = Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.artist_id== artist_id).count()
  data = {
    "id": search.id,
    "name": search.name,
    "genres": search.genres.split(','),
    "city": search.city,
    "state": search.state,
    "phone": search.phone,
    "website": search.website,
    "facebook_link": search.facebook_link,
    "seeking_venue": search.seeking_venue,
    "seeking_description": search.seeking_description,
    "image_link": search.image_link,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    "past_shows":[],
    'upcoming_shows':[]
  }
  if past_shows_count > 0:
    for show in Show.query.filter(Show.date < str(datetime.datetime.now())).filter(Show.artist_id == search.id):
      venue = Venue.query.filter(Venue.id == show.venue_id).first()
      element = {
        'venue_id': venue.id, 
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.date.strftime("%Y-%m-%d, %H:%M:%S")
        }
      data['past_shows'].append(element)
  
  if upcoming_shows_count > 0:
    for show in Show.query.filter(Show.date > str(datetime.datetime.now())).filter(Show.artist_id == search.id):
      venue = Venue.query.filter(Venue.id == show.venue_id).first()
      element = {
        'venue_id': venue.id, 
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.date.strftime("%Y-%m-%d, %H:%M:%S")
        }
      data['upcoming_shows'].append(element)
  return render_template('pages/show_artist.html', artist= data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  artist = Artist.query.filter(Artist.id == artist_id).first()
  data={
    "id": artist.id,
    "name": artist.name,
    }
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.website.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = VenueForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = ','.join(form.genres.data)
    artist.website = form.website.data
    artist.seeking_talent = form.seeking_talent.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    db.session.commit()
    flash(f'Awesome, Your changes were update!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Thats too bad, Your changes were not update!. Try again')
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  data={
    "id": venue.id,
    "name": venue.name,
    }
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.website.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
    
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = ','.join(form.genres.data)
    venue.website = form.website.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    db.session.commit()
    flash(f'Awesome, Your changes were update!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash(f'Thats too bad, Your changes were not update!. Try again')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  error = False
  body = {}
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    phone = form.phone.data
    genres = ','.join(form.genres.data)
    website = form.website.data
    seeking_venue = form.seeking_venue.data
    seeking_description = form.seeking_description.data
    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    artist = Artist(name = name, city = city, state = state, phone = phone, facebook_link = facebook_link, genres = genres, website= website, seeking_description = seeking_description, seeking_venue =seeking_venue, image_link = image_link)
    db.session.add(artist)
    db.session.commit()
    body['name'] = artist.name
    body['city'] = artist.city
    body['state'] = artist.state
    body['phone'] = artist.phone
    body['facebook_link'] = artist.facebook_link
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    print(body)
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  data = []
  for show in Show.query.all():
    venue = Venue.query.filter(Venue.id == show.venue_id).first()
    artist = Artist.query.filter(Artist.id == show.artist_id).first()
    element =  {'artist_id': show.artist_id, "start_time": show.date.strftime("%Y-%m-%d, %H:%M:%S"), 'venue_id': show.venue_id, 'venue_name': venue.name, 'artist_name': artist.name, 'artist_image_link': artist.image_link}
    data.append(element)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  error = False
  body = {}
  try:
    date = form.start_time.data
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    show = Show(date = date, artist_id = artist_id, venue_id = venue_id)
    db.session.add(show)
    db.session.commit()
    body['date'] = show.date
    body['artist_id'] = show.artist_id
    body['venue_id'] = show.venue_id
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  if error:
    abort(400)
  else:
    print(body)
  
  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500



# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
