import json
import re
import requests
from bs4 import BeautifulSoup
import house_scraper

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

url = "https://www.zillow.com/homedetails/626-S-Hoover-Rd-Durham-NC-27703/157439692_zpid/"

house_type_map = {
    'SINGLE_FAMILY': house_scraper.HouseType.SingleFamily,
    'Attached': house_scraper.HouseType.TownHouse,
    'Attached, townhouse': house_scraper.HouseType.TownHouse,
    'Condominium': house_scraper.HouseType.Condo,
}


def string_to_num(string_to_convert):
    return float(re.sub("[^0-9]", "", string_to_convert))


class ZillowScraper:
    def __init__(self, address):
        url = self.get_url_by_address(address)
        self.soup = self.get_page(url)
        self.json_data = self.get_json()

    def get_page(self, url):
        page = requests.get(url, headers=req_headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def get_url_by_address(self, address):
        search_url = r'https://www.zillowstatic.com/autocomplete/v3/suggestions?q={}'.format(address)
        results = requests.get(search_url, headers=req_headers)
        zpid = json.loads(results.content)['results'][0]['metaData']['zpid']
        return r'https://www.zillow.com/homes/{}_zpid/'.format(zpid)

    def get_json(self):
        full_json_data = json.loads(self.soup.find('script', {'id': 'hdpApolloPreloadedData'}).get_text())
        api_cache = json.loads(full_json_data['apiCache'])
        return api_cache[list(api_cache.keys())[1]]

    def get_rental_value(self):
        return self.json_data['property']['rentZestimate']

    def get_home_price(self):
        return self.json_data['property']['price']

    def get_num_beds(self):
        return self.json_data['property']['bedrooms']

    def get_num_baths(self):
        return self.json_data['property']['bathrooms']

    def get_num_square_feet(self):
        return self.json_data['property']['livingArea']

    def get_city(self):
        return self.json_data['property']['address']['city']

    def get_address(self):
        address_json = self.json_data['property']['address']
        return '{}, {}, {}, {}'.format(address_json['streetAddress'], address_json['city'], address_json['state'], address_json['zipcode'])

    def get_zip_code(self):
        return self.json_data['property']['address']['zipcode']

    def get_community(self):
        return

    def get_num_days_on_market(self):
        return self.json_data['property']['daysOnZillow']

    def get_house_type(self):
        type_string = self.json_data['property']['homeType']
        return house_type_map[type_string]

    def get_new_construction(self):
        return self.json_data['property']['listing_sub_type']['is_newHome']

    def get_tax_rate(self):
        return self.json_data['property']['propertyTaxRate']

    def get_hoa(self):
        hoa = self.json_data['property']['monthlyHoaFee']

        if hoa:
            return hoa
        return 0  # Return 0 if no HOA

    def get_home_insurance(self):
        return None

    def get_elementary_school_rating(self):
        return self.json_data['property']['schools'][0]['rating']

    def get_middle_school_rating(self):
        return self.json_data['property']['schools'][1]['rating']

    def get_high_school_rating(self):
        return self.json_data['property']['schools'][2]['rating']

    def get_year_built(self):
        return self.json_data['property']['yearBuilt']

    def get_location(self):
        return (
            self.json_data['property']['latitude'],
            self.json_data['property']['longitude']
        )

    def get_data(self):
        house_data = house_scraper.HouseData(
            price=self.get_home_price(),
            property_tax=self.get_tax_rate(),
            home_insurance=self.get_home_insurance(),
            hoa=self.get_hoa(),
            rent_zestimate=self.get_rental_value(),
            beds=self.get_num_beds(),
            baths=self.get_num_baths(),
            area_sq_ft=self.get_num_square_feet(),
            address=self.get_address(),
            zip_code=self.get_zip_code(),
            days_on_market=self.get_num_days_on_market(),
            house_type=self.get_house_type(),
            location=self.get_location(),
            year_built=self.get_year_built(),
            elementary_rating=self.get_elementary_school_rating(),
            middle_rating=self.get_middle_school_rating(),
            high_rating=self.get_high_school_rating(),
            community=self.get_community()
        )
        return house_data
