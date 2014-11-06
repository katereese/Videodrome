from flask import Flask, render_template, redirect, request, flash, session
from create_db import User, session as dbsession 
# need to go back and add Movie, Rating
import omdb
import json
# import jinja2


app = Flask(__name__)
app.secret_key ='bosco'

# @app.route("/")
# def index():
# 	user_list = create_db.session.query(create_db.User).all()
# 	return render_template("user_list.html", users=user_list)
# 	return "HIIIIII"

@app.route("/")
def index():
	return render_template("front.html")

@app.route("/login", methods=['POST'])
def login():

	# fetch email and password from userinput client-side
    email = request.form.get("email")
    password = request.form.get("password")
    
    # check for user email and password in db
    u = dbsession.query(User).filter_by(email=email).filter_by(password=password).first()
   
    #if user is in db, add to session (cookie dictionary), if not redirect to login url
    if u:
        session["login"] = u.id
        print session
        return redirect("/wall")      
    else:
        flash("User not recognized, please try again or signup.")
        return redirect("/")

@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")

@app.route("/sign_up_form", methods=["POST"])
def sign_up_form():
	# input new user row into database and redirect to wall page

	# fetch email and password from userinput client-side
    ## if request.form else redirect back to sign_up

    email = request.form.get("email")
    password = request.form.get("password")
    username = request.form.get("username")
    
    # create an instance of user with email, password and username as attributes
    user = User(email=email, password=password, username=username)

	# check for email in db, if not there, add it to db
    if dbsession.query(User).filter_by(email = email).first():
		flash("This email address is already in use. Please try again.")
		return redirect("/sign_up")
    else:
 		dbsession.add(user)
 		dbsession.commit()
 		return redirect("/wall")

# need to create 'forgot your password' feauture

@app.route("/wall")
def user_wall():
	return render_template("wall.html")

@app.route("/movie_prof", methods=["GET"])
def movie_prof():
    #retrieve user input from main.html and set variable movie to movie title
    movie = request.args.get("movie")
	
	# query API for move title
    # using OMDb API parameters
    res = omdb.request(t=movie, r='JSON')
    xml_content = json.loads(res.content)

    return render_template("movie_prof.html", movie=movie, json=xml_content)

    # #query database by movie title
    # movie_info = dbsession.query(Movie).filter_by(name = movie).first()
    # #fetch attribute for release date
    # released_at = movie_info.released_at
    # #fetch attribute for imdb_url
    # imdb_url = movie_info.imdb_url
    # #fetch attribute for ratings
    # ratings = movie_info.ratings

    # print session

    # return render_template("movie_info.html", ratings = ratings, movie = movie, release_date = released_at, imdb_url = imdb_url)

# @app.route("/movie_prof")
# def movie_prof():

#     movie_list = create_db.session.query(create_db.Movie).all()
#     # add limit later
#     # movie_list = create_db.session.query(reate_db.User).limit(20).all()
#     movie_dict = {'movies': []}

    # for item in movie_list:
    #     # movie_dict[str(user.id)] = "name"
    #     movie_dict['movies'].append(movie.id)

    # print movie_dict
    # return jsonify(**movie_dict)

if __name__ == '__main__':
	# starts the built-in web server on port 5000
	app.run(debug = True)