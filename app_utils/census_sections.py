import streamlit as st
from app_utils.color import render_colorbar, map_outlier_yellow, jenks_color_map, get_colornorm_stats, TopHoldNorm
from  matplotlib import colormaps
import matplotlib.cm as cm
import matplotlib.colors as colors
import pydeck as pdk
from app_utils.df_filtering import filter_dataframe, ensure_list
from collections import defaultdict
import altair as alt
import pandas as pd
from app_utils.plot import plot_container
from app_utils.mapping import map_gdf_single_layer, add_tooltip_from_dict



def select_census_geography(census_df):
    col1, col2 = st.columns(2)
    # County selection
    with col1:
        county_list = sorted(census_df["County"].dropna().unique())
        county = st.selectbox("**County**", ["All Counties"] + county_list)
    # Jurisdiction selection
    with col2:
        if county != "All Counties":
            jurisdiction_list = sorted(census_df[census_df["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_list = sorted(census_df["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)
    
    return county, jurisdiction



def filter_census_geography(census_dfs, county, jurisdiction):
    """
    
    """
    filtered_census_dfs = []
    for df in census_dfs:
        filtered_df = df.copy()
        if county != "All Counties":
            filtered_df = filtered_df[filtered_df["County"] == county]
        if jurisdiction != "All Jurisdictions":
            filtered_df = filtered_df[filtered_df["Jurisdiction"] == jurisdiction]

        filtered_census_dfs.append(filtered_df)
        
    return filtered_census_dfs
    

def fill_census_colors(gdf, map_color):
    """
    Note some of this is uesless because it doesn;t matter 
    """
    # n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
    # Define the Jenk's colormap and apply it to the dataframe
    jenks_cmap_dict = jenks_color_map(gdf, 10, map_color)
    gdf['rgba_color'] = gdf['color_groups'].astype(str).map(jenks_cmap_dict)
    # Fill null values with a transparent color
    gdf['rgba_color'] = gdf['rgba_color'].fillna("(0, 0, 0, 0)")
    
    ## potential legacy code to use
    # vmin, vmax, cutoff  = get_colornorm_stats(gdf, 5)
    # cmap = colormaps["Reds"]
    # norm = colors.Normalize(vmin=vmin, vmax=vmax)
    # cmap = cm.get_cmap("Reds")
    # style = st.pills("Outlier Handling:", options=["Jenk's Natural Breaks", "Yellow", "Holdout"], default="Jenk's Natural Breaks", label_visibility="collapsed") # if you want options
    #     if style == "Holdout":
    #     # Option One:  Outliers get the top 10% of the norm (same color, just gradation shifts)
    #     norm = TopHoldNorm(vmin=vmin, vmax=vmax, cutoff=cutoff, outlier_fraction=0.05)
    #     # Convert colors to [R, G, B, A] values
    #     gdf["fill_color"] = gdf['Value'].apply(
    #         lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])
    #     render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    
    # elif style == "Yellow":
    #     # Option Two: Outliers get a separate color (yellow)
    #     norm = colors.Normalize(vmin=vmin, vmax=cutoff, clip=False)
    #     gdf["fill_color"] = gdf["Value"].apply(
    #         lambda x: map_outlier_yellow(x, cmap, norm, cutoff))
    #     render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    return gdf


def process_census_data(gdf, selected_values, map_color):
    gdf = fill_census_colors(gdf, map_color)
    gdf = add_census_tooltip(gdf, selected_values)
    gdf["coordinates"] = gdf.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"]) 
    return gdf


def add_census_tooltip(gdf, selected_values):
    ## hardcode a string to callout the variable we're mapping
    tooltip_fmt = f"{selected_values['Variable']} {selected_values['Measure']}".upper() 
    return add_tooltip_from_dict(gdf, label_to_col={
        "Municipality" : "Jurisdiction",
        tooltip_fmt : "Value"
    })


def mapping_tab(data, map_color="Reds"): 
    st.subheader("Mapping")
    
    ## filter down to column to map
    filtered_2023, selected_values = filter_dataframe(
        data, 
        filter_columns=["Category", "Subcategory", "Variable", "Measure"], 
        key_prefix="mapping_filter_2023")
    filtered_2023 = process_census_data(filtered_2023, selected_values, map_color)
 
    # Normalize the housing variable for monochromatic chloropleth coloring
    vmin, vmax, cutoff  = get_colornorm_stats(filtered_2023, 5)
    cmap = colormaps[map_color]
    
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap(map_color)

    # style = st.pills("Outlier Handling:", options=["Jenk's Natural Breaks", "Yellow", "Holdout"], default="Jenk's Natural Breaks", label_visibility="collapsed") # if you want options
    style = "Jenk's Natural Breaks"

    if style == "Holdout":
        # Option One:  Outliers get the top 10% of the norm (same color, just gradation shifts)
        norm = TopHoldNorm(vmin=vmin, vmax=vmax, cutoff=cutoff, outlier_fraction=0.05)
        # Convert colors to [R, G, B, A] values
        filtered_2023["fill_color"] = filtered_2023['Value'].apply(
            lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])
        render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    
    elif style == "Yellow":
        # Option Two: Outliers get a separate color (yellow)
        norm = colors.Normalize(vmin=vmin, vmax=cutoff, clip=False)
        filtered_2023["fill_color"] = filtered_2023["Value"].apply(
            lambda x: map_outlier_yellow(x, cmap, norm, cutoff))
        render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    
    elif style == "Jenk's Natural Breaks":
        # Option Three: Jenk's Natural Breaks Algorithm
        n_classes=10
        # n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
        # Define the Jenk's colormap and apply it to the dataframe
        jenks_cmap_dict = jenks_color_map(filtered_2023, n_classes, map_color)
        filtered_2023['fill_color'] = filtered_2023['color_groups'].astype(str).map(jenks_cmap_dict)
        # Fill null values with a transparent color
        filtered_2023['fill_color'] = filtered_2023['fill_color'].fillna("(0, 0, 0, 0)")

    # generate and display map
    map = map_gdf_single_layer(
        gdf=filtered_2023,
        view_state=pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)
    )
    st.pydeck_chart(map, height=550)


def select_dataset(col, data_dict, label_prefix):
    """
    Helper func for the comparison tab to select two different datasets to compare. 
    """    
    label_color = "blue" if label_prefix == "Base" else "orange"
    select_dataset = col.selectbox(f"Select :{label_color}[**{label_prefix} Dataset**]", data_dict.keys())
    df = data_dict.get(select_dataset)
    select_county = col.selectbox("Select **County**", sorted(df['County'].unique().tolist()), key=f"{label_prefix}_select_col")
    df = df[df['County'] == select_county].copy()
    select_juridisdictions = col.multiselect(
        "Select **Towns**", 
        options=sorted(list(df['Jurisdiction'].unique())+["All"]), 
        default="All", key=f"{label_prefix}_select_jur"
        )
    select_juridisdictions_df = select_juridisdictions if "All" not in select_juridisdictions else list(df['Jurisdiction'].unique())
    df = df[df['Jurisdiction'].isin(select_juridisdictions_df)]
        
    return df


def get_sets_and_filter(data_dict, label_prefixs, drop_cols=["GEOID", "geometry"], filter_columns=["Category", "Subcategory", "Variable", "Measure"]):
    """
    Function to let the user:
        - select datasets, county, and towns to compare
        - click buttons to add or remove variables
    Returns a dictionary where keys are complicated format strings and values are filtered dataframes (2 for each var)
    """
    st.subheader("Select Datasets to Compare")

    # Dataset selection (left = base, right = comparison)u
    with st.expander("**Filter Datasets**", expanded=True):
        dfs = [
            select_dataset(col, data_dict, label_prefix=label).drop(columns=drop_cols)
            for col, label in zip(st.columns(2), label_prefixs)
        ]

    # Initialize a session state
    if "comparison_var_count" not in st.session_state:
        st.session_state.comparison_var_count = 1
    
    st.subheader("Variables to Investigate")
    st.session_state.comparison_var_count = add_remove_compare_variables(st.session_state.comparison_var_count)

    # Render variable selectors
    results_dict = {}
    for var_i in range(st.session_state.comparison_var_count):
        filtered = ensure_list(filter_dataframe(
            dfs,
            filter_columns=filter_columns,
            key_prefix=f"results{var_i + 1}",
            header=f"#### Variable {var_i + 1}"
        ))
        for df_idx, (df, selected) in enumerate(filtered):
            key=f"**Variable {var_i + 1}**: {' | '.join(selected.values())} : **{label_prefixs[df_idx]} Dataset**"
            results_dict[key] = df

    return results_dict


def compare_tab(data_dict, drop_cols=["GEOID", "geometry"], filter_columns=["Category", "Subcategory", "Variable", "Measure"]):
    label_prefixs = ["Base", "Comparison"]
    results_dict = get_sets_and_filter(data_dict, label_prefixs, drop_cols=drop_cols, filter_columns=filter_columns)

    grouped = defaultdict(dict)
    for key, df in results_dict.items():
        var_name, dataset_name = key.rsplit(':', 1)
        grouped[var_name][f"{dataset_name}"] = df


    # Run plots
    plotting_dict = {
        "Jurisdiction Barplot" : grouped_barplot_by_jurisdiction,
        "County Barplot" : barplot_by_county,
        "County Boxplot" : boxplot_by_county,
    }

    st.divider()
    st.subheader("Results")
    plots = st.multiselect("Select which plots to show", options=plotting_dict.keys())
    for plot in plots:
        plotting_dict[plot](grouped, label_prefixs)


def barplot_by_county(grouped, label_prefixs):
    for var_name, datasets in grouped.items():
        if len(datasets) != 2:
            continue

        totals = []
        for i, (_, df) in enumerate(datasets.items()):
            total = df["Value"].sum()
            totals.append({"Dataset": label_prefixs[i], "Total": total})

        totals_df = pd.DataFrame(totals)

        st.markdown(f"#### {var_name}")
        chart = alt.Chart(totals_df).mark_bar().encode(
                x=alt.X("Dataset:N", title="Dataset", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Total:Q", title="Value"),
                color=alt.Color("Dataset:N", scale=alt.Scale(domain=["Base", "Comparison"], range=["#1f77b4", "#ff7f0e"]))
            ).properties(height=300)
        
        plot_container(totals_df, chart)


def grouped_barplot_by_jurisdiction(grouped, label_prefixs):
    for var_name, datasets in grouped.items():
        if len(datasets) != 2:
            continue

        dfs = list(datasets.values())

        merged = pd.merge(
            dfs[0][["Jurisdiction", "Value"]].rename(columns={"Value": f"{label_prefixs[0]}"}),
            dfs[1][["Jurisdiction", "Value"]].rename(columns={"Value": f"{label_prefixs[1]}"}),
            on="Jurisdiction",
            how="outer"
        ).fillna(0)

        merged_long = merged.reset_index(drop=True).melt(id_vars="Jurisdiction", var_name="Dataset", value_name="Value")
        
        st.markdown(f"#### {var_name}")
        
        chart = alt.Chart(merged_long).mark_bar().encode(
            x=alt.X("Jurisdiction", title="Jurisdiction", axis=alt.Axis(labelAngle=-90), sort=None), ## this is just flat; not sure the best angle
            y="Value",
            color=alt.Color("Dataset:N", scale=alt.Scale(domain=["Base", "Comparison"], range=["#1f77b4", "#ff7f0e"])),
            tooltip=['Jurisdiction', 'Dataset', 'Value'],
            xOffset='Dataset:N'
        ).properties(width=700, height=400)

        plot_container(merged_long, chart)


def boxplot_by_county(grouped, label_prefixs):
    for var_name, datasets in grouped.items():
        if len(datasets) != 2:
            continue

        dfs = list(datasets.values())
        merged = pd.merge(
            dfs[0][["County", "Value"]].rename(columns={"Value": f"{label_prefixs[0]}"}),
            dfs[1][["County", "Value"]].rename(columns={"Value": f"{label_prefixs[1]}"}),
            on="County",
            how="outer"
        )

        merged_long = merged.reset_index(drop=True).melt(id_vars="County", var_name="Dataset", value_name="Value")

        st.markdown(f"#### {var_name}")

        chart = alt.Chart(merged_long).mark_boxplot().encode(
            x=alt.X("Value:Q", title="Value"),
            y=alt.Y("County:N", title="County", axis=alt.Axis(labelAngle=-90), sort=None),
            color=alt.Color("Dataset:N", scale=alt.Scale(domain=["Base", "Comparison"], range=["#1f77b4", "#ff7f0e"]))
        ).configure_boxplot(size=100).properties(width=700, height=400)

        plot_container(merged_long.dropna(), chart)


def add_remove_compare_variables(comparison_var_count):
    """
    Adds and removes comparison variables from the comparison page.
    """

    # Button row (above variable filters)
    _, col1, col2, _ = st.columns([2, 1, 1, 2])
    with col1:
        add_clicked = st.button(label="Add Variable", key="add_btn", disabled=comparison_var_count == 5)
    with col2:
        remove_clicked = st.button(label="Remove Variable", key="remove_btn", disabled=comparison_var_count == 1)

    # Update variable count AFTER buttons render (avoids Streamlit rerun issues)
    if add_clicked:
        comparison_var_count += 1
    if remove_clicked:
        comparison_var_count -= 1

    return comparison_var_count