import os
from dotenv import load_dotenv
import requests

load_dotenv()

url = "https://realty-in-ca1.p.rapidapi.com/properties/list-residential"

querystring = {"LatitudeMax": "42.309842", "LatitudeMin": "42.298578", "LongitudeMax": "-83.045481", "LongitudeMin": "-83.095084",
               "CurrentPage": "1", "RecordsPerPage": "10", "SortOrder": "A", "SortBy": "1", "CultureId": "1", "NumberOfDays": "0", "BedRange": "0-0", "BathRange": "0-0", "RentMin": "0"}

headers = {
    "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": os.environ.get("RAPIDAPI_HOST")
}

response = requests.request("GET", url, headers=headers, params=querystring)
response_dict = response.json()

for property in response_dict['Results']:
    print(f"{property['Property']['Address']['AddressText']}")
    print(
        f"{property['Building']['StoriesTotal']} story {property['Building']['Type']} | {property['Building']['Bedrooms']} bed(s), {property['Building']['BathroomTotal']} bath(s)")
    print(f"{property['Property']['Type']} {property['Property']['Price']}")
    print(f"NOTES: {property['PublicRemarks']}\n")
