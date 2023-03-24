import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = "https://realty-in-ca1.p.rapidapi.com/locations/v2/auto-complete"

querystring = {"Query": "Quebec", "CultureId": "1", "IncludeLocations": "true"}

headers = {
    "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": os.environ.get("RAPIDAPI_HOST")
}

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)
