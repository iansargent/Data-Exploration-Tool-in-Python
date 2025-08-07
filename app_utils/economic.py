"""
Open Research Community Accelorator
Vermont Data App

Economic Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.color import get_text_color
from app_utils.plot import donut_chart, bar_chart
from app_utils.df_filtering import filter_snapshot_data
from app_utils.plot import safe_altair_plot
from app_utils.data_loading import load_metrics


# import constants
from app_utils.constants.ACS import ACS_ECON_METRICS, FAMILY_INCOME_COLUMNS, FAMILY_INCOME_LABELS


def economic_snapshot_header():
    st.subheader("Economic Snapshot")
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP03: Selected Economic Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")

def make_time_series_plot(
    df,
    x_col,
    y_col,
    color_col,
    tooltip_cols,
    title,
    color_domain,
    color_range,
    y_axis_format=".0f",
    y_scale_domain=None,
    legend=None,
    height=500,
    title_config=dict(fontSize=19, anchor="middle")
):
    y_scale = alt.Scale(domain=y_scale_domain) if y_scale_domain is not None else alt.Undefined

    return alt.Chart(df).mark_line(point=True).encode(
        x=alt.X(x_col, title="Year",
                axis=alt.Axis(
                    labelAngle=0,
                    labelFontSize=15,
                    labelFont="Helvetica Neue",
                    labelFontWeight='normal',
                    titleFont="Helvetica Neue")),
        y=alt.Y(y_col, title=title.split('|')[0].strip(),
                axis=alt.Axis(
                    format=y_axis_format,
                    labelFont="Helvetica Neue",
                    labelFontWeight='normal',
                    titleFont="Helvetica Neue"),
                scale=y_scale),
        color=alt.Color(color_col, title=None,
                        scale=alt.Scale(
                            domain=color_domain,
                            range=color_range),
                        legend=legend),
        tooltip=[alt.Tooltip(c) for c in tooltip_cols]
    ).properties(height=height, title=alt.Title(title)
    ).configure_title(**title_config).interactive()

def unemployment_rate_ts_plot(filtered_unemployment_df, unemployment_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    
    # Filter data based on selection
    plot_df = filtered_unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index()
    plot_df["Unemployment_Rate"] = plot_df["Unemployment_Rate"] / 100
    plot_df["Geography"] = title_geo
    
    # Calculate the statewide avg dataframe for plotting at the statewide level
    statewide_avg_df = unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index().assign(Geography="Statewide Average")
    statewide_avg_df["Unemployment_Rate"] = statewide_avg_df["Unemployment_Rate"] / 100

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
    
    # Set the max and min of the y axis to frame the plotted data nicely
    ymax = plot_df["Unemployment_Rate"].max() + 0.01
    ymin = plot_df["Unemployment_Rate"].min() - 0.01

    # Create a time series plot of the unemployment rate
    return make_time_series_plot(
        df=plot_df,
        x_col="year:O",
        y_col="Unemployment_Rate:Q",
        color_col="Geography:O",
        tooltip_cols=["year", "Unemployment_Rate", "Geography"],
        title=f"Unemployment Rate Over Time | {title_geo}",
        y_axis_format="%",
        y_scale_domain=(ymin, ymax),
        color_domain=["Statewide Average", title_geo],
        color_range=["#83C299", "darkgreen"],
        legend=legend,
        height=500
    )


def median_earnings_ts_plot(filtered_earnings_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    # Summarize earnings by both year and variable (mean): Call the summarized variable "Median_Earnings"
    plot_df = filtered_earnings_df.groupby(["year", "variable"]).agg(Median_Earnings=("estimate", "mean")).reset_index()
    
    # Rename variables for the labels within the legend
    variable_names = {"DP03_0092": "All Workers", "DP03_0093": "Male (FTYR)", "DP03_0094": "Female (FTYR)"}
    plot_df = plot_df.assign(Population = lambda df: df["variable"].map(variable_names))
    
    # Set the max and min of the y axis to frame the plotted data nicely
    ymax = plot_df["Median_Earnings"].max() + 5000
    ymin = plot_df["Median_Earnings"].min() - 15000

    # If there is not enough available data for the filtered geography,  (1 or less years)
    if len(plot_df) <= 1:
        return None
    
    # Create a time series plot of the median earnings for three groups over time rate
    return make_time_series_plot(
        df=plot_df,
        x_col="year:O",
        y_col="Median_Earnings:Q",
        color_col="Population:N",
        tooltip_cols=["year", "Median_Earnings", "Population"],
        title=f"Median Earnings | {title_geo}",
        y_axis_format="$,.0f",
        y_scale_domain=[ymin, ymax],
        color_domain=["All Workers", "Male (FTYR)", "Female (FTYR)"],
        color_range=["forestgreen", "dodgerblue", "deeppink"],
        legend=alt.Legend(orient="bottom-left", direction="horizontal", offset=20, labelFont="Helvetica Neue"),
        height=475
    )



def avg_commute_time_ts_plot(filtered_commute_time_df, commute_time_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    # Summarize commute time by year (mean): Call the variable "Average_Commute"    
    plot_df = filtered_commute_time_df.groupby("year").agg(Average_Commute=("estimate", "mean")).reset_index()
    # Add a geography column for comparing to the statewide average line
    plot_df["Geography"] = title_geo
    
    # Load the full unfiltered dataset for the statewide line
    statewide_avg_df = commute_time_df.groupby("year").agg(Average_Commute=("estimate", "mean")).reset_index().assign(Geography="Statewide Average")

    # If not statewide scope, concatanate the filtered line DataFrame with the statewide avg DataFrame
    if title_geo != "Vermont (Statewide)":
        plot_df = pd.concat([plot_df, statewide_avg_df], ignore_index=True)
        legend=alt.Legend(orient="top", direction="horizontal", offset=0, labelFont="Helvetica Neue")
    # If we’re statewide only, skip adding the comparison line and don't show the color legend
    else:
        legend=None

    # If there is not enough available data for the filtered geography,  (1 or less years)
    if len(plot_df[plot_df["Geography"] != "Statewide Average"]) <= 1:
        return None
    
    # Set the max and min of the y axis to frame the plotted data nicely
    ymax = plot_df["Average_Commute"].max() + 5
    ymin = plot_df["Average_Commute"].min() - 5

    # Create a time series plot of average commute time
    return make_time_series_plot(
        df=plot_df,
        x_col="year:O", 
        y_col="Average_Commute:Q",
        color_col="Geography:O",
        tooltip_cols=["year", "Average_Commute", "Geography"],
        title=f"Average Commuting Time | {title_geo}",
        y_axis_format=".0f",
        y_scale_domain=(ymin, ymax),
        color_domain=["Statewide Average", title_geo],
        color_range=["#83C299", "darkgreen"],
        legend=legend,
        height=450,
        title_config=dict(fontSize=19, anchor="start", dx=68, offset=10),
    )


def commute_habits_ts_plot(filtered_commute_habits_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    # Summarize earnings by both year and variable (mean): Call the summarized variable "Percentage"
    plot_df = filtered_commute_habits_df.groupby(["year", "variable"]).agg(Percentage=("estimate", "mean")).reset_index()
    
    # Rename variables for the labels within the legend
    variable_names = {"DP03_0019P": "Drove Alone", "DP03_0021P": "Public Transit", "DP03_0024P": "Work From Home"}
    plot_df = plot_df.assign(Commute_Type = lambda df: df["variable"].map(variable_names))
    # Turn the percentage column into a proportion (for easier axis formatting in the plot)
    plot_df["Percentage"] = plot_df["Percentage"] / 100
    
    # Pivot the DataFrame to calculate an 'Other' variable
    pivot_df = plot_df.pivot(index="year", columns="Commute_Type", values="Percentage").fillna(0)
    pivot_df["Other"] = 1.0 - pivot_df.sum(axis=1)
    other_df = pivot_df[["Other"]].reset_index().melt(id_vars="year", var_name="Commute_Type", value_name="Percentage")

    # Combine the two DataFrames so that "other" is included in the analysis
    final_plot_df = pd.concat([plot_df[["year", "Commute_Type", "Percentage"]], other_df], ignore_index=True)
    
    # If there is not enough available data for the filtered geography,  (1 or less years)
    if len(final_plot_df) <= 1:
        return None
    
    # Create a time series plot of the modes of commute to work (% share)
    return make_time_series_plot(
        df=final_plot_df,
        x_col="year:O",
        y_col="Percentage:Q",
        color_col="Commute_Type:N",
        tooltip_cols=["year", "Percentage", "Commute_Type"],
        title=f"How People Commute to Work | {title_geo}",
        y_axis_format=".0%",
        color_domain=["Drove Alone", "Other", "Work From Home", "Public Transit"],
        color_range=["tomato", "grey", "dodgerblue", "mediumseagreen"],
        legend=alt.Legend(orient="top", direction="horizontal",offset=0,labelFont="Helvetica Neue"),
        height=450,
        title_config=dict(fontSize=19, anchor="start", dx=78, offset=10),
    )

def build_econ_plot_dataframes(df, metrics):
    """
    Calculate a dictionary of economic dataframes
    """
    def pov_df(value):
        return pd.DataFrame({
            "Category": ["Below Poverty Level", "Over Poverty Level"],
            "Value": [value, 1 - value]
        })

    def mean_pct(col): 
        return df[col].mean() / 100

    return {
        "public_private_coverage_df": pd.DataFrame({
            "Coverage Type": ["Private Insurance", "Public Insurance"],
            "Value": [1 - metrics["pct_public_hc_coverage"], metrics["pct_public_hc_coverage"]]
        }),
        "family_income_df": pd.DataFrame({
            "Family Income": FAMILY_INCOME_LABELS,
            "Estimated Families": [df[col].sum() for col in FAMILY_INCOME_COLUMNS]
        }),
        "pov_people_df": pov_df(metrics["pct_people_below_pov"]),
        "pov_families_df": pov_df(metrics["pct_families_below_pov"]),
        "poverty_by_age_df": pd.DataFrame({
            "Age": ["Under 18 years", "18 - 64 years", "65+ years"],
            "Poverty Rate": [
                mean_pct("DP03_0129PE"),
                mean_pct("DP03_0134PE"),
                mean_pct("DP03_0135PE")
            ]
        })
    }

def compute_econ_metrics(df):
    metrics = load_metrics(df, ACS_ECON_METRICS)

    # manual calculation
    metrics[ "wage_gap"] = metrics['male_earnings'] - metrics['female_earnings']
    return metrics

 
def econ_df_metric_dict(filtered_gdf_2023):
    metrics  = compute_econ_metrics(filtered_gdf_2023)
    dfs = build_econ_plot_dataframes(filtered_gdf_2023, metrics)
    return metrics, dfs


# NOTE: The `st.metric` delta (^change) values are simply placeholders for now (not real data!)
def economic_snapshot(econ_dfs):    
    # Display the category header with data source
    economic_snapshot_header()
   
    # filter the data 
    filtered_dfs, selected_values = filter_snapshot_data(econ_dfs, key_df=econ_dfs['econ_2023'])

    # Get the title of the geography for plotting
    title_geo = get_geography_title(selected_values)
    
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="economic_snapshot")
    # Define two callable dictionaries: Metrics and Plot DataFrames
    metrics, plot_dfs = econ_df_metric_dict(filtered_dfs["econ_2023"])

    ## TODO: maybe better to run all of these with **kwargs, or just all take the same args, idk
    render_employment(econ_dfs, metrics, filtered_dfs, title_geo)
    render_health_insurance(metrics, title_geo, plot_dfs, text_color)
    render_income(metrics, filtered_dfs, title_geo, plot_dfs)
    render_poverty(metrics, title_geo, plot_dfs, text_color)
    render_work(econ_dfs, filtered_dfs, title_geo)



def render_employment(econ_dfs, metrics, filtered_dfs, title_geo):
    st.divider()
    st.subheader("Employment")
    # Set two columns (Left for metrics, right for line plot)
    metric_col, chart_col = st.columns([1, 4])
    metric_col.markdown("\2")
    
    # Display employment metrics
    metric_col.metric(
        label="**Unemployment Rate (2023)**", 
        value=f"{metrics['unemployment_rate'] * 100:.1f}%", 
        delta=f"{0.8}%", 
        delta_color='inverse')
    metric_col.metric(
        label="**Civilian Employment Rate**", 
        value=f"{metrics['pct_employed']:.1f}%", 
        delta=f"{2}%")
    metric_col.metric(
        label="**In Labor Force**", 
        value=f"{metrics['pct_in_labor_force']:.1f}%", 
        delta=f"{-3}%")
    metric_col.metric(
        label="**Females in Labor Force**", 
        value=f"{metrics['pct_female_in_labor_force']:.1f}%", 
        delta=f"{10}%")
    
    safe_altair_plot(
        plot =  unemployment_rate_ts_plot(filtered_dfs["unemployment"], econ_dfs['unemployment'], title_geo),
        data_type= "unemplotment",
        chart_col=chart_col
    )
    metric_col.markdown("\2")



def render_health_insurance(metrics, title_geo, plot_dfs, text_color):
    st.divider()
    st.subheader("Health Insurance Coverage")
    st.markdown("\2")
    
    # Set two columns (with a middle spacer) for donut chart on the left and metrics on the right
    h_col1, _, h_col2 = st.columns([10, 2, 10])
    
    public_private_coverage_df = plot_dfs['public_private_coverage_df']
    # Use the `donut_chart` function  to create a tailored chart using info from the dataframe above
    public_private_pie_chart = donut_chart(
        source=public_private_coverage_df, colorColumnName="Coverage Type", height=350, width=200, 
        innerRadius=130, fontSize=45, titleFontSize=18, fillColor="mediumseagreen", 
        title=f"Private Health Coverage | {title_geo}", stat=(1 - metrics['pct_public_hc_coverage']), text_color=text_color)
    # Display the donut chart on the left
    h_col1.altair_chart(public_private_pie_chart)
    
    # On the right, display useful insurance metrics
    h_col2.metric(
        label="**No Health Coverage**", 
        value=f"{metrics['pct_no_hc_coverage']:.1f}%", 
        delta=f"{0.5}%", 
        delta_color='inverse')
    h_col2.metric(
        label="**No Health Coverage (Age 0-19)**", 
        value=f"{metrics['pct_no_hc_coverage_u19']:.1f}%", 
        delta=f"{-0.4}%", 
        delta_color='inverse')
    h_col2.metric(
        label="**Employed without Health Coverage (19-64)**", 
        value=f"{metrics['pct_employed_no_hc_coverage']:.1f}%", 
        delta=f"{1.8}%", 
        delta_color='inverse')


def render_income(metrics, filtered_dfs, title_geo, plot_dfs):
    st.divider()
    st.subheader("Income")
    
    # Define 4 columns (with left spacer) to display important income metrics
    _, earn_metric_col1, earn_metric_col2, earn_metric_col3, earn_metric_col4 = st.columns([0.5, 1, 1, 1, 1])
    
    earn_metric_col1.metric(
        label="**Median Earnings** (All Workers)", 
        value=f"${metrics['median_earnings']:,.0f}", 
        delta=f"{12459:,.0f}")
    earn_metric_col2.metric(
        label="**Median Male Earnings** (FTYR)", 
        value=f"${metrics['male_earnings']:,.0f}", 
        delta=f"{2459:,.0f}")
    earn_metric_col3.metric(
        label="**Median Female Earnings** (FTYR)", 
        value=f"${metrics['female_earnings']:,.0f}", 
        delta=f"{1047:,.0f}")
    earn_metric_col4.metric(
        label="**Gender Wage Gap**", 
        value=f"${metrics['wage_gap']:,.0f}", 
        delta=f"{-749:,.0f}", delta_color='inverse')
    st.markdown("\2")
    
    # Display the median earnings time series plot directly below the metrics
    safe_altair_plot(
        plot=median_earnings_ts_plot(filtered_dfs['median_earnings'], title_geo),
        data_type="median earnings"
    )
    
    # Define two columns for metrics on the left and a bar plot on the right
    income_col1, income_col2 = st.columns([2, 11])
    income_col1.markdown("\2")

    # On the left, display more useful income metrics
    income_col1.metric(
        label="Income Per Capita", 
        value=f"${metrics['income_per_capita']:,.0f}", 
        delta=f"{5492:,.0f}")
    income_col1.markdown("\2")
    income_col1.metric(
        label="Median Family Income", 
        value=f"${metrics['median_family_income']:,.0f}", 
        delta=f"{4204:,.0f}")
    
    # Use the `census_bar_chart` function to create a highly customizable bar chart
    family_income_dist_chart = bar_chart(
        source=plot_dfs['family_income_df'], title_geo=title_geo, XcolumnName="Family Income", xType=":N", yType=":Q",
        YcolumnName="Estimated Families", barWidth=75, titleFontSize=19, title="Family Income Distribution")
    # Display the bar chart on the right
    income_col2.altair_chart(family_income_dist_chart, use_container_width=True)


def render_poverty(metrics, title_geo, plot_dfs, text_color):
    st.divider()
    st.subheader("Poverty")

    # Define two columns with two donut charts on the left and a barplot on the right
    pov_col1, pov_col2 = st.columns([2, 3])
    
    pov_people_df = plot_dfs['pov_people_df']
    pov_families_df = plot_dfs['pov_families_df']
    
    # Create a donut chart to show the % of people below the poverty level
    pov_people_pie_chart = donut_chart(
        source=pov_people_df, colorColumnName="Category", height=250, width=175, 
        innerRadius=85,fontSize=40, title=f"People Below Poverty Level | {title_geo}",
        stat=metrics['pct_people_below_pov'], text_color=text_color)
    # Create a donut chart to show the % of families below the poverty level
    pov_families_pie_chart = donut_chart(
        source=pov_families_df, colorColumnName="Category", height=250, width=175, 
        innerRadius=85, fontSize=40, titleFontSize=14, fillColor="mediumseagreen", 
        title=f"Families Below Poverty Level | {title_geo}", stat=metrics['pct_families_below_pov'], text_color=text_color)
    # Display the two donut charts
    pov_col1.markdown("\2") 
    pov_col1.altair_chart(pov_people_pie_chart)
    pov_col1.altair_chart(pov_families_pie_chart)

    poverty_by_age_df = plot_dfs['poverty_by_age_df']
    # Create a highly customizable bar chart using the `census_bar_chart` function
    pov_by_age_chart = bar_chart(
        source=poverty_by_age_df, title_geo=title_geo, XcolumnName="Age", YcolumnName="Poverty Rate",
        xType=":O", yType=":Q", yFormat=".0%", YtooltipFormat=".1%", barWidth=130, XlabelAngle=0, height=600, titleFontSize=19, 
        labelFontSize=13, title="Poverty Rate by Age Group", distribution=False)
    # Display the bar chart on the right
    pov_col2.altair_chart(pov_by_age_chart)
    

def render_work(econ_dfs, filtered_dfs, title_geo):
    st.divider()
    st.subheader("Work")
    st.markdown("\2")
    
    # Define and display a time series plot of average commute time
    safe_altair_plot(
        avg_commute_time_ts_plot(filtered_dfs['commute_time'], econ_dfs['commute_time'], title_geo),
        "commute time"
    )

    safe_altair_plot(
        commute_habits_ts_plot(filtered_dfs['commute_habits'], title_geo),
        "commute habit "
    )