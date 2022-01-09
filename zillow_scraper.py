import collections

# a collection of data harvested from Zillow
ZillowData = collections.namedtuple(
    'ZillowData',
    [
        'price',
        'property_tax',
        'home_insurance',
        'hoa',
        'rent_zestimate'
    ]
)

# https://www.zillow.com/homedetails/700-Nightshade-Way-Raleigh-NC-27610/65344676_zpid/
example_zillow_data = ZillowData(
    price=280000,
    property_tax=203,
    home_insurance=98,
    hoa=25,
    rent_zestimate=1711
)
