from flask import Flask, render_template, request, redirect, url_for
import requests
from datamanager.json_data_manager import JSONDatabaseManager

app = Flask(__name__)

# Initialize the JSONDatabaseManager
db_manager = JSONDatabaseManager('storage/users.json', 'storage/movies.json')

OMDB_API_KEY = 'bde1b2d6'  # Replace with your actual OMDb API key


def fetch_movie_details(title):
    """Fetch movie details from OMDb API."""
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


def parse_year(year_string):
    """Parse the year string to extract the starting year."""
    try:
        # Attempt to convert the first four characters of the year string to an integer
        return int(year_string[:4])
    except ValueError:
        # Return None if parsing fails
        return None


# Routes
@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@app.route('/users')
def users_list():
    """Render the users list page."""
    users = db_manager.get_all('users')
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Render the user movies page."""
    user = db_manager.get_by_id('users', user_id)
    if user:
        user_favorite_movies = [db_manager.get_by_id('movies', movie_id) for movie_id in user['favorite_movies']]
        user_favorite_movies = [movie for movie in user_favorite_movies if movie is not None]  # Filter out None values
        return render_template('user_movies.html', user=user, movies=user_favorite_movies)
    return render_template('error.html', message="User not found"), 404


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Render the add user page and handle user creation."""
    if request.method == 'POST':
        new_user = {
            "username": request.form['username'],
            "email": request.form['email'],
            "favorite_movies": []
        }
        db_manager.add('users', new_user)
        return redirect(url_for('users_list'))
    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Render the add movie page and handle movie creation."""
    user = db_manager.get_by_id('users', user_id)
    if not user:
        return render_template('error.html', message="User not found"), 404

    if request.method == 'POST':
        title = request.form['title']
        movie_details = fetch_movie_details(title)

        if not movie_details or movie_details['Response'] == 'False':
            return render_template('error.html', message="Movie not found in OMDb"), 404

        new_movie = {
            "title": movie_details['Title'],
            "genre": movie_details['Genre'],
            "year": parse_year(movie_details['Year']),
            "director": movie_details['Director'],
            "rating": float(movie_details['imdbRating']) if movie_details['imdbRating'] != 'N/A' else None,
            "image_url": movie_details['Poster']
        }

        added_movie = db_manager.add('movies', new_movie)
        user['favorite_movies'].append(added_movie['movie_id'])
        db_manager.update('users', user_id, user)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Render the update movie page and handle movie update."""
    user = db_manager.get_by_id('users', user_id)
    movie = db_manager.get_by_id('movies', movie_id)
    if not user or not movie:
        return render_template('error.html', message="User or movie not found"), 404

    if request.method == 'POST':
        try:
            movie['title'] = request.form['title']
            movie['genre'] = request.form['genre']
            movie['year'] = int(request.form['year'])
            movie['director'] = request.form['director']
            movie['rating'] = float(request.form['rating'])
            movie['image_url'] = request.form['image_url']
            db_manager.update('movies', movie_id, movie)
            return redirect(url_for('user_movies', user_id=user_id))
        except ValueError as e:
            return render_template('error.html', message=f"Error updating movie: {str(e)}"), 400
    return render_template('update_movie.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """Render the delete movie page and handle movie deletion."""
    user = db_manager.get_by_id('users', user_id)
    movie = db_manager.get_by_id('movies', movie_id)
    if not user or not movie:
        return render_template('error.html', message="User or movie not found"), 404

    if request.method == 'POST':
        user['favorite_movies'].remove(movie_id)
        db_manager.update('users', user_id, user)
        db_manager.delete('movies', movie_id)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('delete_movie.html', user=user, movie=movie)


if __name__ == '__main__':
    app.run(port=5002, debug=True)
