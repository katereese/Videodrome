from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Date, Float, Text, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import scoped_session

ENGINE = None
Session = None

# Create an instance of an engine that stores data in the local directory's
# sqlalchemy_example.db file. If Echo=True then Engine will log all statements 
# which is good for debugging.
engine = create_engine("sqlite:///movies.db", echo=False)
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
	Year = Column(Integer, nullable=False)
	Rated = Column(String(64), nullable=True)
	Released = Column(Date, nullable=True)
	Runtime = Column(Integer, nullable=True)
	Genre = Column(String(64), nullable=True)
	Director = Column(String(64), nullable=True)
	Writer = Column(String(64), nullable=True)
	Actors = Column(String(64), nullable=True)
	Plot = Column(Text, nullable=True)
	Language = Column(String(64), nullable=True)
	Country = Column(String(64), nullable=True)
	Awards = Column(String(64), nullable=True)
	Poster = Column(String(256), nullable=True)
	Metascore = Column(Float, nullable=True)
	imdbRating = Column(Float, nullable=True)
	imdbVotes = Column(Integer, nullable=True)
	imdbID = Column(String(64), nullable=True)
	Type = Column(String(64), nullable=True) ##movie or TV show?
	tomatoRating = Column(Integer, nullable=True)
	tomatoReviews = Column(Text, nullable=True)
	tomatoFresh = Column(String(64), nullable=True)
	tomatoRotten = Column(String(64), nullable=True)
	tomatoConsensus = Column(String(256), nullable=True)
	tomatoUserMeter = Column(Float, nullable=True)
	tomatoUserRating = Column(Integer, nullable=True)
	tomatoUserReviews = Column(Integer, nullable=True)
	BoxOffice = Column(Integer, nullable=True)
	Production = Column(Float, nullable=True)
	Website = Column(String(256), nullable=True)

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String(64), nullable=False)
	email = Column(String(64), nullable=False)
	password = Column(String(64), nullable=False)

class UserInfo(Base):
	__tablename__ = "users_info"
	# user_id references id column in users table ('table.column name')
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	first_name = Column(String(64), nullable=True)
	last_name = Column(String(64), nullable=True)
	age = Column(String(64), nullable=True)
	gender = Column(String(64), nullable=True)
	zipcode = Column(String(15), nullable=True)
	user = relationship("User", backref=backref("users_info", order_by=id))

class Rating(Base):
	__tablename__ = "ratings"

	id = Column(Integer, primary_key=True)
	movie_id = Column(Integer, ForeignKey('movies.id'))
	user_id = Column(Integer, ForeignKey('users.id'))
	rating = Column(Integer, nullable=True)
	user = relationship("User",backref=backref("ratings", order_by=id))
	movie = relationship("Movie",backref=backref("ratings", order_by=id))

### End class declarations

# function that connects to the ratings database and creates a cursor 
# (henceforward called "session")s
# def connect():
#     global ENGINE
#     global Session
#     ENGINE = create_engine("sqlite:///ratings.db", echo=True)
#     Session = sessionmaker(bind=ENGINE)

#     return session 

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
