from flask import Flask, render_template, request, redirect, url_for
from datamanager.json_data_manager import JSONDatabaseManager

app = Flask(__name__)

# Initialize the JSONDatabaseManager
db_manager = JSONDatabaseManager('storage/users.json', 'storage/movies.json')


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/users')
def users_list():
    users = db_manager.get_all('users')
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = db_manager.get_by_id('users', user_id)
    if user:
        user_favorite_movies = [db_manager.get_by_id('movies', movie_id) for movie_id in user['favorite_movies']]
        return render_template('user_movies.html', user=user, movies=user_favorite_movies)
    return "User not found", 404


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
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
    user = db_manager.get_by_id('users', user_id)
    if not user:
        return "User not found", 404

    if request.method == 'POST':
        new_movie = {
            "title": request.form['title'],
            "genre": request.form['genre'],
            "year": int(request.form['year']),
            "director": request.form['director'],
            "rating": float(request.form['rating'])
        }
        added_movie = db_manager.add('movies', new_movie)
        user['favorite_movies'].append(added_movie['movie_id'])
        db_manager.update('users', user_id, user)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    user = db_manager.get_by_id('users', user_id)
    movie = db_manager.get_by_id('movies', movie_id)
    if not user or not movie:
        return "User or movie not found", 404

    if request.method == 'POST':
        movie['title'] = request.form['title']
        movie['genre'] = request.form['genre']
        movie['year'] = int(request.form['year'])
        movie['director'] = request.form['director']
        movie['rating'] = float(request.form['rating'])
        db_manager.update('movies', movie_id, movie)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('update_movie.html', user=user, movie=movie)


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    user = db_manager.get_by_id('users', user_id)
    movie = db_manager.get_by_id('movies', movie_id)
    if not user or not movie:
        return "User or movie not found", 404

    if request.method == 'POST':
        user['favorite_movies'].remove(movie_id)
        db_manager.update('users', user_id, user)
        db_manager.delete('movies', movie_id)
        return redirect(url_for('user_movies', user_id=user_id))
    return render_template('delete_movie.html', user=user, movie=movie)


if __name__ == '__main__':
    app.run(port=5002, debug=True)
