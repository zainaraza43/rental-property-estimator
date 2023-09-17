import os
from datetime import timedelta
from typing import List

import requests
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

from Property import Property
from PropertyModel import PropertyModel
from database import Session

load_dotenv()


def print_properties(props):
    for prop in props:
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
        print(f"Projected Profit: {prop.calculate_profitability(5, 6, 550)}")
        print()


def calculate_bedrooms_and_bathrooms(property_data):
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


def get_profitable_properties(properties: List[Property]) -> List[Property]:
    profitable_properties = []
    for prop in properties:
        if prop.calculate_profitability(5, 6, 550) >= -300:
            profitable_properties.append(prop)
    return profitable_properties


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

    def get_all_unique_properties(self) -> List[Property]:
        unique_properties = []
        session = Session()

        try:
            response_dict = self.call_api().json()

            for property_data in response_dict["Results"]:
                beds, baths = calculate_bedrooms_and_bathrooms(property_data)

                prop = Property(
                    property_id=property_data["Id"],
                    mls_number=property_data["MlsNumber"],
                    description=property_data["PublicRemarks"],
                    street_address=property_data["Property"]["Address"]["AddressText"]
                    .split("|", 1)[0]
                    .strip(),
                    city=property_data["Property"]["Address"]["AddressText"]
                    .split("|", 1)[-1]
                    .split(", ", 1)[0]
                    .strip(),
                    province=property_data["Property"]["Address"]["AddressText"]
                    .split(", ", 1)[-1]
                    .rsplit(" ", 1)[0]
                    .strip(),
                    postal_code=property_data["Property"]["Address"]["AddressText"]
                    .rsplit(" ", 1)[-1]
                    .strip(),
                    latitude=float(property_data["Property"]["Address"]["Latitude"]),
                    longitude=float(property_data["Property"]["Address"]["Longitude"]),
                    property_type=property_data["Property"]["Type"],
                    price=int(property_data["Property"]["PriceUnformattedValue"]),
                    bedrooms=beds,
                    bathrooms=baths,
                )
                prop_model = PropertyModel(
                    property_id=prop.property_id,
                    mls_number=prop.mls_number,
                    description=prop.description,
                    street_address=prop.street_address,
                    city=prop.city,
                    province=prop.province,
                    postal_code=prop.postal_code,
                    latitude=prop.latitude,
                    longitude=prop.longitude,
                    property_type=prop.property_type,
                    price=prop.price,
                    bedrooms=beds,
                    bathrooms=baths,
                )

                existing_property = (
                    session.query(PropertyModel)
                    .filter_by(property_id=prop.property_id)
                    .first()
                )

                if prop.property_type == "Single Family":
                    if existing_property:
                        existing_property.description = prop.description
                        if prop.price != existing_property.price:
                            existing_property.price = prop.price
                            unique_properties.append(prop)
                    else:
                        unique_properties.append(prop)
                        session.add(prop_model)

            session.commit()
        except Exception as e:
            print(f"Error: {e}")
            session.rollback()
        finally:
            session.close()
        return unique_properties
