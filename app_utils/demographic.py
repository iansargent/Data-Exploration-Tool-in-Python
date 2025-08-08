import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.df_filtering import filter_snapshot_data
from app_utils.color import get_text_color
from app_utils.plot import donut_chart, bar_chart


def demographic_snapshot_header():
    st.subheader("Demographic Snapshot")
    # Include a source for the dataset (Census DP05 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP05: Demographic and Housing Estimates - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def demog_df_metric_dict(filtered_gdf_2023):
# Define a dictionary of metrics to display in the snapshot
    metrics = {
        # SEX and AGE Metrics
        "total_population": filtered_gdf_2023['DP05_0001E'].mean(),
        "pop_male": filtered_gdf_2023['DP05_0002E'].sum(),
        "pct_male": filtered_gdf_2023['DP05_0002PE'].mean(),
        "pop_female": filtered_gdf_2023['DP05_0003E'].sum(),
        "pct_female": filtered_gdf_2023['DP05_0003PE'].mean(),
        "pct_pop_under_18": filtered_gdf_2023['DP05_0019PE'].mean(),
        "pct_pop_65_and_over": filtered_gdf_2023['DP05_0024PE'].mean(),
        "median_age": filtered_gdf_2023['DP05_0018E'].mean(),

        # For every 100 working-age people, there are X dependents
        # A dependency ratio of 50 means that each working-age person must support about half a dependent (on average)
        "dependency_ratio": (
            # Dependents
            (
                filtered_gdf_2023['DP05_0005E'].sum() +  # Under 5 years
                filtered_gdf_2023['DP05_0006E'].sum() +  # 5 to 9 years
                filtered_gdf_2023['DP05_0007E'].sum() +  # 10 to 14 years
                filtered_gdf_2023['DP05_0015E'].sum() +  # 65 to 74 years
                filtered_gdf_2023['DP05_0016E'].sum() +  # 75 to 84 years
                filtered_gdf_2023['DP05_0017E'].sum()    # 85+ years
            ) / 
            # Working Age
            (
                filtered_gdf_2023['DP05_0008E'].sum() +  # 15 to 19 years
                filtered_gdf_2023['DP05_0009E'].sum() +  # 20 to 24 years
                filtered_gdf_2023['DP05_0010E'].sum() +  # 25 to 34 years
                filtered_gdf_2023['DP05_0011E'].sum() +  # 35 to 44 years
                filtered_gdf_2023['DP05_0012E'].sum() +  # 45 to 54 years
                filtered_gdf_2023['DP05_0013E'].sum() +  # 55 to 59 years
                filtered_gdf_2023['DP05_0014E'].sum()    # 60 to 64 years
            )
        ) * 100,

        # CITIZEN/VOTING AGE metrics
        "pop_voting_age_citizen": filtered_gdf_2023["DP05_0087E"].sum(),
        "citizen_voting_age_pct_male": filtered_gdf_2023["DP05_0088PE"].mean(),
        "citizen_voting_age_pct_female": filtered_gdf_2023["DP05_0089PE"].mean(),
    }

    # Define a dictionary of DataFrames to plot in the snapshot
    dfs = {
        "age_dist": pd.DataFrame({
            "Age Group": [
                "Under 5", "5 to 9", "10 to 14", "15 to 19", "20 to 24",
                "25 to 34", "35 to 44", "45 to 54", "55 to 59", "60 to 64",
                "65 to 74", "75 to 84", "85 and over"], 
            "Population": [
                filtered_gdf_2023['DP05_0005E'].sum(),
                filtered_gdf_2023['DP05_0006E'].sum(),
                filtered_gdf_2023['DP05_0007E'].sum(),
                filtered_gdf_2023['DP05_0008E'].sum(),
                filtered_gdf_2023['DP05_0009E'].sum(),
                filtered_gdf_2023['DP05_0010E'].sum(),
                filtered_gdf_2023['DP05_0011E'].sum(),
                filtered_gdf_2023['DP05_0012E'].sum(),
                filtered_gdf_2023['DP05_0013E'].sum(),
                filtered_gdf_2023['DP05_0014E'].sum(),
                filtered_gdf_2023['DP05_0015E'].sum(),
                filtered_gdf_2023['DP05_0016E'].sum(),
                filtered_gdf_2023['DP05_0017E'].sum()]}),
        
        "race_dist": pd.DataFrame({
            "Race/Ethnicity": [
                "White",
                "Black",
                "Hispanic",
                "AI/AN",
                "Asian",
                "NH/PI",
                "Other"
            ],
            "Population": [
                filtered_gdf_2023['DP05_0037E'].sum(), 
                filtered_gdf_2023['DP05_0038E'].sum(),
                filtered_gdf_2023['DP05_0071E'].sum(),
                filtered_gdf_2023['DP05_0039E'].sum(),
                filtered_gdf_2023['DP05_0044E'].sum(),
                filtered_gdf_2023['DP05_0052E'].sum(),
                filtered_gdf_2023['DP05_0057E'].sum()]})
        }

    return metrics, dfs


def demographic_snapshot(demog_dfs):
    # Display the Category Header with Data Source
    demographic_snapshot_header()
    
    # Filter the dataframes using select boxes for "County" and "Jurisdiction"
    filtered_dfs, selected_values = filter_snapshot_data(demog_dfs, key_df=demog_dfs['demogs_2023'])

    # Get the title of the geography for plotting
    title_geo = get_geography_title(selected_values)
    
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="demographic_snapshot")
    metrics, plot_dfs = demog_df_metric_dict(filtered_dfs["demogs_2023"])

    # Snapshot sections
    ## TODO: maybe better to run all of these with **kwargs, or just all take the same args, idk
    # render_sex(demog_dfs, metrics, filtered_dfs, title_geo)
    # render_age(metrics, title_geo, plot_dfs, text_color)
    # render_race(metrics, filtered_dfs, title_geo, plot_dfs)
    # render_voting_age(metrics, title_geo, plot_dfs, text_color)

    # The SEX and AGE Section
    st.subheader("Sex and Age")
    
    age_col1, _, age_col2 = st.columns([6, 0.5, 2])

    age_dist_bar_chart = bar_chart(
        source=plot_dfs["age_dist"], title_geo=title_geo, XcolumnName="Age Group", YcolumnName="Population",
        XlabelAngle=0, fillColor="steelblue", height=500, barWidth=45, distribution=True, labelFontSize=12,
        title="Age Distribution")
    age_col1.altair_chart(age_dist_bar_chart, use_container_width=True)

    age_col2.markdown("\2")
    age_col2.metric(
        label="% Under 18 years", 
        value=f"{metrics['pct_pop_under_18']:.0f}%")
    age_col2.divider()
    age_col2.metric(
        label="Median Age", 
        value=f"{metrics['median_age']:.1f} years")
    age_col2.divider()
    age_col2.metric(
        label="% 65 years+", 
        value=f"{metrics['pct_pop_65_and_over']:.0f}%")

    # The RACE Section
    st.subheader("Race")

    race_dist_chart = bar_chart(
        source=plot_dfs['race_dist'], title_geo=title_geo, XcolumnName="Race/Ethnicity", YcolumnName="Population",
        fillColor="steelblue", barWidth=120, distribution=True, labelFontSize=13, height=500,
        title="Race Distribution", XlabelAngle=0
    )
    st.altair_chart(race_dist_chart)

    # The CITIZEN VOTING AGE Section
    st.subheader("Citizen Voting Age")


