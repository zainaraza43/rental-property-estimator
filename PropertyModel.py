from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PropertyModel(Base):
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
