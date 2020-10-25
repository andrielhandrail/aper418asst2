from typing import List, Iterable
from datetime import datetime


class User:
    def __init__(
            self, username: str, password: str
    ):
        self._username: str = username
        self._password: str = password
        self._reviews: List[Review] = list()

    @property
    def username(self) -> str:
        return self._username

    @property
    def password(self) -> str:
        return self._password

    @property
    def reviews(self) -> Iterable['Review']:
        return iter(self._reviews)

    def add_comment(self, comment: 'Review'):
        self._reviews.append(comment)

    def __repr__(self) -> str:
        return f'<User {self._username} {self._password}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return other._username == self._username


class Movie:
    def __init__(self, title: str, year: int):
        if type(title) is not str or len(title) == 0:
            self._title = None
        else:
            self._title = title.strip()

        if type(year) is not int or year < 1900:
            self._year = None
        else:
            self._year = year

        self._description = None

        self._director = None

        self._actors = []

        self._genres = []

        self._runtime_minutes = None

        self._id = None

    @property
    def title(self):
        return self._title

    @property
    def year(self):
        return self._year

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, val):
        if type(val) is str:
            self._description = val.strip()

    @property
    def director(self):
        return self._director

    @director.setter
    def director(self, val):
        if type(val) is Director:
            self._director.remove_movie(self)
            self._director = val
            val.add_movie(self)

    @property
    def actors(self):
        return self._actors

    @actors.setter
    def actors(self, val):
        if type(val) is not list:
            return
        for actor in val:
            if type(actor) is not Actor:
                return
        self._actors = val
        for actor in val:
            actor.add_movie(self)  # doesnt account for setting actor list as new list

    def add_actor(self, val):
        if type(val) is Actor and val not in self._actors:
            self.actors.append(val)
            val.add_movie(self)

    def remove_actor(self, val):
        if type(val) is Actor:
            for i in range(len(self._actors) - 1):
                if self._actors[i] == val:
                    actor = self._actors.pop(i)
                    actor.remove_movie(self)

    @property
    def genres(self):
        return self._genres

    @genres.setter
    def genres(self, val):
        if type(val) is not list:
            return
        for genre in val:
            if type(genre) is not Genre:
                return
        self._genres = val

    def add_genre(self, val):
        if type(val) is Genre and val not in self._genres:
            self._genres.append(val)

    def remove_genre(self, val):
        if type(val) is Genre:
            for i in range(len(self._genres) - 1):
                if self._genres[i] == val:
                    self._genres.pop(i)

    @property
    def runtime_minutes(self):
        return self._runtime_minutes

    @runtime_minutes.setter
    def runtime_minutes(self, val):
        if type(val) is int:
            if val < 0:
                raise ValueError
            else:
                self._runtime_minutes = val

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        if type(val is int):
            self._runtime_minutes = val

    def __repr__(self):
        return f"<Movie {self._title}, {self._year}>"

    def __eq__(self, other):
        return self.title == other.title and self.year == other.year

    def __lt__(self, other):
        if self.title == other.title:
            return self.year < other.year
        else:
            return self.title < other.title

    def __hash__(self):
        return hash(tuple([self.title, self.year]))


class Director:
    def __init__(self, full_name: str):
        if len(full_name) == 0 or type(full_name) is not str:
            self._director_full_name = None
        else:
            self._director_full_name = full_name
        self._tagged_movies = []

    @property
    def director_full_name(self):
        return self._director_full_name

    def __repr__(self):
        return f"<Director {self._director_full_name}>"

    def __eq__(self, other):
        return self.director_full_name == other.director_full_name

    def __lt__(self, other):
        return self.director_full_name < other.director_full_name

    def __hash__(self):
        return hash(self._director_full_name)

    @property
    def tagged_movies(self):
        return self._tagged_movies

    def add_movie(self, movie: Movie):
        if movie not in self._tagged_movies:
            self._tagged_movies.append(movie)

    def remove_movie(self, movie: Movie):
        for i in range(len(self._tagged_movies)):
            if self._tagged_movies[i] == movie:
                return self._tagged_movies.pop(i)


class Genre:
    def __init__(self, genre: str):
        if len(genre) == 0 or type(genre) is not str:
            self._genre = None
        else:
            self._genre = genre

    @property
    def genre(self):
        return self._genre

    def __repr__(self):
        return f"<Genre {self._genre}>"

    def __eq__(self, other):
        return self.genre == other.genre

    def __lt__(self, other):
        return self.genre < other.genre

    def __hash__(self):
        return hash(self._genre)


class Actor:
    def __init__(self, actor: str):
        if type(actor) is not str or len(actor) == 0:
            self._actor = None
        else:
            self._actor = actor
        self._colleagues_list = []
        self._tagged_movies = []

    @property
    def actor(self):
        return self._actor

    def __repr__(self):
        return f"<Actor {self._actor}>"

    def __eq__(self, other):
        return self.actor == other.actor

    def __lt__(self, other):
        return self.actor < other.actor

    def __hash__(self):
        return hash(self._actor)

    def add_actor_colleague(self, colleague):
        self._colleagues_list.append(colleague)

    def check_if_this_actor_worked_with(self, colleague):
        for actor in self._colleagues_list:
            if actor == colleague:
                return True
        else:
            return False

    def add_movie(self, movie: Movie):
        if movie not in self._tagged_movies:
            self._tagged_movies.append(movie)

    def remove_movie(self, movie: Movie):
        for i in range(len(self._tagged_movies)):
            if self._tagged_movies[i] == movie:
                return self._tagged_movies.pop(i)


class Review:
    def __init__(self, movie: Movie, review_text: str, rating: int):
        if type(movie) is Movie:
            self._movie = movie
        else:
            self._movie = Movie("", 200)
        if type(review_text) is str and len(review_text) > 0:
            self._review_text = review_text.strip()
        else:
            self._review_text = ""
        if type(rating) is int and 0 < rating < 11:
            self._rating = rating
        else:
            self._rating = None
        self._timestamp = datetime.now()

    @property
    def movie(self):
        return self._movie

    @movie.setter
    def movie(self, val):
        if type(val) is Movie:
            self._movie = val
        else:
            self._movie = Movie("", 200)

    @property
    def review_text(self):
        return self._review_text

    @review_text.setter
    def review_text(self, val):
        if type(val) is str and len(val) > 0:
            self._review_text = val.strip()
            self._timestamp = datetime.now()
        self._review_text = None

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, val):
        if type(val) is int and 0 < val < 11:
            self._rating = val
        self._rating = None

    @property
    def timestamp(self):
        return self._timestamp

    def __repr__(self):
        return f"<Review: {self.review_text}>"

    def __eq__(self, other):
        return (self.movie == other.movie) and (self.review_text.lower() == other.review_text.lower()) and (
                    self.rating == other.rating) and (self.timestamp == other.timestamp)


def make_director_association():
    raise NotImplementedError


def make_actor_association():
    raise NotImplementedError


def make_review():
    raise NotImplementedError
