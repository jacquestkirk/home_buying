import constants
from house_scraper import example_house_data
import calculations

down_payment_pct = 20

calculations.calculate_upfront_cost(
    house_price=example_house_data.price,
    down_payment_pct=down_payment_pct,
    reserve_cash=5576.42,
)

mortgage = calculations.calculate_mortgage(
    house_price=example_house_data.price,
    down_payment_pct=down_payment_pct,
    yearly_interest_pct=2.999,
    years=30
)

non_mortgage = calculations.calculate_non_mortgage_costs(
    example_house_data
)

print(mortgage + non_mortgage)

house_calculator = calculations.HouseCalculator(
    example_house_data, constants.mortgages['lee_anne_20_pct']
)
print(house_calculator.calculate_cash_flow())
print(house_calculator.calculate_no_mortgage_cash_flow())
print(house_calculator.find_rent_change_to_zero_cash_flow())
print(house_calculator.find_rent_change_to_zero_cash_flow_pct())
print(house_calculator.calculate_depreciation_tax_deduction())
