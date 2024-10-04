import pandas as pd
import numpy as np
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from flask import Flask, request, jsonify, render_template


# loading the data
movie_df = pd.read_csv('movies.csv') 
selected_features = ['genres','keywords','tagline','cast','director']
for features in selected_features:        
    movie_df[features] = movie_df[features].fillna('')

#concatanating features and vectorizing the resulting data
features_data = movie_df['genres']+' '+movie_df['keywords']+' '+movie_df['tagline']+' '+movie_df['cast']+' '+movie_df['director']
vectorizer = TfidfVectorizer()
features_vector = vectorizer.fit_transform(features_data)

# similarity score 
sim = cosine_similarity(features_vector)



def get_similarity(movie_name, n_reco=5):
    ''' returns the list of movies with the highest similarity score with the given movie
    
    Args: 
        movie_name: str
    
    Returns:
        sorted_sim_movies: shape(n_reco, ) 
    '''
    list_titles = movie_df['title'].tolist()
    find_match = difflib.get_close_matches(movie_name, list_titles)
    try:
        closest_match = find_match[0]
    except IndexError:
        return "Movie not found"
    index_movie = movie_df[movie_df.title == closest_match]['index'].values[0]
    sim_score = list(enumerate(sim[index_movie]))
    sorted_sim_movies = sorted(sim_score, key=lambda x: x[1], reverse=True)[1:]
    return sorted_sim_movies[:n_reco]

def popularity(reco_without_pop):
    ''' sorts selected list of movies by popularity
    
    Args: 
        reco_without_pop: shape(n_reco, )
    
    Returns:
        sorted_pop: shape(n_reco, ) 
    '''
    reco_with_pop = []
    for j, movie in enumerate(reco_without_pop):
        index = movie[0]
        reco_with_pop.append(reco_without_pop[j] + (movie_df.loc[index, 'popularity'],))
    sorted_pop = sorted(reco_with_pop, key=lambda x: x[2], reverse=True)
    return sorted_pop

def recommend_movie(movie_name, n_display=3):
    ''' returns list of recommended movies
    
    Args: 
        movie_name: str
    
    Returns:
        displayed_movies: shape(n_display, ) 
    '''
    sorted_movies = get_similarity(movie_name)
    if isinstance(sorted_movies, str):
        return [sorted_movies]  # Return as a list for consistency
    else:
        top_movies = popularity(sorted_movies)
        displayed_movies = [movie_df.iloc[movie[0]]['title'] for movie in top_movies[:n_display]]
        return displayed_movies
