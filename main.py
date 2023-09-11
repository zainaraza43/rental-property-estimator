import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

from Property import Property

load_dotenv()


class PropertyAnalyzer:
    def __init__(self):
        self.url = "https://realty-in-ca1.p.rapidapi.com/properties/list-residential"
        self.headers = {
            "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
            "X-RapidAPI-Host": os.environ.get("RAPIDAPI_HOST"),
        }

    @sleep_and_retry
    @limits(calls=3, period=timedelta(minutes=1).total_seconds())
    def call_api(self):
        querystring = {
            "LatitudeMax": "42.309842",
            "LatitudeMin": "42.298578",
            "LongitudeMax": "-83.045481",
            "LongitudeMin": "-83.095084",
            "CurrentPage": "1",
            "RecordsPerPage": "10",
            "SortOrder": "A",
            "SortBy": "1",
            "CultureId": "1",
            "NumberOfDays": "0",
            "BedRange": "0-0",
            "BathRange": "0-0",
            "RentMin": "0",
        }

        response = requests.get(self.url, headers=self.headers, params=querystring)

        if response.status_code != 200:
            raise Exception("API response: {}".format(response.status_code))

        return response

    def analyze_properties(self):
        response_dict = self.call_api().json()
        for property_data in response_dict["Results"]:
            property = Property(property_data)


if __name__ == "__main__":
    analyzer = PropertyAnalyzer()
    analyzer.analyze_properties()
