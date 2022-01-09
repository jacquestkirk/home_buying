import math

import calculations
from zillow_scraper import ZillowData


def test_zillow_total_cost():
    # https://www.zillow.com/homedetails/700-Nightshade-Way-Raleigh-NC-27610/65344676_zpid/
    example_zillow_data = ZillowData(
        price=280000,
        property_tax=203,
        home_insurance=98,
        hoa=25,
        rent_zestimate=2100
    )

    mortgage = calculations.calculate_mortgage(
        house_price=example_zillow_data.price,
        down_payment_pct=20,
        yearly_interest_pct=2.999,
        years=30
    )

    non_mortgage = calculations.calculate_non_mortgage_costs(
        example_zillow_data,
        repair_fund_multiplier=0,
        property_manager_pct=0
    )

    assert math.floor(mortgage + non_mortgage) == 1270

