import create_db 
import omdb
import json

def main():

    ## query API for movie items, using OMDb API parameters:
    ## (https://pypi.python.org/pypi/omdb/0.2.0)

    res = omdb.request(t='Alive', r='JSON')
    # json_content is a dictionary
    json_content = json.loads(res.content)

    # title = json_content["Title"]
    # year = json_content["Year"]

    # iterate over each item in the dictionary, assigning the keys to values in 
    # the table, and adding the specified fields
    for item in json_content:
    	eachmovie = create_db.Movie(
    					movie_title = json_content['Title'],
    					Year = json_content['Year'])
    	create_db.session.add(eachmovie)
	create_db.session.commit()
    

    print eachmovie


if __name__ == "__main__":
	main()