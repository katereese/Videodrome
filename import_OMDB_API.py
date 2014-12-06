# -*- coding: utf-8 -*-
import datetime
from model import Media, session as dbsession
import json
import omdb

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def import_from_OMDB():
	movie_list = dbsession.query(Media).filter_by(omdbLoad=None).limit(10)
	print ">>> Starting update"
	updated = 0
	for movie in movie_list:
		print "Updating... %d %s (%d)" % (movie.id, movie.title, movie.year)
		populate_movie_from_OMDB(movie)
		updated = updated + 1
	print ">>> Updated %d movies" % updated

# Takes a Media object as input and refreshes its data from the OMDB API
def populate_movie_from_OMDB(movie_info):
	# query API for move title using OMDB API parameters
	# Exception Handler: do this where you expect a failure
	title = movie_info.title #urllib.quote_plus(movie_info.title)
	res = omdb.request(t=title, y=movie_info.year, r='JSON', apikey="e5b6d27b", tomatoes="true")
	print "fetching [%s]" % title
 
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

# run import job
if __name__ == '__main__':
	while True:
		import_from_OMDB()