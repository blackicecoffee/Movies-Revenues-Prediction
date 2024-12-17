import numpy as np
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def getAllMovies(cleaned_data_path: str) -> pd.DataFrame:
    movies_list_by_year = []
    for file in os.listdir(cleaned_data_path):
        if file.endswith(("csv")):
            file_path = os.path.join(cleaned_data_path, file)
            movie_df = pd.read_csv(file_path)
            movies_list_by_year.append(movie_df)
    
    all_movies = pd.concat(movies_list_by_year)
    return all_movies

def fillNull(lst: pd.DataFrame) -> None:
    lst = lst.drop("Budget", axis=1)
    lst['Opening'].fillna(lst['Opening'].mean(), inplace=True)
    lst['Distributor'].fillna(lst['Distributor'].mode()[0], inplace=True)
    lst['Release Date'].fillna(lst['Release Date'].mode()[0], inplace=True)
    lst['MPAA'].fillna(lst['MPAA'].mode()[0], inplace=True)
    lst['Running Time'].fillna(lst['Running Time'].mean(), inplace=True)
    lst['Genres'].fillna(lst['Genres'].mode()[0], inplace=True)
    lst['In Release'].fillna(lst['In Release'].mean(), inplace=True)
    lst['Widest Release'].fillna(lst['Widest Release'].mean(), inplace=True)
    lst['Director'].fillna(lst['Director'].mode()[0], inplace=True)
    lst['Domestic'].fillna(lst['Domestic'].mean(), inplace=True)
    lst['International'].fillna(lst['International'].mean(), inplace=True)
    lst['Worldwide'].fillna(lst['Worldwide'].mean(), inplace=True)
    return lst

def saveCSV(lst: pd.DataFrame, file_path: str) -> None:
    lst.to_csv(file_path, index=False)

cleaned_data_path = "../datasets/cleaned_data/"
processed_data_path = "../datasets/processed_data/all.csv"

movies = getAllMovies(cleaned_data_path=cleaned_data_path)
movies = fillNull(movies)
saveCSV(movies, processed_data_path)
