
### Paths 
ACS_BASENAME = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/"



### Variable Titles 
ACS_METRICS = {
    # employment
    "unemployment_rate": ("DP03_0009PE", 100),
    "pct_employed": ("DP03_0004PE", 1),
    "pct_in_labor_force": ("DP03_0002PE", 1),
    "pct_female_in_labor_force": ("DP03_0011PE", 1),

    # Healthcare
    "pct_no_hc_coverage": ("DP03_0099PE", 1),
    "pct_no_hc_coverage_u19": ("DP03_0101PE", 1),
    "pct_public_hc_coverage": ("DP03_0098PE", 100),
    "pct_employed_no_hc_coverage": ("DP03_0108PE", 1),

    # Income
    "income_per_capita": ("DP03_0088E", 1),
    "median_family_income": ("DP03_0086E", 1),
    "median_earnings": ("DP03_0092E", 1),
    "male_earnings": ("DP03_0093E", 1),
    "female_earnings": ("DP03_0094E", 1),
    
    # Poverty
    "pct_people_below_pov": ("DP03_0128PE", 100),
    "pct_families_below_pov": ("DP03_0119PE", 100),
}

FAMILY_INCOME_COLUMNS = [
    "DP03_0076E", "DP03_0077E", "DP03_0078E", "DP03_0079E", "DP03_0080E",
    "DP03_0081E", "DP03_0082E", "DP03_0083E", "DP03_0084E", "DP03_0085E"
]

FAMILY_INCOME_LABELS = [
    "Under $10,000", "$10,000 - $14,999", "$15,000 - $24,999", "$25,000 - $34,999", "$35,000 - $49,999",
    "$50,000 - $74,999", "$75,000 - $99,999", "$100,000 - $149,999", "$150,000 - $199,999", "$200,000 +"
]


