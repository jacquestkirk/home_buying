import collections

closing_cost_pct = 4  # percent of home value
repair_fund_multiplier = 1.5  # 1.5x rent per year
property_manager_pct = 10  # percent of rent
lease_finding_fees_pct = 1 / 12 * 100  # need to find a tenant once per year
vacancy_rate_pct = 5  # https://www.stessa.com/blog/rental-property-analysis-spreadsheet/

## Mortgage info
MortgageData = collections.namedtuple(
    'MortgageData',
    [
        'down_payment_pct',
        'yearly_interest_pct',
        'years'
    ]
)

mortgages = {
    'lee_anne_20_pct': MortgageData(
        down_payment_pct=20,
        yearly_interest_pct=4.375,
        years=30
    ),
    'all_cash': MortgageData(
        down_payment_pct=100,
        yearly_interest_pct=0,
        years=0
    )
}



