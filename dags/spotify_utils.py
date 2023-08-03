from requests import post, get
import base64
from urllib.parse import urlencode
import os
import json
from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for,session
from datetime import datetime
import pandas as pd
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"
app = Flask(__name__) 
app.secret_key = "Ajjudaii@987"

def get_access_token_client_credentials():
    # Implementing the method to get the access token
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    auth_url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content_Type": "application/x-www-form-urlencoded"
    }
    # The "grant_type": "client_credentials" parameter is specific to the "Client Credentials Flow" and is used to indicate
    # to the Spotify API that the app is requesting an access token for server-to-server authentication.

    data = {'grant_type': 'client_credentials'}

    result = post(auth_url, headers=headers, data=data)
    json_result = json.loads(result.content)  # or we can use result.json()
    token = json_result["access_token"]
    return token

@app.route("/")
def get_authorization_code():
    #Redirecting  to the Spotify authorization page
    auth_url = "https://accounts.spotify.com/authorize"
    scopes = ["user-read-recently-played"]
    auth_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes)
    }

    auth_url += "?" + urlencode(auth_params)
    
    session["authorization_url"] = auth_url

    return redirect(auth_url)


@app.route("/callback")
def callback():

    # Handling the callback from the Spotify authorization page
    authorization_code = request.args.get("code")
    print("Authorization Code received:", authorization_code)
    
    session["authorization_code"] = authorization_code

    authorization_code = session.get("authorization_code")
    if authorization_code:
       
        access_token = get_access_token_authorization_code(authorization_code)
        print("Access Token (Authorization Code Flow):", access_token)
        session["access_token"] = access_token
    else:
        print("Failed to get authorization code.")

    return "Authorization Process Completed!"


def get_access_token_authorization_code(authorization_code):
    # Step 4: Exchange the authorization code for an access token
    auth_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": redirect_uri
    }
    response = post(auth_url, headers=headers, data=data)
    
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_json(url, headers, params=None):
    response = get(url, headers=headers, params=params)
    return response.json()

def post_json(url, headers, data=None):
    response = post(url, headers=headers, data=data)
    return response.json()


if __name__ == "__main__":
        # authorization_code = get_authorization_code()
    
    app.run(debug=True , port = 8888)

    

