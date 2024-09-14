# Filename: chess_prediction.py

import numpy as np
import tensorflow as tf
from tensorflow import keras
import pickle
from keras.models import load_model

def extract_features_from_pgn(pgn_path):
    # Extract features from PGN file
    # Placeholder for feature extraction logic
    features = {}
    # Actual implementation needed here
    return features

def load_models():
    # Load both models, return them
    h5_model = load_model('path_to_your_model.h5')
    pkl_model = pickle.load(open('path_to_your_model.pkl', 'rb'))
    return h5_model, pkl_model

def predict_win_probability(win_pgn, loss_pgn, model_type='h5'):
    # Extract features
    win_features = extract_features_from_pgn(win_pgn)
    loss_features = extract_features_from_pgn(loss_pgn)
    
    # Prepare model input
    model_input = np.array([list(win_features.values()) + list(loss_features.values())])

    # Load models
    h5_model, pkl_model = load_models()

    # Select model
    model = h5_model if model_type == 'h5' else pkl_model

    # Make prediction
    prediction = model.predict(model_input)
    return prediction[0]

# Example usage:
if __name__ == "__main__":
    win_pgn = 'path_to_win_game.pgn'
    loss_pgn = 'path_to_loss_game.pgn'
    probability = predict_win_probability(win_pgn, loss_pgn, model_type='h5')
    print(f'Win Probability: {probability}')
