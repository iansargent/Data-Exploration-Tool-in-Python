
### Paths 
ACS_BASENAME = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/"



### Variable Titles 
ACS_ECON_METRICS = {
    # Employment
    "unemployment_rate": lambda df: df["DP03_0009PE"].mean() / 100,
    "pct_employed": lambda df: df["DP03_0004PE"].mean(),
    "pct_in_labor_force": lambda df: df["DP03_0002PE"].mean(),
    "pct_female_in_labor_force": lambda df: df["DP03_0011PE"].mean(),

    # Healthcare
    "pct_no_hc_coverage": lambda df: df["DP03_0099PE"].mean(),
    "pct_no_hc_coverage_u19": lambda df: df["DP03_0101PE"].mean(),
    "pct_public_hc_coverage": lambda df: df["DP03_0098PE"].mean() / 100,
    "pct_employed_no_hc_coverage": lambda df: df["DP03_0108PE"].mean(),

    # Income
    "income_per_capita": lambda df: df["DP03_0088E"].mean(),
    "median_family_income": lambda df: df["DP03_0086E"].mean(),
    "median_earnings": lambda df: df["DP03_0092E"].mean(),
    "male_earnings": lambda df: df["DP03_0093E"].mean(),
    "female_earnings": lambda df: df["DP03_0094E"].mean(),

    # Poverty
    "pct_people_below_pov": lambda df: df["DP03_0128PE"].mean() / 100,
    "pct_families_below_pov": lambda df: df["DP03_0119PE"].mean() / 100,
}

FAMILY_INCOME_COLUMNS = [
    "DP03_0076E", "DP03_0077E", "DP03_0078E", "DP03_0079E", "DP03_0080E",
    "DP03_0081E", "DP03_0082E", "DP03_0083E", "DP03_0084E", "DP03_0085E"
]

FAMILY_INCOME_LABELS = [
    "Under $10,000", "$10,000 - $14,999", "$15,000 - $24,999", "$25,000 - $34,999", "$35,000 - $49,999",
    "$50,000 - $74,999", "$75,000 - $99,999", "$100,000 - $149,999", "$150,000 - $199,999", "$200,000 +"
]


ACS_HOUSING_METRICS = {
    # Basic counts
    "total_units": lambda df: df["DP04_0001E"].sum(),
    "vacant_units": lambda df: df["DP04_0003E"].sum(),
    "occupied_units": lambda df: df["DP04_0002E"].sum(),

    # Vacancy & occupancy
    "pct_vacant": lambda df: df["DP04_0003E"].sum() / df["DP04_0001E"].sum(),
    "pct_occupied": lambda df: df["DP04_0002E"].sum() / df["DP04_0001E"].sum(),

    # Tenure
    "owned_units": lambda df: df["DP04_0046E"].sum(),
    "rented_units": lambda df: df["DP04_0047E"].sum(),
    "pct_owned": lambda df: df["DP04_0046E"].sum() / df["DP04_0002E"].sum(),
    "pct_rented": lambda df: df["DP04_0047E"].sum() / df["DP04_0002E"].sum(),

    # Monthly ownership & rent costs
    "avg_SMOC_mortgaged": lambda df: df["DP04_0101E"].mean(),
    "avg_SMOC2_non_mortgaged": lambda df: df["DP04_0109E"].mean(),
    "avg_gross_rent": lambda df: df["DP04_0134E"].mean(),

    # Rent burden
    "units_paying_rent": lambda df: df["DP04_0126E"].sum(),
    "rent_burden35": lambda df: df["DP04_0142E"].sum(),
    "pct_rent_burden35": lambda df: (df["DP04_0142E"].sum() / df["DP04_0126E"].sum()) * 100,

    # Units by structure type
    "one_unit_detached": lambda df: df["DP04_0007E"].sum(),
    "one_unit_attached": lambda df: df["DP04_0008E"].sum(),
    "one_unit_total": lambda df: df["DP04_0007E"].sum() + df["DP04_0008E"].sum(),
    "two_units": lambda df: df["DP04_0009E"].sum(),
    "three_or_four_units": lambda df: df["DP04_0010E"].sum(),
    "five_to_nine_units": lambda df: df["DP04_0011E"].sum(),
    "ten_to_nineteen_units": lambda df: df["DP04_0012E"].sum(),
    "twenty_or_more_units": lambda df: df["DP04_0013E"].sum(),
    "mobile_home": lambda df: df["DP04_0014E"].sum(),
    "boat_rv_van_etc": lambda df: df["DP04_0015E"].sum(),
}