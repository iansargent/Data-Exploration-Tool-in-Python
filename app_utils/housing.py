"""
Open Research Community Accelorator
Vermont Data App

Housing Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
import io
import requests

from app_utils.census import get_geography_title
from app_utils.df_filtering import filter_snapshot_data
from app_utils.color import get_text_color
from app_utils.plot import donut_chart, bar_chart, make_time_series_plot
from app_utils.data_loading import load_metrics

from app_utils.constants.ACS import ACS_HOUSING_METRICS, HOUSING_YEAR_LABELS, NEW_HOUSING_UNIT_COLUMNS, POPULATION_YEAR_LABELS 


def housing_snapshot_header():
    st.subheader("Housing Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def med_home_value_ts_plot(filtered_med_val_df, med_val_df, title_geo):   
    # Filter data based on selection
    plot_df = filtered_med_val_df.groupby("year").agg(Median_Home_Value=("estimate", "mean")).reset_index()
    plot_df["Geography"] = title_geo
    
    # Calculate the statewide avg dataframe for plotting at the statewide level
    statewide_avg_df = med_val_df.groupby("year").agg(Median_Home_Value=("estimate", "mean")).reset_index().assign(Geography="Statewide Average")

    # If not statewide scope, concatanate the filtered line DataFrame with the statewide avg DataFrame
    if title_geo != "Vermont (Statewide)":
        plot_df = pd.concat([plot_df, statewide_avg_df], ignore_index=True)
        legend = alt.Legend(orient="bottom-left", direction="horizontal", offset=20, labelFont="Helvetica Neue")
    # If we’re statewide only, skip adding the comparison line and don't show the color legend
    else:
        legend = None

    # If there is not enough available data for the filtered geography,  (1 or less years)
    if len(plot_df[plot_df["Geography"] != "Statewide Average"]) <= 1:
        return None
    
    # Create a time series plot of the unemployment rate
    return make_time_series_plot(
        df=plot_df,
        x_col="year:O",
        y_col="Median_Home_Value:Q",
        color_col="Geography:O",
        tooltip_cols=["year", "Median_Home_Value", "Geography"],
        title=f"Median Home Value Over Time | {title_geo}",
        y_axis_format="$,.0f",
        color_domain=["Statewide Average", title_geo],
        color_range=["#F5A68C", "tomato"],
        legend=legend,
        height=500
    )


def med_smoc_ts_plot(filtered_med_smoc_df, med_smoc_df, title_geo):
        
    # Filter data based on selection
    plot_df = filtered_med_smoc_df.groupby(["year", "variable"]).agg(Monthly_Costs=("estimate", "mean")).reset_index()
    plot_df["Geography"] = title_geo
    
    # Calculate the statewide avg dataframe for plotting at the statewide level
    statewide_avg_df = med_smoc_df.groupby(["year", "variable"]).agg(Monthly_Costs=("estimate", "mean")).reset_index().assign(Geography="Statewide Average")

    # If not statewide scope, concatanate the filtered line DataFrame with the statewide avg DataFrame
    if title_geo != "Vermont (Statewide)":
        plot_df = pd.concat([plot_df, statewide_avg_df], ignore_index=True)
        legend = alt.Legend(orient="bottom-left", direction="horizontal", offset=20, labelFont="Helvetica Neue")
    # If we’re statewide only, skip adding the comparison line and don't show the color legend
    else:
        legend = None

    # If there is not enough available data for the filtered geography,  (1 or less years)
    if len(plot_df[plot_df["Geography"] != "Statewide Average"]) <= 1:
        return None
    
    # Create a time series plot of the unemployment rate
    return make_time_series_plot(
        df=plot_df,
        x_col="year:O",
        y_col="Monthly_Costs:Q",
        color_col="Geography:O",
        tooltip_cols=["year", "Monthly_Costs", "Geography"],
        title=f"Median Monthly Costs Value Over Time | {title_geo}",
        y_axis_format="$,.0f",
        color_domain=["Statewide Average", title_geo],
        color_range=["#F5A68C", "tomato"],
        legend=legend,
        height=500,
        stroke_dash_col="variable",
        add_points=False
    )


def housing_pop_plot(plot_dfs, title_geo):
    return make_time_series_plot(
        df=plot_dfs['housing_population_df'], 
        x_col="Year Range", 
        y_col="Value", 
        color_col="Metric",
        tooltip_cols=["Metric", "Value"], 
        title=f"Housing Units vs Population Over Time | {title_geo}",
        color_domain=["Total Housing Units", "New Housing Units", "Population"],
        color_range=["red", "royalblue", "skyblue"], 
        y_axis_format=",.0f", 
        x_label_config=dict(labelAngle=-30, labelFontSize=12)
    )          
    

def compute_housing_metrics(df):
    return load_metrics(df, ACS_HOUSING_METRICS)


def housing_df_metric_dict(filtered_housing_2023):
    # Unpack necessary datasets
    filtered_gdf_2023 = filtered_housing_2023["housing_2023"]    
    metrics = compute_housing_metrics(filtered_gdf_2023)
    dfs = build_housing_plot_dataframes(filtered_housing_2023, metrics)

    return metrics, dfs


def build_housing_plot_dataframes(dfs, metrics):
    """
    Calculate a dictionary of housing dataframes
    """

    filtered_gdf_2023 = dfs["housing_2023"]
        
    filtered_pop_df = dfs["vt_historic_population"]
    
    population_counts = [filtered_pop_df.loc[filtered_pop_df["Year"] == year, "Population"].sum() for year in POPULATION_YEAR_LABELS]
    raw_housing_counts = [filtered_gdf_2023[col].sum() for col in NEW_HOUSING_UNIT_COLUMNS]
    # get hardcoded metrics
    pct_occ_2023 = metrics['pct_occupied']
    pct_vac_2023 = metrics['pct_vacant']
    pct_own_2023 = metrics['pct_owned']
    pct_rent_2023 = metrics['pct_rented']

    # Units in structure: define the label and corresponding metric keys
    structure_labels = [
        '1-Unit', '2-Units', '3 - 4 Units', '5 - 9 Units',
        '10 - 19 Units', '20+ Units', 'Mobile Homes', 'Boat/RV/Van, etc.'
    ]
    structure_keys = [
        'one_unit_total', 'two_units', 'three_or_four_units',
        'five_to_nine_units', 'ten_to_nineteen_units',
        'twenty_or_more_units', 'mobile_home', 'boat_rv_van_etc'
    ]
    
    
    return {
        "occupancy_occ_df": pd.DataFrame({
            'Occupancy Status': ['Occupied', 'Vacant'],
            'Value': [pct_occ_2023, pct_vac_2023]
        }),
        
        "occupancy_vac_df": pd.DataFrame({
            'Occupancy Status': ['Occupied', 'Vacant'],
            'Value': [pct_occ_2023, pct_vac_2023]
        }),
        
        "tenure_df": pd.DataFrame({
            'Occupied Tenure': ['Owner', 'Renter'],
            'Value': [pct_own_2023, pct_rent_2023]
        }),
        
        "units_in_structure_df": pd.DataFrame({
            'Structure Category': structure_labels,
            'Units': [metrics[k] for k in structure_keys]
        }),
        
        "housing_population_df": pd.DataFrame({
            "Year Range": HOUSING_YEAR_LABELS,
            "Census Year": POPULATION_YEAR_LABELS,
            "Population": population_counts,
            "Total Housing Units": pd.Series(raw_housing_counts).cumsum().tolist(),
            "New Housing Units": raw_housing_counts
        }).melt(
            id_vars=['Year Range', 'Census Year'],
            value_vars=['Population', 'Total Housing Units', 'New Housing Units'],
            var_name='Metric',
            value_name='Value'
        )
    }


def housing_snapshot(housing_dfs):
    # Display the Category Header with Data Source
    housing_snapshot_header()
    
    # Filter the dataframes using select boxes for "County" and "Jurisdiction"    
    filtered_housing_dfs, selected_values = filter_snapshot_data(housing_dfs, housing_dfs['housing_2023'])
    st.divider()

    # Get the title of the geography for plotting
    title_geo = get_geography_title(selected_values)
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="housing_snapshot")
    # Define two callable dictionaries: Metrics and Plot DataFrames
    metrics, plot_dfs = housing_df_metric_dict(filtered_housing_dfs)    
    
    # Display the population and housing units time series plot
    population_units_plot = housing_pop_plot(plot_dfs, title_geo)
    st.altair_chart(population_units_plot)

    render_occupancy(metrics, plot_dfs, text_color, title_geo)
    render_tenure(metrics, plot_dfs, text_color)
    render_owner_occupied(metrics, title_geo, housing_dfs, filtered_housing_dfs)
    render_renter_occupied(metrics)


def render_occupancy(metrics, plot_dfs, text_color, title_geo): 
    # The OCCUPANCY Section ___________________________________________________
    st.divider()
    st.subheader("Occupancy")
    # Split section into three colunms: Metrics on the left followed by two donut charts
    _, occ_col1, occ_col2, occ_col3 = st.columns([0.5, 1, 2, 2])
    occ_col1.markdown("\2")
    occ_col1.markdown("\2")
    occ_col1.metric(
        label="**Total Housing Units**", 
        value=f"{metrics['total_units']:,.0f}", 
        help="Total number of housing units in the selected geography for 2023.")
    occ_col1.metric(
        label="**Occupied** Units", 
        value=f"{metrics['occupied_units']:,.0f}", 
        help="Total number of occupied housing units in the selected geography.")
    occ_col1.metric(
        label="**Vacant** Units", 
        value=f"{metrics['vacant_units']:,.0f}", 
        help="Total number of vacant housing units in the selected geography.")
    
    # In the middle, show the donut chart of occupied units
    occupancy_occ_chart = donut_chart(
        source=plot_dfs['occupancy_occ_df'], colorColumnName="Occupancy Status", titleFontSize=15, 
        fillColor="tomato", title="Units Occupied", text_color=text_color, 
        stat=metrics['pct_occupied'], innerRadius=135, height=400)
    # In the right column, show the donut chart of vacant units
    occupancy_vac_chart = donut_chart(
        source=plot_dfs['occupancy_vac_df'], colorColumnName="Occupancy Status", titleFontSize=15, 
        fillColor="tomato", title="Units Vacant", text_color=text_color, 
        stat=metrics['pct_vacant'], innerRadius=135, height=400, inverse=True)
    
    # Display the two donut charts
    occ_col2.altair_chart(occupancy_occ_chart, use_container_width=True)
    occ_col3.altair_chart(occupancy_vac_chart, use_container_width=True)
    
    
    st.divider()
    # Define a bar chart distribution of structure types (1 unit, 2 unit, etc.)
    units_in_structure_bar_chart = bar_chart(
        plot_dfs['units_in_structure_df'], title_geo=title_geo, XcolumnName="Structure Category", YcolumnName="Units",
        distribution=True, height=600, fillColor="tomato", title="2023 Housing Unit Type Distribution",
        barWidth=90, XlabelAngle=0, labelFontSize=12)
    # Display the bar chart
    st.subheader("Unit Type")
    st.altair_chart(units_in_structure_bar_chart, use_container_width=True)
    
    
def render_tenure(metrics, plot_dfs, text_color):
    # The HOUSING TENURE Section ___________________________________________________
    st.divider()
    st.subheader("Housing Tenure")
    # Split into three columns: Two donut charts on the left and metrics on the right
    ten_col3, ten_col2, ten_col1, _ = st.columns([10, 10, 5, 2])
        
    ten_col1.markdown("\2")
    ten_col1.metric(
        label="**Owner-Occupied** Units", 
        value=f"{metrics['owned_units']:,.0f}", 
        help="Total number of owner-occupied housing units in the selected geography.")    
    ten_col1.metric(
        label="**Renter-Occupied** Units", 
        value=f"{metrics['rented_units']:,.0f}", 
        help="Total number of renter-occupied housing units in the selected geography.")

    # Create the owner-occupied donut chart
    tenure_own_donut = donut_chart(
        plot_dfs['tenure_df'], colorColumnName="Occupied Tenure", fillColor="tomato", 
        title="Owner Occupied", stat=metrics['pct_owned'], text_color=text_color)
    # Create the renter-occupied donut chart
    tenure_rent_donut = donut_chart(
        source=plot_dfs['tenure_df'], colorColumnName="Occupied Tenure", fillColor="tomato", 
        title="Renter Occupied", stat=metrics['pct_rented'], text_color=text_color, inverse=True)
    
    # Display the two donut charts
    ten_col2.altair_chart(tenure_own_donut)
    ten_col3.altair_chart(tenure_rent_donut) 
    
    st.divider()


def render_owner_occupied(metrics, title_geo, housing_dfs, filtered_housing_dfs):
    # The OWNER-OCCUPIED Section ___________________________________________________
    med_value_ts_plot = med_home_value_ts_plot(filtered_housing_dfs["median_value"], housing_dfs['median_value'], title_geo)  
    st.altair_chart(med_value_ts_plot)
    st.divider()
    st.subheader("Selected Monthly Owner Costs (SMOC)")
    # Split into two columns: Metrics on the left and time series plot on the right
    _, smoc_col1, smoc_col2 = st.columns([0.5, 3, 10])
    # Metrics
    smoc_col1.markdown("\2")
    smoc_col1.markdown("\2")
    smoc_col1.markdown("##### Median Monthly Costs")
    smoc_col1.markdown("\2")
    smoc_col1.metric(
        label="**Mortgaged** Units", 
        value=f"${metrics['avg_SMOC_mortgaged']:,.2f}",
        help="Average monthly owner costs for ***mortgaged*** units in the selected geography for 2023")    
    smoc_col1.divider()
    smoc_col1.metric(
        label="**Non-Mortgaged** Units", 
        value=f"${metrics['avg_SMOC_non_mortgaged']:,.2f}",
        help="Average monthly owner costs for ***non-mortgaged*** units in the selected geography for 2023")
    
    # Define and display the median selected monthly cost time series plot (mortgaged vs non-mortgaged units)    
    median_smoc_ts_plot = med_smoc_ts_plot(filtered_housing_dfs["median_smoc"], housing_dfs['median_smoc'], title_geo)
    smoc_col2.markdown("\2")
    smoc_col2.altair_chart(median_smoc_ts_plot)


def render_renter_occupied(metrics):
    # The RENTER-OCCUPIED Section ___________________________________________________
    st.divider()
    st.subheader("Renter-Occupied Units")
    # Split into three columns for three metrics
    rent_col1, rent_col2, rent_col3 = st.columns(3)
    # Metrics
    rent_col1.metric(
        label="Median **Gross Rent**", 
        value=f"${metrics['avg_gross_rent']:,.2f}",
        help="Average median gross rent in the selected geography for 2023.")
    rent_col2.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{metrics['rent_burden35']:,.0f}",
        help="Count of households where rent takes up 35% or more of their household income in the selected geography for 2023")
    rent_col3.metric(
        label="% Occupied Units paying 35%+ of Income on Rent", 
        value=f"{metrics['pct_rent_burden35']:.1f}%",
        help="Percentage of households where rent takes up 35% or more of their household income in the selected geography for 2023.")
    
