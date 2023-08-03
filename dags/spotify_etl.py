from spotify_utils import get_authorization_code, get_access_token_authorization_code, get_json, get_auth_header
from datetime import datetime
import pandas as pd
from flask import session 
import os

# Getting the authorization code and access token

access_token = os.environ["SPOTIFY_ACCESS_TOKEN"]

def get_recently_played(access_token, after_time=None):
    headers = get_auth_header(access_token)

    url = "https://api.spotify.com/v1/me/player/recently-played"
    params = {"limit": 50}

    if after_time:
        params["after"] = after_time

    response = get_json(url, headers, params)

    # print(response)
    return response

def format_timestamp_ms(timestamp_ms):
    #parsing the time 
    dt_object = datetime.strptime(timestamp_ms, "%Y-%m-%dT%H:%M:%S.%fZ")
    #or dt_object = datetime.fromisoformat(timestamp_ms.replace("Z","+00:00"))
    return dt_object.strftime("%Y-%m-%d %H:%M:%S")

def main_dataframe():
    all_recently_played = []
    after_time = None

    while True:
        recently_played = get_recently_played(access_token, after_time)

        if not recently_played or len(recently_played["items"]) == 0:
            break

        all_recently_played.extend(recently_played["items"])
        after_time = recently_played["items"][-1]["played_at"]

    if all_recently_played:
        song_names = []
        artist_names = []
        played_at_list = []
        timestamps = []

        print("All Recently Played Songs:")
        for item in all_recently_played:
            track = item["track"]
            song_names.append(track["name"])
            artist_names.append(track["album"]["artists"][0]["name"])
            played_at = format_timestamp_ms(item["played_at"])
            played_at_list.append(played_at)
            timestamps.append(played_at[:10])

            # print(f"Song: {track['name']}")
            # print(f"Artist: {track['album']['artists'][0]['name']}")
            # print(f"Played at: {played_at}")
            # print("-" * 30)

        song_dict = {
            "song_name": song_names,
            "artist_name": artist_names,
            "played_at": played_at_list,
            "timestamp": timestamps
        }

        df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
        # df.drop_duplicates(subset=['played_at', 'song_name', 'artist_name'], keep='first', inplace=True)

        return df

def Quality_Check(main_df):
    if main_df.empty:
        print("Songs are not extracted.")
        return False

    # Enforcing Primary keys since we don't need duplicates
    if pd.Series(main_df['played_at']).is_unique:
       pass
    else:
        # The Reason for using exception is to immediately terminate the program and avoid further processing
        raise Exception("Exception occurred: (Primary key) Data might contain duplicates")

    # Checking for null
    if main_df.isnull().values.any():
        raise Exception("Null values found")

def transform_df(main_df):
    # Applying main_df logic
    main_df['played_at'] = pd.to_datetime(main_df['played_at'])

    main_df['minutes'] = main_df['played_at'].dt.minute
    main_df['seconds'] = main_df['played_at'].dt.second

    # Creating a Primary Key based on Timestamp and artist name
    main_df["ID"] = main_df['minutes'].astype(str) + '-' + main_df['seconds'].astype(str) + "-" + main_df["artist_name"]

    main_df.drop(columns=['minutes', 'seconds'], inplace=True)

    return main_df[['played_at', 'artist_name', 'song_name','timestamp']]

def spotify_etl():
    
    main_df = main_dataframe()

    main_df.drop_duplicates(subset=["played_at"], keep='first', inplace=True)

    # Quality check for duplicates and null values
    Quality_Check(main_df)

    # Perform main_df
    fin_df = transform_df(main_df)

    print(fin_df)
    return(fin_df)
spotify_etl()