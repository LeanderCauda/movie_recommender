from flask import Flask, request, jsonify, render_template
import requests
import pickle
import pandas as pd
import numpy as np
import difflib
import faiss
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

movie_factors_df = pd.read_csv('collaborative_matrix.csv',index_col=0)
lookup_title = pd.read_csv('lookup_title.csv')

# movies_df['genres'] = movies_df['genres'].fillna('')  
# movies_df['keywords'] = movies_df['keywords'].fillna('')  
# movies_df['crew'] = movies_df['crew'].fillna('')
# movies_df['title'] = movies_df['title'].fillna('')

# def get_content_similarity(movie_name, n_reco=5):
#     ''' returns the list of movies with the highest similarity score with the given movie
    
#     Args: 
#         movie_name: str
    
#     Returns:
#         sorted_sim_movies: shape(n_reco, ) 
#     '''
#     list_titles = movies_df['title'].tolist()
#     find_match = difflib.get_close_matches(movie_name, list_titles)
#     try:
#         closest_match = find_match[0]
#     except IndexError:
#         return "Movie not found"
#     index_movie = movies_df[movies_df.title == closest_match]['id'].index[0]
#     query_vector = tfidf_matrix[index_movie].reshape(1, -1).astype('float32')

#     # Use FAISS to find the most similar movies (top n_reco)
#     distances, indices = index.search(query_vector, n_reco+1) 

#     sorted_sim_movies = []
#     for idx, _ in zip(indices[0][1:], distances[0][1:]):
#         sorted_sim_movies.append(idx)

#     return sorted_sim_movies

# def popularity(reco_without_pop):
#     ''' sorts selected list of movies by popularity
    
#     Args: 
#         reco_without_pop: shape(n_reco, )
    
#     Returns:
#         sorted_pop: shape(n_reco, ) 
#     '''
#     reco_with_pop = []
#     for idx in reco_without_pop:
#         reco_with_pop.append((idx,movies_df.loc[idx, 'vote_count']))
#     sorted_pop = sorted(reco_with_pop, key=lambda x: x[1], reverse=True)
#     return sorted_pop

# def recommend_movie(movie_name, n_display=3):
#     ''' returns list of recommended movies
    
#     Args: 
#         movie_name: str
    
#     Returns:
#         displayed_movies: shape(n_display, ) 
#     '''
#     sorted_movies = get_similarity(movie_name)
#     if isinstance(sorted_movies, str):
#         return [sorted_movies] 
#     else:
#         top_movies = popularity(sorted_movies)
#         displayed_movies = [movies_df.iloc[movie[0]]['title'] for movie in top_movies[:n_display]]
#         return displayed_movies



def recommend_collaborative(movie_title, top_n=3):

    list_titles = lookup_title['title'].dropna().tolist()
    print(movie_title)
    find_match = difflib.get_close_matches(movie_title, list_titles)
    try:
        closest_match = find_match[0]
    except IndexError:
        return "Movie not found"

    movie_id = lookup_title.loc[lookup_title['title'] == closest_match, 'movieId'].values[0]


    # Compute cosine similarity between this movie and all others
    movie_vector = movie_factors_df.loc[[movie_id]]
    similarities = cosine_similarity(movie_vector, movie_factors_df)[0]

    sim_scores = pd.Series(data = similarities, index=movie_factors_df.index)
    sim_scores = sim_scores.drop(movie_id)  
    top_similar = sim_scores.sort_values(ascending=False).head(top_n)

    to_display = []

    missing_ids = [idm for idm in top_similar.index if idm not in lookup_title['movieId'].values]
    print("Missing movieIds in lookup_title:", missing_ids)

    for idm in top_similar.index.tolist():
        print(type(idm), idm)
        print(lookup_title['movieId'].dtype)
        title = lookup_title.loc[lookup_title['movieId'] == idm, 'title'].values[0]
        print(title)
        to_display.append(title)

    return to_display





def fetch_movie_posters(movie_title):
    api_key = "b57bd9976b48f8b8922927d508e7e38c"
    base_url = "https://api.themoviedb.org/3/search/movie"
    image_base_url = "https://image.tmdb.org/t/p/w500"

    response = requests.get(base_url, params={"api_key": api_key, "query": movie_title})
    data = response.json()
    
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
    recommendations = recommend_collaborative(movie_title)

    movie_data = []
    for recommended_movie in recommendations:
        poster_url = fetch_movie_posters(recommended_movie)
        movie_data.append({"title": recommended_movie, "poster_url": poster_url})
    return jsonify(movie_data)

if __name__ == '__main__':
    app.run(debug=True)