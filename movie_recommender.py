import pandas as pd
import numpy as np
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import pickle
from scipy.sparse import csr_matrix
import faiss


movies_df = pd.read_csv('cleaned_movies.csv')
ratings_df = pd.read_csv('dataset/ratings_small.csv')


#Handle NaNs Values
movies_df['title'] = movies_df['title'].fillna('')


# TF-IDF Model

#Weight distribution
feature_weights = {
    'overview': 2,  
    'genres': 3,    
    'keywords': 1.5,
    'crew': 1,    
    'tagline': 1.5  
}

features_data = (
    movies_df['overview'].fillna('').apply(lambda x: (str(x) + ' ') * feature_weights['overview']) +
    movies_df['genres'].fillna('').apply(lambda x: (str(x) + ' ') * feature_weights['genres']) +
    movies_df['keywords'].fillna('').apply(lambda x: (str(x) + ' ') * int(feature_weights['keywords'])) +
    movies_df['crew'].fillna('').apply(lambda x: (str(x) + ' ') * int(feature_weights['crew'])) +
    movies_df['tagline'].fillna('').apply(lambda x: (str(x) + ' ') * int(feature_weights['tagline']))
)

print("Building Vectorizer...")
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
features_vector = vectorizer.fit_transform(features_data)
print("Building Sparse Matrix...")


# Metric: cosine similarity
print("Computing Cosine Similarity...")
features_vector_dense = features_vector.toarray().astype(np.float32)

# Initialize FAISS index for inner product (cosine similarity)
index = faiss.IndexFlatIP(features_vector_dense.shape[1]) 
index.add(features_vector_dense)

# Collaborative Filtering

user_movie_matrix = ratings_df.pivot(index='userId', columns='movieId', values='rating').fillna(0)
movie_ratings = user_movie_matrix.T

# KNN model
collab_model = NearestNeighbors(metric='cosine', algorithm='brute')
collab_model.fit(movie_ratings)

print("Exporting models...")
# with open('models/vectorizer.pkl', 'wb') as f:
#     pickle.dump(vectorizer, f)

# with open('models/svd.pkl', 'wb') as f:
#     pickle.dump(svd, f)

faiss.write_index(index, 'models/faiss_index.index')

with open('models/tfidf_matrix.pkl', 'wb') as f:
    pickle.dump(features_vector_dense, f)

with open('models/user_movie_matrix.pkl', 'wb') as f:
    pickle.dump(user_movie_matrix, f)

with open('models/collab_model.pkl', 'wb') as f:
    pickle.dump(collab_model, f)


movies_df.to_csv('processed_movies.csv', index=False)
