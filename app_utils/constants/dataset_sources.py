from app_utils.census import tidy_census

ECON_SOURCES = {
    "econ_2023": "VT_ECONOMIC_ALL.fgb",
    "econ_2023_tidy": ("VT_ECONOMIC_ALL.fgb", tidy_census),
    "unemployment": "unemployment_rate_by_year.csv",
    "median_earnings": "median_earnings_by_year.csv",
    "commute_time": "commute_time_by_year.csv",
    "commute_habits": "commute_habits_by_year.csv",
}

HOUSING_SOURCES =  {
    "housing_2023" : "VT_HOUSING_ALL.fgb",
    "housing_2023_tidy" : ("VT_HOUSING_ALL.fgb", tidy_census),

    "housing_2013" : "VT_HOUSING_ALL_2013.fgb",
    "housing_2013_tidy" : ("VT_HOUSING_ALL_2013.fgb", tidy_census),

    "median_value" : "med_home_value_by_year.csv",
    "median_smoc" : "med_smoc_by_year.csv",
    "vt_historic_population": "VT_Historic_Population.csv"
}

DEMO_SOURCES = {
    "demogs_2023": "VT_DEMOGRAPHIC_ALL.fgb",
    "demogs_2023_tidy": ("VT_DEMOGRAPHIC_ALL.fgb", tidy_census),
}

SOCIAL_SOURCES = {
    "social_2023": "VT_SOCIAL_ALL.fgb",
    "social_2023_tidy": ("VT_SOCIAL_ALL.fgb", tidy_census),
}


COMBINED_CENSUS = {
    "Housing": ("census_housing", "housing_2023_tidy"),
    "Economic": ("census_economics", "econ_2023_tidy"),
    "Demographic": ("census_demographics", "demogs_2023_tidy"),
    "Social": ("census_social", "social_2023_tidy"),
}
