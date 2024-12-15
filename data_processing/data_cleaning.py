import numpy as np
import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)

def CleanAndSaveCSV(file_path: str, save_file: str) -> None:
    movie_df = pd.read_csv(file_path, na_values=["", "NULL", "missing"], encoding="latin1")
    processed_movie_df = pd.DataFrame(columns=movie_df.columns)
    for i in range(len(movie_df)):
        processed_movie_df.loc[i] = [np.nan for _ in range(len(movie_df.keys()))]
        for key in movie_df.iloc[i].keys():
            value = movie_df.iloc[i][key]
            if pd.isna(value): continue

            if value == "-" or value == "": continue

            if key == "Opening":
                processed_opening = value.split(",")
                processed_opening = int(processed_opening[0][1:]) * pow(1000, len(processed_opening) - 3)
                processed_movie_df.loc[i, key] = processed_opening

            elif key == "Release Date":
                try:
                    processed_release_date = value.split(",")[-1].strip()
                except AttributeError:
                    processed_release_date = 2024
                processed_movie_df.loc[i, key] = processed_release_date

            elif key == "Running Time":
                value = value.split(" ")
                processed_running_time = 0
                try:
                    hr_idx = value.index("hr")
                except ValueError:
                    hr_idx = -1
                
                try:
                    min_idx = value.index("min")
                except ValueError:
                    min_idx = -1

                if hr_idx != -1:
                    processed_running_time += 60 * int(value[hr_idx - 1])
                if min_idx != -1:
                    processed_running_time += int(value[min_idx - 1])

                processed_movie_df.loc[i, key] = processed_running_time
            
            elif key == "In Release":
                value = value.split("/")
                processed_in_release = 0
                if len(value) == 1:
                    days_or_weeks = value[0].split(" ")
                    if days_or_weeks[1] == "weeks":
                        processed_in_release = int(days_or_weeks[0]) * 7
                    else:
                        processed_in_release = int("".join(days_or_weeks[0].split(",")))
                elif len(value) == 2:
                    days = int("".join(value[0].split(" ")[0].split(",")))
                    processed_in_release = days
                processed_movie_df.loc[i, key] = processed_in_release
            
            elif key == "Widest Release":
                value = value.split(" ")[0].split(",")
                if len(value) == 2:
                    processed_widest_release = int(value[0]) * 1000 + int(value[1])
                else: processed_widest_release = int(value[-1])
                processed_movie_df.loc[i, key] = processed_widest_release
            
            elif key == "Director":
                processed_director = value.replace('\n', '').replace('\r', '')
                processed_movie_df.loc[i, key] = processed_director
            
            elif key in ["Domestic", "International", "Worldwide", "Budget"]:
                value = value.replace('\n', '').replace('\r', '')
                processed_value = value.split(',')
                if processed_value[0][0] != '$':
                    processed_movie_df.loc[i, key] = np.nan
                else:
                    if len(processed_value) > 1:
                        processed_value = int(processed_value[0][1:]) * pow(1000, len(processed_value) - 3) + int(processed_value[1]) * pow(1000, len(processed_value) - 4)
                    else:
                        processed_value = int(processed_value[0][1:]) / 1000000
                    processed_movie_df.loc[i, key] = processed_value

            else: 
                processed_movie_df.loc[i, key] = value
    processed_movie_df.to_csv(save_file, index=False)

raw_data_path = "../datasets/raw_data/"
cleaned_data_path = "../datasets/cleaned_data/"

for file in os.listdir(raw_data_path):
    if file.endswith(("csv")):
        file_path = os.path.join(raw_data_path, file)
        save_file = os.path.join(cleaned_data_path, file)
        CleanAndSaveCSV(file_path=file_path, save_file=save_file)