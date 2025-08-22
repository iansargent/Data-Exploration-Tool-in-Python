import streamlit as st
import pandas as pd
import altair as alt
from app_utils.census import get_geography_title, split_name_col
from app_utils.df_filtering import filter_snapshot_data
from app_utils.color import get_text_color
from app_utils.plot import donut_chart, bar_chart, make_time_series_plot
from app_utils.data_loading import load_metrics

from app_utils.constants.ACS import (ACS_DEMOGRAPHIC_METRICS, AGE_GROUP_LABELS, AGE_GROUP_COLUMNS,
                                     RACE_LABELS, RACE_COLUMNS)


def demographic_snapshot_header():
    st.subheader("Demographic Snapshot")
    # Include a source for the dataset (Census DP05 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP05: Demographic and Housing Estimates - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def compute_demog_metrics(df):
    return load_metrics(df, ACS_DEMOGRAPHIC_METRICS)


def build_demog_plot_dataframes(df, metrics):
    """
    Calculate a dictionary of demographic dataframes
    """

    return {
        "age_dist": pd.DataFrame({
            "Age Group": AGE_GROUP_LABELS, 
            "Population": [df[col].sum() for col in AGE_GROUP_COLUMNS]
        }),
        
        "race_dist": pd.DataFrame({
            "Race/Ethnicity": RACE_LABELS,
            "Population": [df[col].sum() for col in RACE_COLUMNS]
        }),
        
        "sex_dist": pd.DataFrame({
            "Sex": ["Male", "Female"],
            "Population": [metrics["pop_male"], metrics['pop_female']]
        })
     }


def demog_df_metric_dict(filtered_gdf_2023):
    metrics = compute_demog_metrics(filtered_gdf_2023)
    dfs = build_demog_plot_dataframes(filtered_gdf_2023, metrics)
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
    render_sex(metrics, plot_dfs, title_geo)
    render_age(metrics, plot_dfs, title_geo)
    render_race(plot_dfs, title_geo)
    render_voting_age_citizens(metrics)

    
def render_sex(metrics, plot_dfs, title_geo):
    # The SEX Section
    st.divider()
    st.subheader("Sex")
    
    _, sex_col1, sex_col2 = st.columns([0.5, 3, 6])
    
    sex_col1.markdown("\2")
    sex_col1.metric(label="Total Population", value=f"{metrics['total_population']:,.0f}")
    sex_col1.metric(label="Sex Ratio (Males for every 100 Females)", value=f"{metrics['sex_ratio']:.1f}")
    sex_col1.metric(label="Percent Male", value=f"{metrics['pct_male']:.1f}%")
    sex_col1.metric(label="Percent Female", value=f"{metrics['pct_female']:.1f}%")

    sex_dist_bar_chart = bar_chart(
        source=plot_dfs['sex_dist'], title_geo=title_geo, x_col="Sex", y_col="Population",
        distribution=True, x_label_size=15, fill="steelblue", x_label_angle=0, height=450, 
        bar_width=250, title="Sex Distribution", title_size=19,
    )
    
    sex_col2.altair_chart(sex_dist_bar_chart, use_container_width=True)
    

def render_age(metrics, plot_dfs, title_geo):
    # The AGE Section
    st.divider()
    st.subheader("Age")
    
    age_col1, _, age_col2 = st.columns([6, 0.5, 2])
    
    age_dist_bar_chart = bar_chart(
        source=plot_dfs["age_dist"], title_geo=title_geo, x_col="Age Group", y_col="Population",
        x_label_angle=0, fill="steelblue", height=500, bar_width=45, distribution=True, x_label_size=12,
        title="Age Distribution"
    )
    age_col1.altair_chart(age_dist_bar_chart, use_container_width=True)

    age_col2.markdown("\2")
    age_col2.metric(label="% Under 18 years", value=f"{metrics['pct_pop_under_18']:.0f}%")
    age_col2.divider()
    age_col2.metric(label="Median Age", value=f"{metrics['median_age']:.1f} years")
    age_col2.divider()
    age_col2.metric(label="% 65 years+", value=f"{metrics['pct_pop_65_and_over']:.0f}%")
    

def render_race(plot_dfs, title_geo):
    # The RACE Section
    st.divider()
    st.subheader("Race")

    race_dist_chart = bar_chart(
        source=plot_dfs['race_dist'], title_geo=title_geo, x_col="Race/Ethnicity", y_col="Population",
        fill="steelblue", bar_width=120, distribution=True, x_label_size=13, height=500,
        title="Race Distribution", x_label_angle=0
    )
    st.altair_chart(race_dist_chart)


def render_voting_age_citizens(metrics):
    st.divider()
    # The CITIZEN VOTING AGE Section
    st.subheader("Citizen Voting Age")

    st.warning("Citizen Voting-Age data issues being worked out.")
    vote_col1, vote_col2, vote_col3 = st.columns(3)

    vote_col1.metric(label="Voting-Age Citizens", value=f"{metrics['pop_voting_age_citizen']:.0f}")
    vote_col2.metric(label="Male Voting-Age Citizens", value=f"{metrics['citizen_voting_age_pct_male']:.0f}%")
    vote_col3.metric(label="Female Voting-Age Citizens", value=f"{metrics['citizen_voting_age_pct_female']:.0f}%")




