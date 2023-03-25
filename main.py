import os
from dotenv import load_dotenv
import requests
from ratelimit import limits, sleep_and_retry

load_dotenv()

# Rate limiting
ONE_MINUTE = 60

# Global temps, one day will make these not static but not today
AVERAGE_ROOM_PRICE = 500
DOWN_PAYMENT = 0.05
MISC = 300
R = 0.05 / 12
N = 12 * 25
I = 100
WINDSOR_PROPERTY_TAX = 0.01853760


@sleep_and_retry
@limits(calls=3, period=ONE_MINUTE)
def call_api(url):

    querystring = {"LatitudeMax": "42.309842", "LatitudeMin": "42.298578", "LongitudeMax": "-83.045481", "LongitudeMin": "-83.095084",
                   "CurrentPage": "1", "RecordsPerPage": "10", "SortOrder": "A", "SortBy": "1", "CultureId": "1", "NumberOfDays": "0", "BedRange": "0-0", "BathRange": "0-0", "RentMin": "0"}

    headers = {
        "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.environ.get("RAPIDAPI_HOST")
    }
    response = requests.request(
        "GET", url, headers=headers, params=querystring)

    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return response


url = "https://realty-in-ca1.p.rapidapi.com/properties/list-residential"

properties = []  # All properties eligible

for i in range(5):
    response_dict = call_api(url).json()

    for property in response_dict['Results']:
        P = int(property['Property']['PriceUnformattedValue']
                ) * (1 - DOWN_PAYMENT)
        M = (P * R * (1 + R) ** N) / (((1 + R) ** N) - 1)
        T = WINDSOR_PROPERTY_TAX * \
            int(property['Property']['PriceUnformattedValue']) / 12
        beds = 0
        for c in property['Building']['Bedrooms']:
            if c.isdigit():
                beds += int(c)
        PM = 0.1 * AVERAGE_ROOM_PRICE * beds
        total_cost = M + T + I + PM + MISC

        print(f"{property['Property']['Address']['AddressText']}")
        print(
            f"{property['Building']['StoriesTotal']} story {property['Building']['Type']} | {property['Building']['Bedrooms']} bed(s), {property['Building']['BathroomTotal']} bath(s)")
        print(
            f"{property['Property']['Type']} {property['Property']['Price']}")
        # print(f"NOTES: {property['PublicRemarks']}")
        print(f"{M:.2f} (Mortgage) + {T:.2f} (Taxes) + {I} (Insurance) + {PM} (Property Management) + {MISC} (MISC) = ${total_cost:.2f}")
        print(
            f"Assuming average room price of {AVERAGE_ROOM_PRICE}, total revenue/month = ${AVERAGE_ROOM_PRICE * beds}")
        print(
            f"Profit = {AVERAGE_ROOM_PRICE * beds - total_cost:.2f}, down payment of ${int(property['Property']['PriceUnformattedValue']) * DOWN_PAYMENT:.2f}\n")
