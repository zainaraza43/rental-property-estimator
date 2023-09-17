class Property:
    CAPEX = 300
    INSURANCE = 150
    WINDSOR_PROPERTY_TAX = 0.01853760
    AMORTIZATION_PERIOD_TOTAL_MONTHS = 12 * 25

    def __init__(
        self,
        property_id: int,
        mls_number: str,
        description: str,
        street_address: str,
        city: str,
        province: str,
        postal_code: str,
        latitude: float,
        longitude: float,
        property_type: str,
        price: int,
        bedrooms: int,
        bathrooms: int,
    ):
        self.property_id = property_id
        self.mls_number = mls_number
        self.description = description
        self.street_address = street_address
        self.city = city
        self.province = province
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.property_type = property_type
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms

    def get_monthly_mortgage_payment(
        self, down_payment_percent, interest_rate_percent
    ) -> float:
        down_payment = down_payment_percent / 100
        interest_rate_per_month = interest_rate_percent / 1200

        mortgage = (
            (self.price * (1 - down_payment))
            * (
                interest_rate_per_month
                * (1 + interest_rate_per_month) ** self.AMORTIZATION_PERIOD_TOTAL_MONTHS
            )
            / (
                ((1 + interest_rate_per_month) ** self.AMORTIZATION_PERIOD_TOTAL_MONTHS)
                - 1
            )
        )

        return mortgage

    def get_monthly_property_tax(self):
        return (self.price * self.WINDSOR_PROPERTY_TAX) / 12

    def get_monthly_property_management_fees(self, average_room_price):
        return (average_room_price * self.bedrooms) * 0.1

    def calculate_profitability(
        self,
        down_payment_percent: float,
        interest_rate_percent: float,
        average_room_price: float,
    ) -> float:
        profit = (
            (average_room_price * self.bedrooms)
            - self.get_monthly_mortgage_payment(
                down_payment_percent, interest_rate_percent
            )
            - self.get_monthly_property_tax()
            - self.INSURANCE
            - self.get_monthly_property_management_fees(average_room_price)
            - self.CAPEX
        )
        return profit
