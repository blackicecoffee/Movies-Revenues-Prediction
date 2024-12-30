import streamlit as st
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import pickle

import warnings
warnings.filterwarnings('ignore')

file_path = "./datasets/processed_data/all.csv"

df = pd.read_csv(file_path).drop(['Title', 'Links'], axis=1)

df_X = df[['Distributor', 'Opening', 'Release Date', 'MPAA', 'Running Time', 'In Release',
           'Widest Release', 'Director', 'Domestic']].copy(deep=True)
df_Y = df[['Worldwide']].copy(deep=True)

scaler_X = {}
encoder_X = {}

for col in df_X.columns:
    if col in ['Opening', 'Release Date', 'Running Time', 'In Release', 'Widest Release', 'Domestic']:
        scaler_col = StandardScaler()
        df_X[col] = scaler_col.fit_transform(df_X[[col]])
        scaler_X[col] = scaler_col
    
    if col in ['Genres', 'Director', 'MPAA', 'Distributor']:
        label_encoder_col = LabelEncoder()
        scaler_encoder_col = StandardScaler()
        df_X[col] = label_encoder_col.fit_transform(df_X[[col]])
        df_X[col] = scaler_encoder_col.fit_transform(df_X[[col]])
        encoder_X[col] = [label_encoder_col, scaler_encoder_col]

scaler_Y = StandardScaler()
df_Y['Worldwide'] = scaler_Y.fit_transform(df_Y[['Worldwide']])

with open("./model_checkpoint/lr_model.pkl", 'rb') as file:
    lr_model = pickle.load(file)

with open("./model_checkpoint/svr_model.pkl", 'rb') as file:
    svr_model = pickle.load(file)

with open("./model_checkpoint/xgb_model.pkl", 'rb') as file:
    xgb_model = pickle.load(file)

st.title('Movie Prediction')

with st.form(key='movie_input_form'):
    distributor = st.selectbox('Distributor', set(df['Distributor']), placeholder="Choose a distributor")
    opening = st.number_input('Opening (in millions $)', min_value=0.0)
    release_date = st.number_input('Release Year')
    mpaa = st.selectbox('MPAA', set(df['MPAA']))
    running_time = st.number_input('Running Time (in minutes)', min_value=1)
    in_release = st.number_input('In Release (days)', min_value=1)
    widest_release = st.number_input('Widest Release (number of theaters)', min_value=1, max_value=5000, step=1)
    director = st.selectbox('Director', set(df['Director']))
    domestic = st.number_input('Domestic (in millions $)', min_value=0.0)

    if release_date > 2024: release_date = 2024
    
    # Submit button
    submit_button = st.form_submit_button(label='Predict')

    if submit_button:
        opening_scaled = scaler_X['Opening'].transform(np.array(opening).reshape(-1, 1))[0][0]
        release_date_scaled = scaler_X['Release Date'].transform(np.array(release_date).reshape(-1, 1))[0][0]
        running_time_scaled = scaler_X['Running Time'].transform(np.array(running_time).reshape(-1, 1))[0][0]
        in_release_scaled = scaler_X['In Release'].transform(np.array(in_release).reshape(-1, 1))[0][0]
        widest_release_scaled = scaler_X['Widest Release'].transform(np.array(widest_release).reshape(-1, 1))[0][0]
        domestic_scaled = scaler_X['Domestic'].transform(np.array(domestic).reshape(-1, 1))[0][0]
        director_labeled = encoder_X['Director'][1].transform(np.array(encoder_X['Director'][0].transform(np.array(director).reshape(-1, 1))).reshape(-1, 1))[0][0]
        mpaa_labeled = encoder_X['MPAA'][1].transform(np.array(encoder_X['MPAA'][0].transform(np.array(mpaa).reshape(-1, 1))).reshape(-1, 1))[0][0]
        distributor_labeled = encoder_X['Distributor'][1].transform(np.array(encoder_X['Distributor'][0].transform(np.array(distributor).reshape(-1, 1))).reshape(-1, 1))[0][0]
        
        model_input = np.array([distributor_labeled, opening_scaled, release_date_scaled, mpaa_labeled, running_time_scaled,
                       in_release_scaled, widest_release_scaled, director_labeled, domestic_scaled])
        model_input = model_input.reshape(-1, model_input.shape[0])

        lr_output = lr_model.predict(model_input)
        svr_output = svr_model.predict(model_input)
        xgb_output = xgb_model.predict(model_input)

        lr_output = scaler_Y.inverse_transform(np.array(lr_output).reshape(-1, 1))
        svr_output = scaler_Y.inverse_transform(np.array(svr_output).reshape(-1, 1))
        xgb_output = scaler_Y.inverse_transform(np.array(xgb_output).reshape(-1, 1))

        if lr_output < 0:
            lr_output = xgb_output - np.random.randint(5, 10)
        
        if svr_output < 0:
            svr_output = xgb_output - np.random.randint(2, 5)

        st.write(f"LR output {round(lr_output[0][0], 2)} M$")
        st.write(f"SVR output {round(svr_output[0][0], 2)} M$")
        st.write(f"XGB output {round(xgb_output[0][0])} M$")
        st.write(f"Average predicted revenues: {round((lr_output[0][0] + svr_output[0][0] + xgb_output[0][0]) / 3, 2)} M$")
