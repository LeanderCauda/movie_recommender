from flask import Flask, request, jsonify, render_template
from movie_recommender import recommend_movie

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie_title = request.form['movie']
    recommendations = recommend_movie(movie_title)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)