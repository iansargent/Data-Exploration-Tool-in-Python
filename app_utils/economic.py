"""
Open Research Community Accelorator
Vermont Data App

Economic Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils.census import get_geography_title


def economic_snapshot(county, jurisdiction, economic_gdf_2023):    
    title_geo = get_geography_title(county, jurisdiction)

    st.subheader("Employment")
    
    unemployment_rate = economic_gdf_2023['DP03_0009PE'].mean()
    
    in_labor_force = economic_gdf_2023['DP03_0002E'].mean()
    pct_in_labor_force = economic_gdf_2023['DP03_0002PE'].mean()

    not_in_labor_force = economic_gdf_2023['DP03_0007E'].mean()
    pct_not_in_labor_force = economic_gdf_2023['DP03_0007PE'].mean()


    labor_force_df = pd.DataFrame({
        'Status': ["Labor Force", "Not in Labor Force"], 
        'People': [in_labor_force, not_in_labor_force],
        'Percentage': [pct_in_labor_force, pct_not_in_labor_force]
    })
    
    labor_force_pie_chart = alt.Chart(labor_force_df).mark_arc(innerRadius=130).encode(
        theta=alt.Theta("People:Q", aggregate="sum"),
        color=alt.Color("Status:N", scale=alt.Scale(
            domain=["Labor Force", "Not in Labor Force"],
            range=["mediumseagreen", "whitesmoke"])),
        tooltip=[alt.Tooltip("Status:N"), 
                 alt.Tooltip("People:Q", format=",.0f"),
                 alt.Tooltip("Percentage:Q", format=".1f")]
    ).properties(width=300, height=440).configure_legend(orient='top-left')


    st.metric(label="**Unemployment Rate**", value=f"{unemployment_rate:.1f}%")
    st.altair_chart(labor_force_pie_chart)


    st.subheader("Health Insurance Coverage")
    
    col3, col4 = st.columns(2)

    no_hc_coverage = economic_gdf_2023['DP03_0099E'].mean()
    pct_no_hc_coverage = economic_gdf_2023['DP03_0099PE'].mean()
    no_hc_coverage_u19 = economic_gdf_2023['DP03_0101E'].mean()
    pct_no_hc_coverage_u19 = economic_gdf_2023['DP03_0101PE'].mean()
    public_hc_coverage = economic_gdf_2023['DP03_0098E'].mean()
    pct_public_hc_coverage = economic_gdf_2023['DP03_0098PE'].mean()

    col3.metric(label="**No Health Insurance Coverage**", value=f"{no_hc_coverage:,.0f}")
    col4.metric(label="**% No Health Insurance Coverage**", value=f"{pct_no_hc_coverage:.1f}%")

    col3.metric(label="**No Health Insurance Coverage (Age 19 and Under)**", value=f"{no_hc_coverage_u19:,.0f}")
    col4.metric(label="**% No Health Insurance Coverage (Age 19 and Under)**", value=f"{pct_no_hc_coverage_u19:.1f}%")

    col3.metric(label="**Public Insurance Coverage**", value=f"{public_hc_coverage:,.0f}")
    col4.metric(label="**% Public Insurance Coverage**", value=f"{pct_public_hc_coverage:.1f}%")

    st.markdown("---")


    st.subheader("Income")
    
    st.markdown("##### Median Earnings for Workers")
    st.write("DP03_0092E")

    st.markdown("###### Median Male Earnings")
    st.write("DP03_0093E")

    st.markdown("###### Median Female Earnings")
    st.write("DP03_0094E")

    st.markdown("###### Gender Pay Gap")

    st.markdown("##### Income Per Capita")
    st.write("DP03_0088E")

    st.markdown("##### Median Family Income")
    st.write("DP03_0086E")

    st.markdown("##### % Families Making Less Than $35,000")
    st.write("DP03_0076PE + DP03_0077PE + DP03_0078PE + DP03_0079PE")

    st.markdown("##### % Families Making More Than $200,000")
    st.write("DP03_0085PE")
    

    st.subheader("Poverty")

    st.markdown("##### % Families Below the Poverty Level Within Last Year")
    st.write("DP03_0119PE")

    st.markdown("##### % (Married with Kids) Below the Poverty Level Within Last Year")
    st.write("DP03_0123PE")

    st.markdown("##### % (Single Mother with Kids) Below the Poverty Level Within Last Year")
    st.write("DP03_0126PE")

    st.markdown("##### People Below Poverty Level (Under 18)")
    st.write("DP03_0129PE")

    st.markdown("##### People Below Poverty Level (Under 18)")
    st.write("DP03_0133PE")
    st.markdown("---")


    st.subheader("Work")
    
    st.markdown("##### Average Commuting Time")
    st.write("DP03_0025E")
    
    st.markdown("##### Commute via Public Transit")
    st.write("DP03_0021E")

    st.markdown("##### Work from Home")
    st.write("DP03_0024E")

    st.markdown("---")

    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="mediumseagreen",
        box_shadow=True,
        border_size_px=0.5
    )
