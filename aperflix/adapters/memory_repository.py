import csv
import os
from datetime import date, datetime
from typing import List

from bisect import bisect, bisect_left, insort_left

from werkzeug.security import generate_password_hash

from aperflix.adapters.repository import AbstractRepository, RepositoryException
from aperflix.domain.model import Movie, User, Review, make_director_association, make_actor_association, make_review, \
    Director, Actor


class MemoryRepository(AbstractRepository):
    # movies ordered by date, not id. id is assumed unique.

    def __init__(self):
        self._movies = list()
        self._movies_index = dict()
        self._directors = list()
        self._actors = list()
        self._users = list()
        self._reviews = list()

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def add_movie(self, movie: Movie):
        insort_left(self._movies, movie)
        self._movies_index[movie.id] = movie

    def get_movie(self, i: int) -> Movie:
        movie = None

        try:
            movie = self._movies_index[i]
        except KeyError:
            pass  # Ignore exception and return None.

        return movie

    def get_movies_by_year(self, target_year: int) -> List[Movie]:
        target_movie = Movie(
            title="",
            year=target_year
        )
        matching_movies = list()

        try:
            index = self.movie_index(target_movie)
            for movie in self._movies[index:None]:
                if movie.year == target_year:
                    matching_movies.append(movie)
                else:
                    break
        except ValueError:
            # No movies for specified date. Simply return an empty list.
            pass

        return matching_movies

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[0]
        return movie

    def get_last_movie(self):
        movie = None

        if len(self._movies) > 0:
            movie = self._movies[-1]
        return movie

    def get_movies_by_id(self, id_list):
        # Strip out any ids in id_list that don't represent movie ids in the repository.
        existing_ids = [i for i in id_list if i in self._movies_index]

        # Fetch the movies.
        movies = [self._movies_index[i] for i in existing_ids]
        return movies

    def get_movie_ids_for_director(self, director_name: str):
        # Linear search, to find the first occurrence of a Director with the name director_name.
        director = next((director for director in self._directors if director.director_name == director_name), None)

        # Retrieve the ids of movies associated with the Director.
        if director is not None:
            movie_ids = [movie.id for movie in director.tagged_movies]
        else:
            # No Director with name director_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_movie_ids_for_actor(self, actor_name: str):
        # Linear search, to find the first occurrence of a Director with the name director_name.
        actor = next((actor for actor in self._actors if actor.actor_name == actor_name), None)

        # Retrieve the ids of movies associated with the Director.
        if actor is not None:
            movie_ids = [movie.id for movie in actor.tagged_movies]
        else:
            # No Director with name director_name, so return an empty list.
            movie_ids = list()

        return movie_ids

    def get_year_of_previous_movie(self, movie: Movie):
        previous_year = None

        try:
            index = self.movie_index(movie)
            for stored_movie in reversed(self._movies[0:index]):
                if stored_movie.year < movie.year:
                    previous_year = stored_movie.year
                    break
        except ValueError:
            # No earlier movies, so return None.
            pass

        return previous_year

    def get_year_of_next_movie(self, movie: Movie):
        next_year = None

        try:
            index = self.movie_index(movie)
            for stored_movie in self._movies[index + 1:len(self._movies)]:
                if stored_movie.year > movie.year:
                    next_year = stored_movie.year
                    break
        except ValueError:
            # No subsequent movies, so return None.
            pass

        return next_year

    def add_director(self, director: Director):
        self._directors.append(director)

    def get_directors(self) -> List[Director]:
        return self._directors

    def add_review(self, review: Review):
        super().add_review(review)
        self._reviews.append(review)

    def get_reviews(self):
        return self._reviews

    # Helper method to return movie index.
    def movie_index(self, movie: Movie):
        index = bisect_left(self._movies, movie)
        if index != len(self._movies) and self._movies[index].year == movie.year:
            return index
        raise ValueError


def read_csv_file(filename: str):
    with open(filename, encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]
            yield row


def load_movies(data_path: str, repo: MemoryRepository):
    directors = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'movies.csv')):

        movie_key = int(data_row[0])
        movie_director = data_row[4]
        movie_genres = data_row[2].split(sep=",")
        movie_actors = data_row[5].split(sep=",")

        # Add any new directors; associate the current movie with directors.
        if movie_director not in directors.keys():
            directors[movie_director] = list()
        directors[movie_director].append(movie_key)

        # Create movie object.
        movie = Movie(
            title=data_row[1],
            year=int(data_row[6])
        )
        movie.id(int(data_row[0]))
        movie.description(data_row[3])

        # Add the movie to the repository.
        repo.add_movie(movie)

    # Create Director objects, associate them with movies and add them to the repository.
    for director_name in directors.keys():
        director = Director(director_name)
        for movie_id in directors[director_name]:
            movie = repo.get_movie(movie_id)
            make_director_association(movie, director)
        repo.add_director(director)


def load_users(data_path: str, repo: MemoryRepository):
    users = dict()

    for data_row in read_csv_file(os.path.join(data_path, 'users.csv')):
        user = User(
            username=data_row[1],
            password=generate_password_hash(data_row[2])
        )
        repo.add_user(user)
        users[data_row[0]] = user
    return users


def load_reviews(data_path: str, repo: MemoryRepository, users):
    for data_row in read_csv_file(os.path.join(data_path, 'reviews.csv')):
        review = make_review(
            review_text=data_row[3],
            user=users[data_row[1]],
            movie=repo.get_movie(int(data_row[2])),
            timestamp=datetime.fromisoformat(data_row[4])
        )
        repo.add_review(review)


def populate(data_path: str, repo: MemoryRepository):
    # Load movies and directors into the repository.
    load_movies_and_directors(data_path, repo)

    # Load users into the repository.
    users = load_users(data_path, repo)

    # Load reviews into the repository.
    load_reviews(data_path, repo, users)
