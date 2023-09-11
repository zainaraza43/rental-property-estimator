import os
from datetime import timedelta

import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

from Property import Property
from database import Session

load_dotenv()


def get_properties_by_type(property_type):
    session = Session()
    properties = session.query(Property).filter_by(property_type=property_type).all()
    session.close()
    return properties


def print_database():
    session = Session()
    properties = session.query(Property).all()
    session.close()

    for prop in properties:
        print(f"Property ID: {prop.property_id}")
        print(f"MLS Number: {prop.mls_number}")
        print(f"Description: {prop.description}")
        print(f"Street Address: {prop.street_address}")
        print(f"City: {prop.city}")
        print(f"Province: {prop.province}")
        print(f"Postal Code: {prop.postal_code}")
        print(f"Latitude: {prop.latitude}")
        print(f"Longitude: {prop.longitude}")
        print(f"Property Type: {prop.property_type}")
        print(f"Price: {prop.price}")
        print(f"Bedrooms: {prop.bedrooms}")
        print(f"Bathrooms: {prop.bathrooms}")
        print("\n")


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

    def calculate_bedrooms_and_bathrooms(self, property_data):
        beds = 0
        baths = 0

        if property_data["Property"]["Type"] == "Single Family":
            for c in property_data["Building"]["Bedrooms"]:
                if c.isdigit():
                    beds += int(c)
            for c in property_data["Building"]["BathroomTotal"]:
                if c.isdigit():
                    baths += int(c)

        return beds, baths

    def analyze_properties(self):
        response_dict = self.call_api().json()
        session = Session()
        for property_data in response_dict["Results"]:
            beds, baths = self.calculate_bedrooms_and_bathrooms(property_data)
            property = Property(
                property_id=property_data["Id"],
                mls_number=property_data["MlsNumber"],
                description=property_data["PublicRemarks"],
                street_address=property_data["Property"]["Address"]["AddressText"].split('|', 1)[0].strip(),
                city=property_data["Property"]["Address"]["AddressText"].split('|', 1)[-1].split(', ', 1)[0].strip(),
                province=property_data["Property"]["Address"]["AddressText"].split(', ', 1)[-1].rsplit(' ', 1)[
                    0].strip(),
                postal_code=property_data["Property"]["Address"]["AddressText"].rsplit(' ', 1)[-1].strip(),
                latitude=float(property_data["Property"]["Address"]["Latitude"]),
                longitude=float(property_data["Property"]["Address"]["Longitude"]),
                property_type=property_data["Property"]["Type"],
                price=int(property_data["Property"]["PriceUnformattedValue"]),
                bedrooms=beds,
                bathrooms=baths,
            )

            existing_property = session.query(Property).filter_by(property_id=property.property_id).first()

            if existing_property:
                existing_property.description = property.description
                existing_property.price = property.price
            else:
                session.add(property)

        session.commit()
        session.close()


if __name__ == "__main__":
    analyzer = PropertyAnalyzer()
    analyzer.analyze_properties()

    single_family_properties = get_properties_by_type("Single Family")
    for prop in single_family_properties:
        print_database()
