from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Property(Base):
    __tablename__ = 'properties'

    id = Column(Integer, primary_key=True)
    property_id = Column(Integer)
    mls_number = Column(String)
    description = Column(String)
    street_address = Column(String)
    city = Column(String)
    province = Column(String)
    postal_code = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    property_type = Column(String)
    price = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)

    CAPEX = 300
    INSURANCE = 150
    WINDSOR_PROPERTY_TAX = 0.01853760

    def get_monthly_mortgage_payment(self, down_payment_percent, interest_rate_percent) -> float:
        down_payment = down_payment_percent / 100
        interest_rate_per_month = interest_rate_percent / 1200
        AMORTIZATION_PERIOD_TOTAL_MONTHS = 12 * 25

        mortgage = (self.price * (1 - down_payment)) * (
                interest_rate_per_month * (1 + interest_rate_per_month) ** AMORTIZATION_PERIOD_TOTAL_MONTHS) / (
                           ((1 + interest_rate_per_month) ** AMORTIZATION_PERIOD_TOTAL_MONTHS) - 1)

        return mortgage

    def get_monthly_property_tax(self):
        return (self.price * self.WINDSOR_PROPERTY_TAX) / 12

    def get_monthly_property_management_fees(self, average_room_price):
        return (average_room_price * self.bedrooms) * 0.1

    def calculate_profitability(self, down_payment_percent: float,
                                interest_rate_percent: float, average_room_price: float) -> float:
        profit = (
                         average_room_price * self.bedrooms) - self.get_monthly_mortgage_payment(down_payment_percent,
                                                                                                 interest_rate_percent) - self.get_monthly_property_tax() - self.INSURANCE - self.get_monthly_property_management_fees(
            average_room_price) - self.CAPEX
        return profit
