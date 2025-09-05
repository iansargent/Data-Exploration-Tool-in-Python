"""
Open Research Community Accelorator
Vermont Data App

Zoning Utility Functions
"""

# Streamlit
import io

import altair as alt
import pandas as pd
import streamlit as st

from app_utils.color import add_fill_colors
from app_utils.mapping import add_tooltip_from_dict, map_gdf_single_layer


def process_zoning_data(gdf):

    """
    wrapper for all the cleaning, color, tooltip functions for zoning dataset
    """
    gdf = clean_zoning_gdf(gdf)
    gdf = add_fill_colors(gdf, column="District Type", cmap="tab20")
    gdf = add_zoning_tooltip(gdf)
    return gdf


def clean_zoning_gdf(gdf):
    """
    Function to format columns for tooltip display and prune unneeded columns
    """

    ## replace names
    gdf["District Type"] = gdf["District Type"].replace(
        {
            "Primarily Residential": "Residential",
            "Mixed with Residential": "Mixed",
            "Nonresidential": "Nonresidential",
            "Overlay not Affecting Use": "Overlay",
        }
    )

    ## format the acres string
    gdf["Acres_fmt"] = gdf["Acres"].map(lambda x: f"{x:,.0f}")

    return gdf


def add_zoning_tooltip(gdf):
    return add_tooltip_from_dict(
        gdf,
        gdf_name="Zoning",
        label_to_col={
            "District": "Jurisdiction District Name",
            "Type": "District Type",
            "Acreage": "Acres_fmt",
        },
    )



def zoning_district_map(gdf):
    return map_gdf_single_layer(gdf)


## reports and comparison ##


def district_comparison(filtered_gdf):
    """
    Displays an interactive AgGrid table and returns selected rows.

    @param gdf: A GeoDataFrame.
    @return: The selected rows in the AgGrid Table.
    """

    df = filtered_gdf.copy()
    if "geometry" in df.columns:
        df = df.drop(columns=["geometry"])

    districts = st.multiselect(
        label="Select Districts to Compare",
        options=sorted(df["Jurisdiction District Name"].dropna().unique()),
    )

    return districts


def zoning_comparison_table(filtered_gdf, selected_districts):
    """
    Takes selected rows from AgGrid, creates a comparison table, and displays it.

    @param selected_rows: The selected rows from an AgGrid interactive table.
    @return: The comparison table as a dataframe
    """
    from datetime import datetime
    from functools import reduce

    from streamlit_extras.dataframe_explorer import dataframe_explorer

    if len(selected_districts) == 0:
        return

    filtered_gdf = filtered_gdf[
        filtered_gdf["Jurisdiction District Name"].isin(selected_districts)
    ]

    dfs = []
    for _, row in filtered_gdf.iterrows():
        district_name = row.get("Jurisdiction District Name", "District")
        df_long = pd.DataFrame(row).reset_index()
        df_long.columns = ["Zoning Regulation", district_name]
        dfs.append(df_long)

    combined_df = reduce(
        lambda left, right: pd.merge(left, right, on="Zoning Regulation", how="outer"),
        dfs,
    )

    st.subheader("District Comparisons")
    filtered_combined_df_sorted = dataframe_explorer(combined_df, case=False)
    st.dataframe(filtered_combined_df_sorted, use_container_width=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    buffer = io.BytesIO()
    filtered_combined_df_sorted.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="Export Comparison Table to Excel",
        data=buffer,
        file_name=f"comparison_table_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    return combined_df


def compute_acerage_metrics(gdf):
    df = gdf.drop(columns=["geometry"])
    metrics = {
        "total_acreage": df["Acres"].sum(),
        "num_districts": len(df),
        "num_residential_districts": len(df[df["District Type"] == "Residential"]),
        "residential_acreage": df[df["District Type"] == "Residential"]["Acres"].sum()
        
    }
    return metrics


def plot_acreage(gdf):
    acres_by_type = gdf.groupby("District Type")["Acres"].sum().fillna(0)
    colors = gdf.drop_duplicates("District Type")[["District Type", "hex_color"]]

    acres_df = acres_by_type.reset_index().merge(colors, on="District Type", how="left")
    total_acres = acres_df["Acres"].sum()
    acres_df["Percent"] = 100 * acres_df["Acres"] / total_acres

    bar_chart = (
      alt.Chart(acres_df)
      .mark_bar()
      .encode(
          x=alt.X(
            "District Type:N", 
            sort="-y", 
            title="District Type", 
            axis=alt.Axis(labelAngle=0)
          ),
          y=alt.Y("Acres:Q", title="Acres"),
          color=alt.Color("hex_color:N", scale=None, legend=None),
          tooltip=[
              "District Type",
              alt.Tooltip("Acres:Q", format=",.0f"),
              alt.Tooltip("Percent:Q", format=".1f", title="% of Total")
          ],
      )
      .properties(height=500, title="Zoning Acreage by District Type")
   )

    return bar_chart


### API STUFF
# zoning_router = create_data_router("/zoning", load_zoning_data, process_zoning_data)
