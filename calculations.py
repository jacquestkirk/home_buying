import copy
import constants
import zillow_scraper

class MonthData:
    def __init__(
        self,
        month,
        loan_amount,
        interest,
        equity_added,
        total_equity,
        monthly_profit,
        cumulative_profit
    ):
        self.month = month
        self.loan_amount = loan_amount
        self.interest = interest
        self.equity_added = equity_added
        self.total_equity = total_equity
        self.monthly_profit = monthly_profit
        self.cumulative_profit = cumulative_profit


def calculate_mortgage(house_price, down_payment_pct, yearly_interest_pct, years):
    """"""
    if down_payment_pct >= 100:
        return 0  # no mortgage if paid in full
    loan_amount = house_price * (1 - down_payment_pct/100)
    months = years * 12
    monthly_interest = yearly_interest_pct / 12 / 100
    numerator = (1 + monthly_interest) ** months
    denominator = (numerator - 1)
    return loan_amount * monthly_interest * numerator / denominator


def calculate_upfront_cost(
        house_price,
        down_payment_pct,
        reserve_cash=0,
        repairs=0,
        closing_cost_pct=constants.closing_cost_pct,
):
    closing_costs_dollars = house_price * closing_cost_pct / 100
    down_payment_dollars = house_price * down_payment_pct / 100
    return closing_costs_dollars + down_payment_dollars + reserve_cash + repairs


class HouseCalculator:
    def __init__(
        self,
        zillow_data: zillow_scraper.ZillowData,
        mortgage_data: constants.MortgageData = constants.mortgages['lee_anne_20_pct'],
        repair_fund_multiplier=constants.repair_fund_multiplier,
        property_manager_pct=constants.property_manager_pct,
        lease_finding_fees=constants.lease_finding_fees_pct,
        vacancy_rate_pct=constants.vacancy_rate_pct,
        closing_cost_pct=constants.closing_cost_pct,
    ):
        self.zillow_data = zillow_data
        self.mortgage_data = mortgage_data
        self.repair_fund_multiplier = repair_fund_multiplier
        self.property_manager_pct = property_manager_pct
        self.lease_finding_fees = lease_finding_fees
        self.vacancy_rate_pct = vacancy_rate_pct
        self.closing_cost_pct = closing_cost_pct
        self.time_series = self.calculate_time_series()

    def calculate_cash_flow(self):
        return calculate_cash_flow(self.zillow_data, self.mortgage_data, self.vacancy_rate_pct)

    def calculate_no_mortgage_cash_flow(self):
        mortgage_data = constants.mortgages['all_cash']
        return calculate_cash_flow(self.zillow_data, mortgage_data, self.vacancy_rate_pct)

    def find_rent_change_to_zero_cash_flow(self):
        step_size = 10  # dollars
        # make a copy of zillow_data to avoid changing the original
        zillow_data_copy = copy.deepcopy(self.zillow_data)

        # Increase rent until cashflow is not negative
        while calculate_cash_flow(zillow_data_copy, self.mortgage_data, self.vacancy_rate_pct) < 0:
            zillow_data_copy = zillow_data_copy._replace(rent_zestimate=zillow_data_copy.rent_zestimate + step_size)

        return zillow_data_copy.rent_zestimate

    def find_rent_change_to_zero_cash_flow_pct(self):
        return (self.find_rent_change_to_zero_cash_flow() - self.zillow_data.rent_zestimate) / self.zillow_data.rent_zestimate

    def calculate_depreciation_tax_deduction(self):
        # https://www.millionacres.com/taxes/real-estate-tax-deductions/a-beginners-guide-to-investment-property-income-tax-deductions/

        return self.zillow_data.price / 27.5 / 12

    def calculate_time_series(self):
        loan_amount = self.zillow_data.price * (1 - self.mortgage_data.down_payment_pct/100)
        time_series = [MonthData(
            month=0,
            loan_amount=loan_amount,
            interest=self.mortgage_data.yearly_interest_pct/12/100 * loan_amount,
            equity_added=0,
            total_equity=self.zillow_data.price * self.mortgage_data.down_payment_pct / 100,
            monthly_profit=0,
            cumulative_profit= -(self.zillow_data.price * self.closing_cost_pct / 100)
        )]

        total_months = self.mortgage_data.years * 12
        mortgage_payment = calculate_mortgage(
            house_price=self.zillow_data.price,
            down_payment_pct=self.mortgage_data.down_payment_pct,
            yearly_interest_pct=self.mortgage_data.yearly_interest_pct,
            years=self.mortgage_data.years
        )

        for month in range(total_months):
            previous_month = time_series[month]
            new_loan_amount = previous_month.loan_amount + previous_month.interest - mortgage_payment
            interest_payment_this_month = self.mortgage_data.yearly_interest_pct/12/100 * new_loan_amount
            equity_added = mortgage_payment - interest_payment_this_month
            monthly_profit = self.calculate_cash_flow() + equity_added
            new_month = MonthData(
                month=previous_month.month + 1,
                loan_amount=new_loan_amount,
                interest=interest_payment_this_month,
                equity_added=equity_added,
                total_equity=previous_month.total_equity + equity_added,
                monthly_profit=monthly_profit,
                cumulative_profit=previous_month.cumulative_profit + monthly_profit
            )
            time_series.append(new_month)
        return time_series


def calculate_best_case_non_mortgage_costs(
    zillow_data: zillow_scraper.ZillowData,
    repair_fund_multiplier=constants.repair_fund_multiplier,
    property_manager_pct=constants.property_manager_pct
):
    calculate_non_mortgage_costs(
        zillow_data=zillow_data,
        repair_fund_multiplier=repair_fund_multiplier,
        property_manager_pct=property_manager_pct,
        lease_finding_fees=0
    )


def calculate_non_mortgage_costs(
    zillow_data: zillow_scraper.ZillowData,
    repair_fund_multiplier=constants.repair_fund_multiplier,
    property_manager_pct=constants.property_manager_pct,
    lease_finding_fees=constants.lease_finding_fees_pct,
):
    return (
        zillow_data.hoa +
        zillow_data.property_tax +
        zillow_data.home_insurance +
        zillow_data.rent_zestimate * repair_fund_multiplier / 12 +
        zillow_data.rent_zestimate * property_manager_pct / 100 +
        zillow_data.rent_zestimate * lease_finding_fees / 100
    )


def calculate_adjusted_rental_income(
    zillow_data: zillow_scraper.ZillowData,
    vacancy_rate_pct=constants.vacancy_rate_pct
):
    return zillow_data.rent_zestimate * (1 - vacancy_rate_pct / 100)


def calculate_monthly_payments(
    zillow_data: zillow_scraper.ZillowData,
    mortgage_data: constants.MortgageData = constants.mortgages['lee_anne_20_pct']
):
    mortgage = calculate_mortgage(
        house_price=zillow_data.price,
        down_payment_pct=mortgage_data.down_payment_pct,
        yearly_interest_pct=mortgage_data.yearly_interest_pct,
        years=mortgage_data.years
    )

    non_mortgage = calculate_non_mortgage_costs(zillow_data)

    return mortgage + non_mortgage


def calculate_cash_flow(
    zillow_data: zillow_scraper.ZillowData,
    mortgage_data: constants.MortgageData = constants.mortgages['lee_anne_20_pct'],
    vacancy_rate_pct=constants.vacancy_rate_pct
):
    return(
        calculate_adjusted_rental_income(zillow_data, vacancy_rate_pct) -
        calculate_monthly_payments(zillow_data, mortgage_data)
    )
