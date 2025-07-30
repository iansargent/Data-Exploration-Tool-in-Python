"""
Open Research Community Accelorator
Vermont Data App

Census Utility Functions
"""

import pandas as pd

import requests
import pyogrio  
import io
from app_utils.data_loading import load_data

import requests
from bs4 import BeautifulSoup


def split_name_col(census_gdf):
    """
    Splits the "NAME" columns in the census datasets into 
    "Jurisdiction" and "County" columns.

    @param census_gdf: A census style GeoDataFrame with a "NAME" column.
    @return: The cleaned dataset with the split "NAME" column.
    """
    # Split the NAME column
    census_gdf[['Jurisdiction', 'County']] = census_gdf['NAME'].str.extract(r'^(.*?),\s*(.*?) County,')
    # Drop the original NAME column if desired
    census_gdf = census_gdf.drop(columns='NAME')

    return census_gdf


def get_census_cols():
    r = requests.get("https://api.census.gov/data/2019/acs/acs5/profile/variables.html")
    soup = BeautifulSoup(r.content, "html.parser") 

    # get table headers as keys
    keys = [th.get_text(strip=True, separator=" ")
            for tr in soup.find_all("tr")
            for th in tr.find_all("th")]
    
    #build rows 
    rows = []
    for tr in soup.find_all("tr"):
        cells = [td.get_text(strip=True, separator=" ") for td in tr.find_all("td")] # cols
        if cells:
            rows.append(cells)
    
    df = pd.DataFrame(rows, columns=keys)
    df = df[['Name', 'Label']].copy()
    df.dropna(inplace=True)
    return df


def split_to_cols(s, cols):
    parts = [p.strip() for p in s.split("!!")]
    
    while len(parts) < len(cols):
        parts.append("")

    first = parts[0:len(cols)-1]
    second = parts[len(cols)-1:]
    second = [": ".join(second)]
    
    return first + second


def relabel_census_cols(df):
    # Splits apart the labels so we can filter across them 
    cols = ["Measure", "Category", "Subcategory", "Variable"]
    
    # Keep only rows where the label is structured by "!!" (Issues with "Geography" rows)
    df_clean = df[df["Label"].str.contains("!!")].copy()

    # Reset index to avoid merging issues
    df_clean.reset_index(drop=True, inplace=True)
    
    splits = df_clean["Label"].apply(lambda x: list(split_to_cols(x, cols)))
    splits_df = pd.DataFrame(splits.tolist(), columns=cols)
    
    # Create the total categories
    splits_df.loc[ 
        (splits_df['Subcategory'].notna()) & (splits_df['Variable']==""),
        "Variable"] = "Total"
    
    name_df = pd.concat([df_clean, splits_df], axis=1)

    return name_df


def merge_census_cols(name_df, data_gdf):
    # Melt the gdf into tidy format
    id_vars = ['GEOID', 'geometry', 'Jurisdiction', 'County',]
    data_gdf[id_vars]
    df_long = data_gdf.melt(
        id_vars=id_vars, 
        value_vars=data_gdf.columns.difference(id_vars),
        var_name="Code",
        value_name="Value")
    
    # Merge to get the right names and drop the cols
    return pd.merge(
        left=df_long,
        right=name_df,
        left_on="Code",
        right_on="Name"
    ).drop(columns=["Code", "Name", "Label"])


def rename_and_merge_census_cols(census_gdf):
    # wrapper func to rename codes in func
    # TODO: consider saving renamed census codes permanently
    name_df = get_census_cols()
    name_df = relabel_census_cols(name_df)
    return merge_census_cols(name_df, census_gdf)


def get_geography_title(county, jurisdiction):
    # For the plot title, dynamically change the area of interest based on user filter selections
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        title_geo = "Vermont (Statewide)"
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        title_geo = f"{county} County"
    elif jurisdiction != "All Jurisdictions":
        title_geo = f"{jurisdiction}"
    
    return title_geo



def calculate_delta_values(filtered_gdf_2023, baseline, filtered_gdf_2013, housing_gdf):

    ##TODO simplify this logic into something that can handle whatever data is thrown at it. 
    if baseline == "2013 Local Data (10-Year Change)":
        total_units_2023 = filtered_gdf_2023['DP04_0001E'].sum()
        total_units_2013 = filtered_gdf_2013['DP04_0001E'].sum()
        total_units_delta = total_units_2023 - total_units_2013

        vacant_units_2023 = filtered_gdf_2023['DP04_0003E'].sum()
        vacant_units_2013 = filtered_gdf_2013['DP04_0003E'].sum()
        pct_vac_2023 = (vacant_units_2023 / total_units_2023) * 100
        pct_vac_2013 = (vacant_units_2013 / total_units_2013) * 100
        vacant_units_delta = vacant_units_2023 - vacant_units_2013
        pct_vac_delta = pct_vac_2023 - pct_vac_2013

        occupied_units_2023 = filtered_gdf_2023['DP04_0002E'].sum()
        occupied_units_2013 = filtered_gdf_2013['DP04_0002E'].sum()
        pct_occ_2023 = (occupied_units_2023 / total_units_2023) * 100
        pct_occ_2013 = (occupied_units_2013 / total_units_2013) * 100
        occupied_units_delta = occupied_units_2023 - occupied_units_2013
        pct_occ_delta = pct_occ_2023 - pct_occ_2013

        owned_units_2023 = filtered_gdf_2023['DP04_0046E'].sum()
        owned_units_2013 = filtered_gdf_2013['DP04_0045E'].sum()
        pct_own_2023 = (owned_units_2023 / occupied_units_2023) * 100
        pct_own_2013 = (owned_units_2013 / occupied_units_2013) * 100
        owned_units_delta = owned_units_2023 - owned_units_2013
        pct_own_delta = pct_own_2023 - pct_own_2013

        # Renter-Occupied Units
        rented_units_2023 = filtered_gdf_2023['DP04_0047E'].sum()
        rented_units_2013 = filtered_gdf_2013['DP04_0046E'].sum()
        pct_rent_2023 = (rented_units_2023 / occupied_units_2023) * 100
        pct_rent_2013 = (rented_units_2013 / occupied_units_2013) * 100
        rented_units_delta = rented_units_2023 - rented_units_2013
        pct_rent_delta = pct_rent_2023 - pct_rent_2013

        # Average Median Monthly Owner Cost (SMOC) (For units with a mortgage)
        avg_med_SMOC_2023 = filtered_gdf_2023['DP04_0101E'].mean()
        avg_med_SMOC_2013 = filtered_gdf_2013['DP04_0100E'].mean()
        avg_med_SMOC_delta = avg_med_SMOC_2023 - avg_med_SMOC_2013

        avg_med_SMOC2_2023 = filtered_gdf_2023['DP04_0109E'].mean()
        avg_med_SMOC2_2013 = filtered_gdf_2013['DP04_0107E'].mean()
        avg_med_SMOC2_delta = avg_med_SMOC2_2023 - avg_med_SMOC2_2013

        # Average Median Gross Rent
        avg_med_gross_rent_2023 = filtered_gdf_2023['DP04_0134E'].mean()
        avg_med_gross_rent_2013 = filtered_gdf_2013['DP04_0132E'].mean()
        avg_med_gross_rent_delta = avg_med_gross_rent_2023 - avg_med_gross_rent_2013

        units_paying_rent_2023 = filtered_gdf_2023['DP04_0126E'].sum()
        units_paying_rent_2013 = filtered_gdf_2013['DP04_0124E'].sum()
        rent_burden35_2023 = filtered_gdf_2023['DP04_0142E'].sum()
        rent_burden35_2013 = filtered_gdf_2013['DP04_0140E'].sum()
        rent_burden35_pct_2023 = (rent_burden35_2023 / units_paying_rent_2023) * 100
        rent_burden35_pct_2013 = (rent_burden35_2013 / units_paying_rent_2013) * 100
        rent_burden35_delta = rent_burden35_2023 - rent_burden35_2013
        rent_burden35_pct_delta = rent_burden35_pct_2023 - rent_burden35_pct_2013
    
    elif baseline == "2023 Vermont Statewide Averages":
        total_units_2023 = filtered_gdf_2023['DP04_0001E'].sum()
        total_units_state = housing_gdf['DP04_0001E'].sum()
        
        occupied_units_2023 = filtered_gdf_2023['DP04_0002E'].sum()
        occupied_units_state = housing_gdf['DP04_0002E'].sum()
        pct_occ_2023 = (occupied_units_2023 / total_units_2023) * 100
        pct_occ_state = (occupied_units_state / total_units_state) * 100
        pct_occ_delta = pct_occ_2023 - pct_occ_state

        vacant_units_2023 = filtered_gdf_2023['DP04_0003E'].sum()
        pct_vac_2023 = (vacant_units_2023 / total_units_2023) * 100
        vacant_units_state = housing_gdf['DP04_0003E'].sum()
        pct_vac_state = (vacant_units_state / total_units_state) * 100
        pct_vac_delta = pct_vac_2023 - pct_vac_state

        # Owner-Occupied Units
        owned_units_2023 = filtered_gdf_2023['DP04_0046E'].sum()
        owned_units_state = housing_gdf['DP04_0046E'].sum()
        pct_own_2023 = (owned_units_2023 / occupied_units_2023) * 100
        pct_own_state = (owned_units_state / occupied_units_state) * 100
        pct_own_delta = pct_own_2023 - pct_own_state

        # Renter-Occupied Units
        rented_units_2023 = filtered_gdf_2023['DP04_0047E'].sum()
        rented_units_state = housing_gdf['DP04_0047E'].sum()
        pct_rent_2023 = (rented_units_2023 / occupied_units_2023) * 100
        pct_rent_state = (rented_units_state / occupied_units_state) * 100
        pct_rent_delta = pct_rent_2023 - pct_rent_state

        avg_med_val_2023 = filtered_gdf_2023['DP04_0089E'].mean()
        avg_med_val_state = housing_gdf['DP04_0089E'].mean()
        avg_med_val_delta = avg_med_val_2023 - avg_med_val_state

        # Average Median Monthly Owner Cost (SMOC) (For units with a mortgage)
        avg_med_SMOC_2023 = filtered_gdf_2023['DP04_0101E'].mean()
        avg_med_SMOC_state = housing_gdf['DP04_0101E'].mean()
        avg_med_SMOC_delta = avg_med_SMOC_2023 - avg_med_SMOC_state

        # Average Median Monthly Owner Cost (SMOC) (For units without a mortgage)
        avg_med_SMOC2_2023 = filtered_gdf_2023['DP04_0109E'].mean()
        avg_med_SMOC2_state = housing_gdf['DP04_0109E'].mean()
        avg_med_SMOC2_delta = avg_med_SMOC2_2023 - avg_med_SMOC2_state

        # Average Median Gross Rent
        avg_med_gross_rent_2023 = filtered_gdf_2023['DP04_0134E'].mean()
        avg_med_gross_rent_state = housing_gdf['DP04_0134E'].mean()
        avg_med_gross_rent_delta = avg_med_gross_rent_2023 - avg_med_gross_rent_state

        # Count of Households where rent takes up 35% or more of their household income
        units_paying_rent_2023 = filtered_gdf_2023['DP04_0126E'].sum()
        units_paying_rent_state = housing_gdf['DP04_0126E'].sum()
        rent_burden35_2023 = filtered_gdf_2023['DP04_0142E'].sum()
        rent_burden35_state = housing_gdf['DP04_0142E'].sum()
        rent_burden35_pct_2023 = (rent_burden35_2023 / units_paying_rent_2023) * 100
        rent_burden35_pct_state = (rent_burden35_state / units_paying_rent_state) * 100
        rent_burden35_pct_delta = rent_burden35_pct_2023 - rent_burden35_pct_state

    return {
        "total_units_delta": total_units_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "vacant_units_delta": vacant_units_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "pct_vac_delta": pct_vac_delta,
        "occupied_units_delta": occupied_units_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "pct_occ_delta": pct_occ_delta,
        "owned_units_delta": owned_units_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "pct_own_delta": pct_own_delta,
        "rented_units_delta": rented_units_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "pct_rent_delta": pct_rent_delta,
        "avg_med_val_delta": avg_med_val_delta if baseline == "2023 Vermont Statewide Averages" else None,
        "avg_med_SMOC_delta": avg_med_SMOC_delta,
        "avg_med_SMOC2_delta": avg_med_SMOC2_delta,
        "avg_med_gross_rent_delta": avg_med_gross_rent_delta,
        "rent_burden35_delta": rent_burden35_delta if baseline == "2013 Local Data (10-Year Change)" else None,
        "rent_burden35_pct_delta": rent_burden35_pct_delta
    }

