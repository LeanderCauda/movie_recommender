from flask import Flask, request, jsonify, render_template
from movie_recommender import recommend_movie

app = Flask(__name__)

import requests

def fetch_movie_posters(movie_title):
    api_key = "b57bd9976b48f8b8922927d508e7e38c"
    base_url = "https://api.themoviedb.org/3/search/movie"
    image_base_url = "https://image.tmdb.org/t/p/w500"

    # Search for the movie in TMDb
    response = requests.get(base_url, params={"api_key": api_key, "query": movie_title})
    data = response.json()
    
    # Check if the movie is found
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"{image_base_url}{poster_path}"
    return None


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie_title = request.form['movie']
    recommendations = recommend_movie(movie_title)

    movie_data = []
    for recommended_movie in recommendations:
        poster_url = fetch_movie_posters(recommended_movie)
        movie_data.append({"title": recommended_movie, "poster_url": poster_url})

    return jsonify(movie_data)

if __name__ == '__main__':
    app.run(debug=True)