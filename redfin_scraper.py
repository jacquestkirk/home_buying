import json
import re
import requests
import numpy as np
from bs4 import BeautifulSoup
import house_scraper

req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

url = "https://www.redfin.com/NC/Durham/626-S-Hoover-Rd-27703/home/110075561"

house_type_map = {
    'Single Family Residential': house_scraper.HouseType.SingleFamily,
    'Townhouse': house_scraper.HouseType.TownHouse,
    'Condominium': house_scraper.HouseType.Condo,
}


def string_to_num(string_to_convert):
    return float(re.sub("[^0-9]", "", string_to_convert))


class RedfinScraper:
    def __init__(self, address):
        url = self.get_url_by_address(address)
        self.soup = self.get_page(url)
        self.json_data = self.get_json()
        self.above_the_fold = json.loads(self.json_data['/stingray/api/home/details/aboveTheFold']['res']['text'].split('&&')[-1])['payload']
        self.below_the_fold = json.loads(self.json_data['/stingray/api/home/details/belowTheFold']['res']['text'].split('&&')[-1])['payload']
        self.rental_info = json.loads(self.json_data['/stingray/api/home/details/rental-estimate']['res']['text'].split('&&')[-1])['payload']

    def get_url_by_address(self, address):
        search_url = r'https://www.redfin.com/stingray/do/location-autocomplete?location={}&start=0&count=10&v=2'.format(address)
        results = requests.get(search_url, headers=req_headers)
        extension = json.loads(results.text.split('&&')[-1])['payload']['sections'][0]['rows'][0]['url']
        return r'https://www.redfin.com{}'.format(extension)

    def get_page(self, url):
        page = requests.get(url, headers=req_headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup

    def get_json(self):
        scripts = self.soup.find_all('script')
        script = scripts[-2]
        json_data = json.loads(script.text.split('InitialContext = ', 2)[-1].rsplit(';\nroot.__reactServerState.Config =', 2)[0])['ReactServerAgent.cache']['dataCache']
        return json_data

    def get_rental_value(self):
        if 'predictedValueLow' in self.rental_info['rentalEstimateInfo']:
            low_value = self.rental_info['rentalEstimateInfo']['predictedValueLow']
            high_value = self.rental_info['rentalEstimateInfo']['predictedValueHigh']
            return np.mean([low_value, high_value])
        else:
            return None

    def get_home_price(self):
        return self.above_the_fold['addressSectionInfo']['priceInfo']['amount']

    def get_num_beds(self):
        return self.above_the_fold['addressSectionInfo']['beds']

    def get_num_baths(self):
        return self.above_the_fold['addressSectionInfo']['baths']

    def get_num_square_feet(self):
        return self.above_the_fold['addressSectionInfo']['sqFt']['value']

    def get_community(self):
        utility_information = self.below_the_fold['amenitiesInfo']['superGroups'][2]['amenityGroups'][3]['amenityEntries'][6]

    def get_address(self):
        address_json = self.above_the_fold['addressSectionInfo']
        return '{}, {}, {}, {}'.format(
            address_json['streetAddress']['assembledAddress'],
            address_json['city'],
            address_json['state'],
            address_json['zip']
        )

    def get_zip_code(self):
        return self.above_the_fold['addressSectionInfo']['zip']

    def get_city(self):
        return self.above_the_fold['addressSectionInfo']['city']

    def get_community(self):
        for super_group in self.below_the_fold['amenitiesInfo']['superGroups']:
            for amenity_group in super_group['amenityGroups']:
                for amenity in amenity_group['amenityEntries']:
                    if 'amenityName' in amenity:
                        if amenity['amenityName'] == 'Subdivision':
                            return amenity['amenityValues'][0]

    def get_num_days_on_market(self):
        return None

    def get_house_type(self):
        type_string = self.below_the_fold['publicRecordsInfo']['basicInfo']['propertyTypeName']
        return house_type_map[type_string]

    def get_new_construction(self):
        return None

    def get_tax_rate(self):
        return self.below_the_fold['publicRecordsInfo']['mortgageCalculatorInfo']['propertyTaxRate']

    def get_hoa(self):
        mortgageCalculatorInfo_json = self.below_the_fold['publicRecordsInfo']['mortgageCalculatorInfo']
        if 'monthlyHoaDues' in mortgageCalculatorInfo_json:
            return mortgageCalculatorInfo_json['monthlyHoaDues']
        else:
            return 0

    def get_home_insurance(self):
        return self.below_the_fold['publicRecordsInfo']['mortgageCalculatorInfo']['homeInsuranceRate']

    def get_elementary_school_rating(self):
        return None #self.below_the_fold['schoolsAndDistrictsInfo']['servingThisHomeSchools'][0]['greatSchoolsRating']

    def get_middle_school_rating(self):
        return None #self.below_the_fold['schoolsAndDistrictsInfo']['servingThisHomeSchools'][1]['greatSchoolsRating']

    def get_high_school_rating(self):
        return None #self.below_the_fold['schoolsAndDistrictsInfo']['servingThisHomeSchools'][2]['greatSchoolsRating']

    def get_year_built(self):
        return self.above_the_fold['addressSectionInfo']['yearBuilt']

    def get_location(self):
        lat_long_json = self.above_the_fold['addressSectionInfo']['latLong']
        return lat_long_json['latitude'], lat_long_json['longitude']

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
            city=self.get_city(),
            zip_code=self.get_zip_code(),
            days_on_market=self.get_num_days_on_market(),
            house_type=self.get_house_type(),
            location=self.get_location(),
            year_built=self.get_year_built(),
            elementary_rating=self.get_elementary_school_rating(),
            middle_rating=self.get_middle_school_rating(),
            high_rating=self.get_high_school_rating(),
            community=self.get_community(),
        )
        return house_data
