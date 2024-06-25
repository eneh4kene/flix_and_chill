import json
from typing import Dict, List
from data_manager_interface import DatabaseManagerInterface


class JSONDatabaseManager(DatabaseManagerInterface):
    def __init__(self, users_file: str, movies_file: str):
        self.users_file = users_file
        self.movies_file = movies_file
        self.users = []
        self.movies = []
        self.load_data()

    def load_data(self):
        with open(self.users_file, 'r') as f:
            self.users = json.load(f)
        with open(self.movies_file, 'r') as f:
            self.movies = json.load(f)

    def save_data(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)
        with open(self.movies_file, 'w') as f:
            json.dump(self.movies, f, indent=4)

    def get_all(self, entity: str) -> List[Dict]:
        if entity == 'users':
            return self.users
        elif entity == 'movies':
            return self.movies
        else:
            raise ValueError("Unknown entity type")

    def get_by_id(self, entity: str, id: int) -> Dict:
        collection = self.get_all(entity)
        for item in collection:
            if item['user_id' if entity == 'users' else 'movie_id'] == id:
                return item
        return None

    def add(self, entity: str, data: Dict) -> Dict:
        collection = self.get_all(entity)
        if entity == 'users':
            data['user_id'] = max([user['user_id'] for user in self.users], default=0) + 1
        elif entity == 'movies':
            data['movie_id'] = max([movie['movie_id'] for movie in self.movies], default=0) + 1
        else:
            raise ValueError("Unknown entity type")
        collection.append(data)
        self.save_data()
        return data

    def update(self, entity: str, id: int, data: Dict) -> Dict:
        collection = self.get_all(entity)
        for index, item in enumerate(collection):
            if item['user_id' if entity == 'users' else 'movie_id'] == id:
                collection[index].update(data)
                self.save_data()
                return collection[index]
        return None

    def delete(self, entity: str, id: int) -> Dict:
        collection = self.get_all(entity)
        for index, item in enumerate(collection):
            if item['user_id' if entity == 'users' else 'movie_id'] == id:
                deleted_item = collection.pop(index)
                self.save_data()
                return deleted_item
        return None


def main():
    my_movie = JSONDatabaseManager('../flix_and_chill/storage/users.json', '../flix_and_chill/storage/movies.json')
    all_users = my_movie.get_all('users')

    # user_2 = my_movie.get_by_id('movies', 102)
    # print(user_2)
    #
    # new_data = {
    #       "user_id": 2,
    #       "username": "jane_morgan",
    #       "email": "jane_morgan@example.com",
    #       "favorite_movies": [103, 102]
    #     }
    # my_movie.update('movies', 102, new_data)


if __name__ == '__main__':
    main()
