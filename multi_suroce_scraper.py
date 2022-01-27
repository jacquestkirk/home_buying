import zillow_scraper
import redfin_scraper
import collections

# a collection of data harvested from Zillow
HouseDataMultiSource = collections.namedtuple(
    'HouseDataMultiSource',
    [
        'price',
        'property_tax',
        'home_insurance',
        'hoa',
        'rent_zestimate',
        'rent_restimate',
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


class MultiSourceScraper:
    def __init__(self, address):
        self.zillow_scraper = zillow_scraper.ZillowScraper(address)
        self.redfin_scraper = redfin_scraper.RedfinScraper(address)

    def get_data(self):
        house_data = HouseDataMultiSource(
            price=self.redfin_scraper.get_home_price(),
            property_tax=max(self.zillow_scraper.get_tax_rate(), self.zillow_scraper.get_tax_rate()),
            home_insurance=self.redfin_scraper.get_home_insurance(),
            hoa=self.redfin_scraper.get_hoa(),
            rent_zestimate=self.zillow_scraper.get_rental_value(),
            rent_restimate=self.redfin_scraper.get_rental_value(),
            beds=self.redfin_scraper.get_num_beds(),
            baths=self.redfin_scraper.get_num_baths(),
            area_sq_ft=self.redfin_scraper.get_num_square_feet(),
            address=self.redfin_scraper.get_address(),
            city=self.zillow_scraper.get_city(),
            zip_code=self.redfin_scraper.get_zip_code(),
            community=self.redfin_scraper.get_community(),
            days_on_market=self.zillow_scraper.get_num_days_on_market(),
            house_type=self.redfin_scraper.get_house_type(),
            location=self.redfin_scraper.get_location(),
            year_built=self.redfin_scraper.get_year_built(),
            elementary_rating=self.zillow_scraper.get_elementary_school_rating(),
            middle_rating=self.zillow_scraper.get_middle_school_rating(),
            high_rating=self.zillow_scraper.get_high_school_rating()
        )
        return house_data



