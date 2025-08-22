### Paths
ACS_BASENAME = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/"


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
    "DP03_0076E",
    "DP03_0077E",
    "DP03_0078E",
    "DP03_0079E",
    "DP03_0080E",
    "DP03_0081E",
    "DP03_0082E",
    "DP03_0083E",
    "DP03_0084E",
    "DP03_0085E",
]

FAMILY_INCOME_LABELS = [
    "Under $10,000",
    "$10,000 - $14,999",
    "$15,000 - $24,999",
    "$25,000 - $34,999",
    "$35,000 - $49,999",
    "$50,000 - $74,999",
    "$75,000 - $99,999",
    "$100,000 - $149,999",
    "$150,000 - $199,999",
    "$200,000 +",
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
    "avg_SMOC_non_mortgaged": lambda df: df["DP04_0109E"].mean(),
    "avg_gross_rent": lambda df: df["DP04_0134E"].mean(),
    # Rent burden
    "units_paying_rent": lambda df: df["DP04_0126E"].sum(),
    "rent_burden35": lambda df: df["DP04_0142E"].sum(),
    "pct_rent_burden35": lambda df: (df["DP04_0142E"].sum() / df["DP04_0126E"].sum())
    * 100,
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

HOUSING_YEAR_LABELS = [
    "1939 and Prior",
    "1940 - 1949",
    "1950 - 1959",
    "1960 - 1969",
    "1970 - 1979",
    "1980 - 1989",
    "1990 - 1999",
    "2000 - 2009",
    "2010 - 2019",
    "2020 - Present",
]

NEW_HOUSING_UNIT_COLUMNS = [
    "DP04_0026E",
    "DP04_0025E",
    "DP04_0024E",
    "DP04_0023E",
    "DP04_0022E",
    "DP04_0021E",
    "DP04_0020E",
    "DP04_0019E",
    "DP04_0018E",
    "DP04_0017E",
]

POPULATION_YEAR_LABELS = [1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]


ACS_DEMOGRAPHIC_METRICS = {
    # Basic counts
    "total_population": lambda df: df["DP05_0001E"].sum(),
    # Sex
    "pop_male": lambda df: df["DP05_0002E"].sum(),
    "pct_male": lambda df: df["DP05_0002PE"].mean(),
    "pop_female": lambda df: df["DP05_0003E"].sum(),
    "pct_female": lambda df: df["DP05_0003PE"].mean(),
    "sex_ratio": lambda df: df["DP05_0004E"].mean(),
    # Age
    "pct_pop_under_18": lambda df: df["DP05_0019PE"].mean(),
    "pct_pop_65_and_over": lambda df: df["DP05_0024PE"].mean(),
    "median_age": lambda df: df["DP05_0018E"].mean(),
    "dependency_ratio": lambda df: (
        # Dependents
        (
            df["DP05_0005E"].sum()  # Under 5 years
            + df["DP05_0006E"].sum()  # 5 to 9 years
            + df["DP05_0007E"].sum()  # 10 to 14 years
            + df["DP05_0015E"].sum()  # 65 to 74 years
            + df["DP05_0016E"].sum()  # 75 to 84 years
            + df["DP05_0017E"].sum()  # 85+ years
        )
        /
        # Working Age
        (
            df["DP05_0008E"].sum()  # 15 to 19 years
            + df["DP05_0009E"].sum()  # 20 to 24 years
            + df["DP05_0010E"].sum()  # 25 to 34 years
            + df["DP05_0011E"].sum()  # 35 to 44 years
            + df["DP05_0012E"].sum()  # 45 to 54 years
            + df["DP05_0013E"].sum()  # 55 to 59 years
            + df["DP05_0014E"].sum()  # 60 to 64 years
        )
    )
    * 100,
    # Voting-age citizens
    "pop_voting_age_citizen": lambda df: df["DP05_0087E"].sum(),
    "citizen_voting_age_pct_male": lambda df: df["DP05_0088PE"].mean(),
    "citizen_voting_age_pct_female": lambda df: df["DP05_0089PE"].mean(),
}

AGE_GROUP_LABELS = [
    "Under 5",
    "5 to 9",
    "10 to 14",
    "15 to 19",
    "20 to 24",
    "25 to 34",
    "35 to 44",
    "45 to 54",
    "55 to 59",
    "60 to 64",
    "65 to 74",
    "75 to 84",
    "85 and over",
]

AGE_GROUP_COLUMNS = [
    "DP05_0005E",
    "DP05_0006E",
    "DP05_0007E",
    "DP05_0008E",
    "DP05_0009E",
    "DP05_0010E",
    "DP05_0011E",
    "DP05_0012E",
    "DP05_0013E",
    "DP05_0014E",
    "DP05_0015E",
    "DP05_0016E",
    "DP05_0017E",
]

RACE_LABELS = ["White", "Black", "Hispanic", "AI/AN", "Asian", "NH/PI", "Other"]

RACE_COLUMNS = [
    "DP05_0037E",
    "DP05_0038E",
    "DP05_0071E",
    "DP05_0039E",
    "DP05_0044E",
    "DP05_0052E",
    "DP05_0057E",
]


ACS_SOCIAL_METRICS = {
    "example": lambda df: df["DP02_0001E"].sum(),
}
