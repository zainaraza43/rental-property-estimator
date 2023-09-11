import re
from enum import Enum


class Property:
    class PropertyType(Enum):
        SINGLE_FAMILY = "Single Family"
        VACANT_LAND = "Vacant Land"

    CAPEX = 300
    INSURANCE = 150
    WINDSOR_PROPERTY_TAX = 0.01853760

    def __init__(self, property_data: dict):
        # MLS Fields
        self.property_id = int(property_data["Id"])
        self.mls_number = property_data["MlsNumber"]
        self.description = property_data["PublicRemarks"]

        # Location Fields
        match = re.match(
            r"(.+)\|(.+), (.+) (.+)",
            property_data["Property"]["Address"]["AddressText"],
        )
        self.street_address = match.group(1).strip()
        self.city = match.group(2).strip()
        self.province = match.group(3).strip()
        self.postal_code = match.group(4).strip()
        self.latitude = float(property_data["Property"]["Address"]["Latitude"])
        self.longitude = float(property_data["Property"]["Address"]["Longitude"])

        # Property Attributes Fields
        self.property_type = property_data["Property"]["Type"]
        self.price = int(property_data["Property"]["PriceUnformattedValue"])

        beds = 0
        baths = 0

        if self.property_type == Property.PropertyType.SINGLE_FAMILY.value:
            for c in property_data["Building"]["Bedrooms"]:
                if c.isdigit():
                    beds += int(c)
            for c in property_data["Building"]["BathroomTotal"]:
                if c.isdigit():
                    baths += int(c)

        self.bedrooms = beds
        self.bathrooms = baths

    def calculate_profitability(self, down_payment_percent, average_room_price: float,
                                interest_rate_percent) -> float:

        down_payment = down_payment_percent / 100
        interest_rate_per_month = interest_rate_percent / 1200
        property_tax = (self.price * self.WINDSOR_PROPERTY_TAX) / 12
        AMORTIZATION_PERIOD_TOTAL_MONTHS = 12 * 25
        property_management_fees = (average_room_price * self.bedrooms) * 0.1

        mortgage = (self.price * (1 - down_payment)) * (
                interest_rate_per_month * (1 + interest_rate_per_month) ** AMORTIZATION_PERIOD_TOTAL_MONTHS) / (
                           ((1 + interest_rate_per_month) ** AMORTIZATION_PERIOD_TOTAL_MONTHS) - 1)
        profit = (
                         average_room_price * self.bedrooms) - mortgage - property_tax - self.INSURANCE - property_management_fees
        return profit
