# -*- coding: utf-8 -*-
import collections
import datetime
from flask import Flask, render_template, redirect, request, flash, session
from model import User, Media, Rating, Genre, genres, session as dbsession
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, func
import json
import omdb
import urllib

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key ='bosco'

@app.route("/")
def index():
	return render_template("front.html")

@app.route("/login", methods=["POST"])  
def login():

	# fetch email and password from userinput client-side
	email = request.form.get("email")
	password = request.form.get("password")
	
	# check for user email and password in db
	u = dbsession.query(User).filter_by(email=email).filter_by(password=password).first()
   
	#if user is in db, add to session (cookie dictionary), if not redirect to login url
	if u:
		session["login"] = u.id
		session["user"] = u
		print session
		return redirect("/wall")      
	else:
		flash("User not recognized, please try again or signup")
		return redirect("/")

@app.route("/logout", methods=["GET", "POST"])
def logout():
	session.clear()
	print "logged out"
	return redirect("/") 

@app.route("/sign_up")
def sign_up():
	return render_template("sign_up.html")

@app.route("/sign_up", methods=["POST"])
def sign_up_form():
	## input new user row into database and redirect to wall page

	# fetch email, password, etc., from userinput client-side
	# add if request.form else redirect back to sign_up?
	email = request.form.get("email")
	password = request.form.get("password")
	username = request.form.get("username")
	first_name = request.form.get("first_name")
	last_name = request.form.get("last_name")
	gender = int(request.form.get("gender"))
	age = int(request.form.get("age"))
	zipcode = request.form.get("zipcode")
	
	# create an instance of User with email, password, username, etc. as attributes
	user = User(email=email, password=password, username=username, first_name=first_name, last_name=last_name, gender=gender, age=age, zipcode=zipcode)

	# check for email in db, if not there, add it to db
	if dbsession.query(User).filter_by(email = email).first():
		flash("This email address is already in use. Please try again.")
		return redirect("/sign_up")
	else:
		dbsession.add(user)
		dbsession.commit()
		created_user = dbsession.query(User).filter_by(email = email).first()
		session["login"] = created_user.id
		session["user"] = created_user
		return redirect("/pick_genres")
# need to create 'forgot your password' feature

@app.route("/my_profile")
def my_profile():
	# fetch user_id from the session dictionary of logged-in user
	user_id = session["login"]
	# query for a User class object filtering by its user_id column and the user_id variable,
	# stored in the session variable named login
	ratings = dbsession.query(Rating).filter_by(user_id = user_id).all()
	user = dbsession.query(User).options(joinedload('follows')).filter_by(id=user_id).first()
	return render_template("my_profile.html", user=user, ratings=ratings)

@app.route("/user_list")
def user_list(): 
	user_list = []
	user_ids = dbsession.query(Rating.user_id).group_by(Rating.user_id).order_by(desc(func.count(Rating.id))).limit(10).all()
	for u_id in user_ids:
		user = dbsession.query(User).filter_by(id = u_id[0]).first()
		user_list.append(user)
	return render_template("user_list.html", users=user_list)

@app.route("/user_search")
def user_search():
	print "search"
	#retrieve user input from user_list.html and set variable user to input
	email_input = request.args.get("email")
	if not email_input:
		return redirect("/user_list")

	#query database by user id
	user_info = dbsession.query(User).filter_by(email = email_input).first()
	if not user_info:
		# user wasn't found
		flash("This user does not exist. Please try again.")
		return redirect("/user_list")

	return redirect("/user_profile?id=%d" % user_info.id)

@app.route("/user_profile", methods=["GET"])
def user_profile():
	id = int(request.args.get("id"))
	user_info = dbsession.query(User).filter_by(id=id).first()
	ratings = dbsession.query(Rating).options(joinedload('movie')).filter_by(user_id = user_info.id).all()

	avg_rating = average_rating(ratings)
	return render_template("user_profile.html", user=user_info, ratings=ratings, avg_rating=avg_rating) #title=movie_info) #user_id=user, username=username, first_name=first_name, last_name=last_name, ratings=ratings)

@app.route("/follow_user", methods=["POST"])
def follow_user():
	loggedin_user_id = int(session["user"].id)
	followee_id = int(request.form.get('followee_id'))

	print "%d wants to follow %d" % (loggedin_user_id, followee_id)

	follow_obj = dbsession.query(User).get(followee_id)
	follower_obj = dbsession.query(User).get(loggedin_user_id)
	follower_obj.follows.append(follow_obj)
	dbsession.commit()
	return redirect("/my_profile")

@app.route("/wall")
def user_wall():
	title = request.args.get("title")
	movies = None
	if title:
		# first try to find exact matches
		movies = dbsession.query(Media).filter_by(title = title).all()
		# fall back on matching parts of the string
		if not movies:
			movies = dbsession.query(Media).filter(Media.title.contains(title)).all()
		
		fixtitle(movies)

	# add a rate these movies section at the bottom which lists movies in each genre the user has chosen	
	### FIXME COMMENTEDO UT  BY JOEL
	# user = session["user"]
	# genre_id = dbsession.query.genres.filter()
	genre_dict = {}
	if "user" in session:
		user = dbsession.query(User).options(joinedload('genres')).filter_by(id = session["user"].id).first()
		genre_dict = collections.OrderedDict()
		for i in user.genres:
			media = base_media_query().join(genres).filter_by(genre_id=i.id).limit(5).all()

			fixtitle(media)
			genre_dict[i] = media

	return render_template("wall.html", movies=movies, genres = genre_dict)

def base_media_query():
	return dbsession.query(Media).order_by(desc('tomatoMeter')).order_by(desc('imdbRating'))

# gets the movie prof by calling OMDB API
@app.route("/movie_prof_API", methods=["GET", "POST"])
def movie_prof_API():
	id = request.args.get("id")
	movie_info = dbsession.query(Media).get(id)
	if not movie_info:
		# movie not found
		redirect('/wall')
	populate_movie_from_OMDB(movie_info)
	return redirect("/movie_prof?id=%d" % movie_info.id)

@app.route("/import_from_OMDB")
def import_from_OMDB():
	movie_list = dbsession.query(Media).filter_by(omdbLoad=None).filter_by(language='English').limit(10)
	print ">>> Starting update"
	updated = 0
	for movie in movie_list:
		print "Updating... %d %s (%d)" % (movie.id, movie.title, movie.year)
		populate_movie_from_OMDB(movie)
		updated = updated + 1
	print ">>> Updated %d movies" % updated
	return redirect ("/import_from_OMDB")

# Takes a Media object as input and refreshes its data from the OMDB API
def populate_movie_from_OMDB(movie_info):
	# query API for move title using OMDB API parameters
	# Exception Handler: do this where you expect a failure
	res = omdb.request(t=urllib.quote_plus(movie_info.title), y=movie_info.year, r='JSON', apikey="e5b6d27b", tomatoes="true")
	try:
		json_content = json.loads(res.content)
	# do this if failure
	except: 
		print res.content
		return

	# updates a column with datetime stamp
	movie_info.omdbLoad = datetime.datetime.now()

	# fetch attributes of json content to pass to movie_info object
	poster = check_api_result(json_content, 'Poster')
	if poster:
		movie_info.poster = poster
	imdbRating = check_api_result(json_content, 'imdbRating')
	if imdbRating:
		movie_info.imdbRating = float(imdbRating)
	imdbID = check_api_result(json_content, 'imdbID')
	if imdbID:
		movie_info.imdbID = imdbID
		movie_info.imdbURL = "http://www.imdb.com/title/%s" % imdbID
	runtime = check_api_result(json_content, 'Runtime')
	if runtime:
		movie_info.runtime = runtime.replace(' min', '')
	director = check_api_result(json_content, 'Director')
	if director:
		movie_info.director = director
	actors = check_api_result(json_content, 'Actors')
	if actors:
		movie_info.actors = actors
	tomatoMeter = check_api_result(json_content, 'tomatoMeter')
	if tomatoMeter:
		movie_info.tomatoMeter = int(tomatoMeter)
	tomatoUserRating = check_api_result(json_content, 'tomatoUserRating')
	if tomatoUserRating:
		movie_info.tomatoUserRating = float(tomatoUserRating)
	tomatoUserMeter = check_api_result(json_content, 'tomatoUserMeter')
	if tomatoUserMeter:
		movie_info.tomatoUserMeter = int(tomatoUserMeter)
	mpaa_rating = check_api_result(json_content, 'Rated')
	if mpaa_rating:
		movie_info.mpaa_rating = mpaa_rating
	metascore = check_api_result(json_content, 'Metascore')
	if metascore:
		movie_info.metascore = int(metascore)
	shortPlot = check_api_result(json_content, 'Plot')
	if shortPlot:
		movie_info.shortPlot = shortPlot

	dbsession.add(movie_info)
	dbsession.commit()

def check_api_result(json_content, field):
	if field in json_content and json_content[field] != 'N/A':
		return json_content[field]
	else:
		return None

@app.route("/genre_prof", methods=["GET"])
def genre_profile():
	id = int(request.args.get("id"))
	if not id:
		return redirect("/wall")

	genre = dbsession.query(Genre).get(id)
	media = base_media_query().join(genres).filter_by(genre_id=id).limit(100).all()
	fixtitle(media)
	return render_template("genre_prof.html", media = media, genre = genre)

@app.route("/movie_prof", methods=["GET"])
def movie_profile():
	id = request.args.get("id")
	if not id:
		return redirect("/wall")

	movie_info = dbsession.query(Media).get(id)
	if not movie_info:
		# movie wasn't found
		flash("This movie does not exist. Please try again.")
		return redirect("/wall")

	# FIXME: fix this workaround for utf-8 decoding weirdness in flask/jinja
	if movie_info.director:
		movie_info.director = movie_info.director.decode('utf-8', 'ignore')
	if movie_info.actors:
		movie_info.actors = movie_info.actors.decode('utf-8', 'ignore')
	if movie_info.plot:
		movie_info.plot = movie_info.plot.decode('utf-8', 'ignore')

	ratings = dbsession.query(Rating).options(joinedload('user')).filter_by(movie_id = id).all()
	avg_rating = average_rating(ratings)

	return render_template("movie_prof.html", movie=movie_info, ratings=ratings, avg_rating = avg_rating)

@app.route("/add_rating", methods=["POST"])
def add_rating():
	#get movie from search in movie_prof.html
	movie_id = int(request.form.get("id"))
	user_id = int(session["user"].id)
	score = int(request.form.get("rating"))
	review = request.form.get("movie_review")
	print review

	rating = dbsession.query(Rating).filter_by(user_id = user_id, movie_id=movie_id).first()
	if not rating:
		# add new rating
		rating = Rating(movie_id = movie_id, user_id = user_id, rating = score, review = review)
	else:
		# update existing rating
		rating.rating = score
		rating.review = review

	dbsession.add(rating)
	dbsession.commit()

	## flash message that it's been added?
	return redirect("/movie_prof?id=%d" % movie_id)

@app.route("/movie_list")
def movie_list():
	movie_list = dbsession.query(Media).limit(20).all()
	return render_template("movie_list.html", movies=movie_list)

def average_rating(ratings):
	if len(ratings) == 0:
		return 0.0

	sum = 0
	for r in ratings:
		sum = sum + r.rating
	return float("{0:.1f}".format(float(sum) / len(ratings)))

@app.route("/pick_genres")
def pick_genres():
	# get loggin in user id
	user_id = int(session["user"].id)
	# get a list of all genres
	genre_list = dbsession.query(Genre).all()
	# Load current user and all her/his/it genre selections
	user = dbsession.query(User).options(joinedload('genres')).filter_by(id = user_id).first()
	
	# create a dictionary with each genre as key and movie list as an array of values
	movie_dict = collections.OrderedDict()
	for i in genre_list:
		media = base_media_query().join(genres).filter_by(genre_id=i.id).limit(5).all()
		fixtitle(media)
		movie_dict[i] = media

		## Bad: media = dbsession.query(Media).filter(Media.genres.any(Genre.id==i.id)).limit(5).all()
		## improved version from discussion w/joel:
		# more directly ask about genre_id in association table, so we don't have to
		# join 3 tables and do a (slow) "subquery" for the "any"

	return render_template("pick_genres.html", movie_list=movie_dict, user=user)

@app.route("/post_genres", methods=["POST"])
def post_genres():
	# get logged in user and user genre picks from pick_genres.html
	user_obj = get_current_user()
	for g in user_obj.genres:
		user_obj.genres.remove(g)
	dbsession.commit()

	# genre_ids_as_strings = request.form.getlist("genres")    -> ["1", "2", "3"]
	# genre_ids = []
	# for gi in genre_ids_as_strings:
	# 	genre_ids.append( int(gi) )

	genre_ids = [int(gi) for gi in request.form.getlist('genres')] # -> [1, 2, 3]

	for gi in genre_ids:
		genre_obj = dbsession.query(Genre).filter_by(id=gi).first()
		user_obj.genres.append(genre_obj)

	dbsession.commit()
	return redirect("/wall")

def get_current_user():
	if "user" in session:
		return dbsession.query(User).filter_by(id = session["user"].id).first()
	else:
		return None

# filter out junk characters that break decoding with this error:
# UnicodeDecodeError: 'utf8' codec can't decode byte 0xa2 in position 43: invalid start byte
def fixtitle(movies):
	for movie in movies:
		newtitle = movie.title.decode('utf-8', 'ignore')
		if newtitle != movie.title:
			print "wtf media %d (%s)" % (movie.id, newtitle)
			movie.title = newtitle

if __name__ == '__main__':
	# starts the built-in web server on port 5000
	app.run(debug = True)