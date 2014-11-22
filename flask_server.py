# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, flash, session
from model import User, Media, Rating, Genre, genres, session as dbsession
from sqlalchemy.orm import joinedload
import imdb
from urllib2 import Request, urlopen
import json
# import omdb

# at.config[ ] = 'https://api.themoviedb.org/3/movie/550?api_key=e8fd17b3d580a7a6a17856a6a7c522aa'

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)
app.secret_key ='bosco'


# @app.route("/api")
# headers = {
#   'Accept': 'application/json'
# }
# request = Request('http://api.themoviedb.org/3/configuration', headers=headers)

# response_body = urlopen(request).read()
# print response_body


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
	session["login"] = ""
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
	user = session["user"]
	ratings = dbsession.query(Rating).filter_by(user_id = user_id).all()
	return render_template("my_profile.html", user=user, ratings=ratings)

@app.route("/user_list")
def user_list(): 
	user_list = dbsession.query(User).limit(10).all()
	return render_template("user_list.html", users=user_list)

@app.route("/user_profile", methods=["GET"])
def user_search():
	#retrieve user input from user_list.html and set variable user to input
	user = request.args.get("id")
	if not user:
		return redirect("/user_list")

	#query database by user id
	user_info = dbsession.query(User).filter_by(id = user).first()
	if not user_info:
		# user wasn't found
		flash("This user does not exist. Please try again.")
		return redirect("/user_list")

	#fetch attribute for columns to pass to html page
	# username = user_info.username
	# first_name = user_info.first_name
	# last_name = user_info.last_name
	# ratings = user_info.ratings
	ratings = dbsession.query(Rating).options(joinedload('movie')).filter_by(user_id = user).all()
	avg_rating = average_rating(ratings)
	return render_template("<user_profile class=""></user_profile>html", user=user_info, ratings=ratings, avg_rating = avg_rating) #title=movie_info) #user_id=user, username=username, first_name=first_name, last_name=last_name, ratings=ratings)

@app.route("/wall")
def user_wall():
	# title - request.args.get("%title%")
	title = request.args.get("title")
	movies = None
	if title:
		# first try to find exact matches
		movies = dbsession.query(Media).filter_by(title = title).all()
		# fall back on matching parts of the string
		if not movies:
			movies = dbsession.query(Media).filter(Media.title.contains(title)).all()

		# filter out junk characters that break decoding with this error:
		# UnicodeDecodeError: 'utf8' codec can't decode byte 0xa2 in position 43: invalid start byte
		for movie in movies:
			newtitle = movie.title.decode('utf-8', 'ignore')
			if newtitle != movie.title:
				print "wtf media %d (%s)" % (movie.id, newtitle)
				movie.title = newtitle

	# add a rate these movies section at the bottom which lists movies in each genre the user has chosen	
	### FIXME COMMENTEDO UT  BY JOEL
	# user = session["user"]
	# genre_id = dbsession.query.genres.filter()

 #    movie_dict = {}
 #    for i in genre_list:
	# 	media = dbsession.query(Media).filter(Media.genres.any(Genre.id==i.id)).limit(5).all()
	# 	movie_dict[i] = media

	return render_template("wall.html", movies=movies)

	# gets the movie prof by calling OMDB API
	# @app.route("/movie_prof", methods=["GET", "POST"])
	# def movie_prof():
	#     #retrieve user input from main.html and set variable movie to movie title
	#     movie = request.args.get("movie")
		
	# 	# query API for move title using OMDb API parameters
	#     res = omdb.request(t=movie, r='JSON')
	#     json_content = json.loads(res.content)
	#     return render_template("movie_prof.html", movie=movie, json=json_content)

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
    # get a list of all genres



    genre_list = dbsession.query(Genre).all()

    # create a dictionary with each genre as key and movie list as an array of values
    movie_dict = {}
    for i in genre_list:
		# media = dbsession.query(Media).filter(Media.genres.any(Genre.id==i.id)).limit(5).all()

		## improved version from discussion w/joel:
		# more directly ask about genre_id in association table, so we don't have to
		# join 3 tables and do a (slow) "subquery" for the "any"
		#
		# SELECT * FROM Media JOIN MediaGenres ON ... JOIN Genre ON ... WHERE Genre.id IN 
		#     (SELECT ...)
		media = dbsession.query(Media).join(genres).filter_by(genre_id=i.id).limit(5).all()
		movie_dict[i] = media

		# for a in media:
		# 	print "******************", i.genre, a.title
		# 	for g in a.genres:
		# 		print g.genre

    return render_template("pick_genres.html", movie_list=movie_dict)

@app.route("/post_genres", methods=["POST"])
def post_genres():
	# get user and user genre picks from pick_genres.html
	# user = session["user"]
	
	# genre_ids_as_strings = request.form.getlist("genres")    -> ["1", "2", "3"]
	# genre_ids = []
	# for gi in genre_ids_as_strings:
	# 	genre_ids.append( int(gi) )

	genre_ids = [int(gi) for gi in request.form.getlist('genres')] # -> [1, 2, 3]

	# test print on genre id
	print "genre from form: %s" % genre_ids

	### DONT FORGET TO MAKE THIS A LOOP   -- JOEL

	# user_obj = dbsession.query(User).filter_by(id=user.id).first()
	for i in genre_ids:
		genre_ids.append(i)
		
	# genre_obj = dbsession.query(Genre).filter_by(id=genre_id).first()
		
	# joel = User(...)
	# dbsession.add(joel)

	# joel.middle_name = '...'
	# DON'T HAVE TO .add(joel)

	dbsession.commit()
	return redirect("/wall")


# # Takes a name in Surname, Firstname Morename The Third and returns
# # a human readable form
# def flip_name(name):
# 	parts = name.split(', ', 1)
# 	if len(parts) == 2:
# 		return '%s %s' % (parts[1], parts[0])
# 	else:
# 		return name

if __name__ == '__main__':
	# starts the built-in web server on port 5000
	app.run(debug = True)