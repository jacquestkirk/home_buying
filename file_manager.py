import pandas as pd
import collections
import time
import random
import multi_suroce_scraper
import house_scraper
import calculations

addresses_file = r'csvs/addresses.txt'
output_file = r'csvs/house_data.csv'
calcs_file = r'csvs/calc_data.csv'

CalculatedData = collections.namedtuple(
    'CalculatedData',
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
        'high_rating',
        'cash_flow',
        'no_mortgage_cash_flow',
        'monthly_payments',
        'zero_cash_flow_pct',
        'no_principle_cash_flow',
        'time_to_zero_no_principle_cash_flow',
        'time_to_break_even',
    ]
)


def pull_data_from_addresses_csv():
    addresses = []
    data_list = []
    with open(addresses_file) as f:
        for line in f:
            clean_line = line.strip().replace('#', '')
            split_address = clean_line.split(',')
            addresses.append('{}, {}'.format(split_address[0], split_address[-1]))  # keep the street address and zipcode

    for address in addresses:
        data = multi_suroce_scraper.MultiSourceScraper(address).get_data()
        data_list.append(data)

        # wait for a random amount of time
        time.sleep(random.random() * 2 + 0.5)

    pd.DataFrame(data_list).to_csv(output_file)


def generate_calculations_csv():
    house_data_df = pd.read_csv(output_file)
    calculated_data_list = []

    for _, row in house_data_df.iterrows():
        house_data = house_scraper.HouseData(
            price=row['price'],
            property_tax=row['property_tax'],
            home_insurance=row['home_insurance'],
            hoa=row['hoa'],
            rent_zestimate=row['rent_zestimate'],
            beds=row['beds'],
            baths=row['baths'],
            area_sq_ft=row['area_sq_ft'],
            address=row['address'],
            city=row['city'],
            zip_code=row['zip_code'],
            community=row['community'],
            days_on_market=row['days_on_market'],
            house_type=row['house_type'],
            location=row['location'],
            year_built=row['year_built'],
            elementary_rating=row['elementary_rating'],
            middle_rating=row['middle_rating'],
            high_rating=row['high_rating']
        )
        calculator = calculations.HouseCalculator(house_data)

        calculated_data = CalculatedData(
            price=row['price'],
            property_tax=row['property_tax'],
            home_insurance=row['home_insurance'],
            hoa=row['hoa'],
            rent_zestimate=row['rent_zestimate'],
            beds=row['beds'],
            baths=row['baths'],
            area_sq_ft=row['area_sq_ft'],
            address=row['address'],
            city=row['city'],
            zip_code=row['zip_code'],
            community=row['community'],
            days_on_market=row['days_on_market'],
            house_type=row['house_type'],
            location=row['location'],
            year_built=row['year_built'],
            elementary_rating=row['elementary_rating'],
            middle_rating=row['middle_rating'],
            high_rating=row['high_rating'],
            cash_flow=calculator.calculate_cash_flow(),
            no_mortgage_cash_flow=calculator.calculate_no_mortgage_cash_flow(),
            monthly_payments=calculator.calculate_monthly_payments(),
            zero_cash_flow_pct=calculator.find_rent_change_to_zero_cash_flow_pct(),
            no_principle_cash_flow=calculator.calculate_initial_non_principle_cash_flow(),
            time_to_zero_no_principle_cash_flow=calculator.calculate_time_to_zero_non_principle_cash_flow(),
            time_to_break_even=calculator.calculate_time_to_break_even(),
        )

        calculated_data_list.append(calculated_data)

    pd.DataFrame(calculated_data_list).to_csv(calcs_file)
