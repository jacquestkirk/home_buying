import collections
import enum


class HouseType(enum.Enum):
    SingleFamily = 'Single family residence'
    TownHouse = 'Attached'
    Condo = 'Condominium'


# a collection of data harvested from Zillow
HouseData = collections.namedtuple(
    'HouseData',
    [
        'price',
        'property_tax',
        'home_insurance',
        'hoa',
        'rent_zestimate',
        'beds',
        'baths',
        'area_sq_ft',
        'address',
        'city',
        'zip_code',
        'community',
        'days_on_market',
        'house_type',
        'location',
        'year_built',
        'elementary_rating',
        'middle_rating',
        'high_rating'
    ]
)

# https://www.zillow.com/homedetails/700-Nightshade-Way-Raleigh-NC-27610/65344676_zpid/
example_house_data = HouseData(
    price=280000,
    property_tax=203,
    home_insurance=98,
    hoa=25,
    rent_zestimate=1711,
    beds=3,
    baths=2,
    area_sq_ft=1000,
    address='123 sesame street',
    city='Durham',
    zip_code=12345,
    community=None,
    days_on_market=1,
    house_type=HouseType.SingleFamily,
    location=(1, 1),
    year_built=2000,
    elementary_rating=1,
    middle_rating=1,
    high_rating=1
)
