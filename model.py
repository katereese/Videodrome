from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session

ENGINE = None
Session = None

# Create an instance of an engine that stores data in the local directory's
# sqlalchemy_example.db file. If Echo=True then Engine will log all statements 
# which is good for debugging.
# mysql://root@localhost/movies
# 
engine = create_engine("sqlite:///movies2.db", echo=False)
session = scoped_session(sessionmaker(bind=engine,
                                      autocommit = False,
                                      autoflush = False))

# Base class definition. It is simply required for SQLALchemy's magic to work. 
Base = declarative_base()
Base.query = session.query_property()


# Setting up a Movies class that inherits the Base class.
class Movie(Base):
	# Informs SQLAlchemy that instances of this class will be stored in a table named users.
	__tablename__ = "movies"

	id = Column(Integer, primary_key=True)
	movie_title = Column(String(64), nullable=False)
	year = Column(Integer, nullable=True)
	rated = Column(String(64), nullable=True)
	released = Column(DateTime(10), nullable=True)
	runtime = Column(Integer, nullable=True)
	genre = Column(String(64), nullable=True)
	director = Column(String(64), nullable=True)
	writer = Column(String(64), nullable=True)
	actors = Column(String(64), nullable=True)
	plot = Column(Text, nullable=True)
	language = Column(String(64), nullable=True)
	country = Column(String(64), nullable=True)
	awards = Column(String(64), nullable=True)
	poster = Column(String(256), nullable=True)
	metascore = Column(Float, nullable=True)
	imdbRating = Column(Float, nullable=True)
	imdbVotes = Column(Integer, nullable=True)
	imdbID = Column(String(64), nullable=True)
	imdbtype = Column(String(64), nullable=True) ##movie or TV show?
	tomatoRating = Column(Integer, nullable=True)
	tomatoReviews = Column(Text, nullable=True)
	tomatoFresh = Column(String(64), nullable=True)
	tomatoRotten = Column(String(64), nullable=True)
	tomatoConsensus = Column(String(256), nullable=True)
	tomatoUserMeter = Column(Float, nullable=True)
	tomatoUserRating = Column(Integer, nullable=True)
	tomatoUserReviews = Column(Integer, nullable=True)
	boxOffice = Column(Integer, nullable=True)
	production = Column(Float, nullable=True)
	website = Column(String(256), nullable=True)

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False)
	email = Column(String(64), nullable=False)
	password = Column(String(64), nullable=False)
	first_name = Column(String(64), nullable=True)
	last_name = Column(String(64), nullable=True)
	age = Column(Integer, nullable=True)
	gender = Column(Integer, nullable=True)
	zipcode = Column(String(15), nullable=True)
	# user = relationship("User", backref=backref("users_info", order_by=id))

class Rating(Base):
	__tablename__ = "ratings"

	id = Column(Integer, primary_key=True)
	movie_id = Column(Integer, ForeignKey('movies.id'))
	user_id = Column(Integer, ForeignKey('users.id'))
	rating = Column(Integer, nullable=True)
	user = relationship("User",backref=backref("ratings", order_by=id))
	movie = relationship("Movie",backref=backref("ratings", order_by=id))

### End class declarations

def connect():
    global ENGINE
    global Session
    # mysql://root@localhost/movies
    ENGINE = create_engine("sqlite:///movies2.db", echo=True)
    Session = sessionmaker(bind=ENGINE)

    return session 

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
# Base.metadata.create_all(engine)