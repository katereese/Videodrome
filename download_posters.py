from model import Media, session as dbsession
import urllib
import hashlib
import json
import omdb
import os

posterpath = '/Users/comunikates/HB/Exercises/Project/static/posters'
bad450md5sum = '0f61bf6d1829c92c4f5394bed991ebd4'

def download_from_OMDB(movie):
	# query API for poster file to download
	print "    fetching image for [%s]" % movie.title
	testfile = urllib.URLopener()
	testfile.retrieve("http://img.omdbapi.com/?apikey=e5b6d27b&i=%s&h=450" % movie.imdbID, "%s/%s_450.jpg" % (posterpath, movie.imdbID))

	# Skips movies with no poster image
	# Check md5 sum of the downloaded file, if it matches the 'no poster' image, abort
	file450 = posterpath + '/' + movie.imdbID + '_450.jpg'
	if match_hash_file(file450, bad450md5sum):
		movie.poster = False
		print "    no poster image: match hash"
		os.remove(file450) # delete 'no poster found' image
		return

	testfile.retrieve("http://img.omdbapi.com/?apikey=e5b6d27b&i=%s&h=95" % movie.imdbID, "%s/%s_95.jpg" % (posterpath, movie.imdbID))
	movie.poster = True
	print "    saving image [%s]" % movie.poster

def match_hash_file(path, md5sum):
	f = open(path, 'r')
	contents = f.read()
	hash = hashlib.md5()
	hash.update(contents)
	f.close()
	return hash.hexdigest() == md5sum;

def check_json_blob(movie):
	title = movie.title
	res = omdb.request(t=title, y=movie.year, r='JSON', apikey="e5b6d27b")
	
	# Parsing the http request into a map
	# Exception Handler: do this where you expect a failure
	try:
		json_content = json.loads(res.content)
	# do this if failure
	except: 
		print res.content
		return False

	kind = check_api_result(json_content, 'Type')
	if kind:
		movie.kind = kind

	## checks the JSON object for poster image link
	poster = check_api_result(json_content, 'Poster')
	if poster:
		return True
	else:
		movie.poster = False

	print "    no poster image in JSON object"
	return False

def check_api_result(json_content, field):
	if field in json_content and json_content[field] != 'N/A':
		return json_content[field]
	else:
		return None

def process_movie(movie):
	print "processing %s (%s)" % (movie.title, movie.year)
	if check_json_blob(movie):
		download_from_OMDB(movie)
	dbsession.add(movie)
	dbsession.commit()

# run import job
if __name__ == '__main__':
	while True:
		movie_list = dbsession.query(Media).filter(Media.imdbID!=None).filter(Media.poster==None).limit(10)
		for movie in movie_list:
			process_movie(movie)
