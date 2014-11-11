# import create_db 
import omdb
import json
from create_db import session, Movie

def main():

    ## query API for movie items, using OMDb API parameters:
    ## (https://pypi.python.org/pypi/omdb/0.2.0)

    res = omdb.request(t="Alive", r='JSON')
    # json_content is a dictionary
    json_content = json.loads(res.content)
    
    Title = json_content['Title']

    # create instance to check for movie in Movie table
    eachmovie = session.query(Movie).filter_by(movie_title=Title).all()

    print eachmovie

    if len(eachmovie) == 0:
    	eachmovie = Movie(
    					movie_title = json_content['Title'],
    					Year = json_content['Year'])
    	session.add(eachmovie)
	session.commit()
 


if __name__ == "__main__":
	main()