import streamlit as st
from app_utils.color import render_colorbar, map_outlier_yellow, jenks_color_map, get_colornorm_stats, TopHoldNorm
from  matplotlib import colormaps
import matplotlib.cm as cm
import matplotlib.colors as colors
import pydeck as pdk
from streamlit_rendering import filter_dataframe, ensure_list
from app_utils.plot import sort_bar_chart
from collections import defaultdict
import altair as alt
import pandas as pd
from streamlit_extras.chart_container import chart_container


def mapping_tab(data): 
    
    # Project meaningful columns to lat/long
    filtered_2023, selected_value = filter_dataframe(data, filter_columns=["Category", "Subcategory", "Variable", "Measure"], key_prefix="mapping_filter")
    filtered_2023.to_crs(epsg=4326)

    # Normalize the housing variable for monochromatic chloropleth coloring
    vmin, vmax, cutoff  = get_colornorm_stats(filtered_2023, 5)
    cmap = colormaps["Reds"]
    
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Reds")

    style = st.radio("Outlier Handling:", options=["Jenk's Natural Breaks", "Yellow", "Holdout"], horizontal=True)

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
        # Option Two: Jenk's Natural Breaks Algorithm
        # Using a slider, adjust the number of "groups" in the data
        col1, _, _ = st.columns(3)
        n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
        # Define the Jenk's colormap and apply it to the dataframe
        jenks_cmap_dict = jenks_color_map(filtered_2023, n_classes, "Reds")
        filtered_2023['fill_color'] = filtered_2023['color_groups'].astype(str).map(jenks_cmap_dict)
        # Fill null values with a transparent color
        filtered_2023['fill_color'] = filtered_2023['fill_color'].fillna("(0, 0, 0, 0)")

    # Convert the geometry column to GeoJSON coordinates
    filtered_2023["coordinates"] = filtered_2023.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"]) 

    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=filtered_2023,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True)

    # Set the map center and zoom settings
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)

    # Display the map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{Jurisdiction}: {Value}"}), height=550)
    

def select_dataset(col, data_dict, label_prefix):
    """
    Helper func for the comparison tab to select two different datasets to compare. 
    """
    base_comparison__color = "blue" if label_prefix == "Base" else "orange"
    
    select_val = col.selectbox(f":{base_comparison__color}[**{label_prefix} Dataset**]", data_dict.keys())
    df = data_dict.get(select_val)
    subcol1, subcol2 = col.columns(2)
    select_col = subcol1.selectbox("**County**", df['County'].unique(), key=f"{label_prefix}_select_col")
    df = df[df['County'] == select_col].copy()
    select_juridisdictions = subcol2.multiselect(
        "**Towns**", 
        options=sorted(list(df['Jurisdiction'].unique())+["All"]), 
        default="All", key=f"{label_prefix}_select_jur"
        )
    select_juridisdictions = select_juridisdictions if "All" not in select_juridisdictions else list(df['Jurisdiction'].unique())
    df = df[df['Jurisdiction'].isin(select_juridisdictions)]
    
    return df


def get_sets_and_filter(data_dict, label_prefixs):
    """
    Function to let the user:
        select datasets, county, and towns to compare
        select number of variables to filter
        filter dataframes as they select those variables

    Returns a dictionary where keys are complicated format strings and values are filtered dataframes (2 for each var)
    """
    st.subheader("Select Datasets")
    dfs = [
        select_dataset(col, data_dict, label_prefix=label).drop(columns=["GEOID", "geometry"])
        for col, label in zip(st.columns([10, 1, 10]), [label_prefixs[0], None, label_prefixs[1]])
        if label is not None
    ]
    
    st.divider()
    
    c1, c2, c3 = st.columns([6, 5, 6])
    c2.markdown("##### Select the Number of Variables")
    var_count = c2.slider("Select **Number of Variables**", 1, 5, 1, label_visibility="collapsed")
    
    results_dict = {
        f"**Variable {var_i+1}**: {' | '.join(selected.values())} : **{label_prefixs[df_idx]} Dataset**": df 
        for var_i in range(var_count)
        for df_idx, (df, selected) in enumerate(ensure_list(
            filter_dataframe(
                dfs,
                filter_columns=["Category", "Subcategory", "Variable", "Measure"],
                key_prefix=f"results{var_i+1}",
                header=f"#### Variable {var_i + 1} "
            )
        ))
    }
    return results_dict


def compare_tab(data_dict):
    label_prefixs = ["Base", "Comparison"]
    results_dict = get_sets_and_filter(data_dict, label_prefixs)

    grouped = defaultdict(dict)
    for key, df in results_dict.items():
        var_name, dataset_name = key.rsplit(':', 1)
        grouped[var_name][f"{dataset_name}"] = df

    ## run plots
    plotting_dict = {
        "Jurisdiction Barplot" : grouped_barplot_by_jurisdiction,
        "County Barplot" : barplot_by_county,
        "County Boxplot" : boxplot_by_county, # NOTE: Only is meaningful when datasets are at the county level
    }

    st.divider()
    st.subheader("Plotting")
    plots = st.pills("Select which plots to show", options=plotting_dict.keys(), selection_mode="multi", label_visibility="collapsed")
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
        
        with chart_container(totals_df):
            st.altair_chart(
                alt.Chart(totals_df)
                .mark_bar()
                .encode(
                    x=alt.X("Dataset:N", title="Dataset", axis=alt.Axis(labelAngle=-60)),
                    y=alt.Y("Total:Q", title="Value"),
                    color="Dataset:N"
                )
                .properties(height=300),
                use_container_width=True
            )


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
        
        c1,_, _, _, _ = st.columns(5)
        
        with c1:
            sort = sort_bar_chart(merged_long)

        chart = alt.Chart(merged_long).mark_bar().encode(
            x=alt.X("Jurisdiction", title="Jurisdiction", axis=alt.Axis(labelAngle=-90), sort=sort), ## this is just flat; not sure the best angle
            y=alt.Y("Value"),
            color='Dataset',
            tooltip=['Jurisdiction', 'Dataset', 'Value'],
            xOffset='Dataset:N'
        ).properties(width=700, height=400)
        
        with chart_container(merged_long):
            st.altair_chart(chart)


def boxplot_by_county(grouped, label_prefixs):
    # For each variable, ensure there are two datasets
    for var_name, datasets in grouped.items():
        if len(datasets) != 2:
            continue
        
        # Get a list of the two dataset values
        dfs = list(datasets.values())

        # Merge the two datasets on County (including the datasets prefix)
        merged = pd.merge(
            dfs[0][["County", "Value"]].rename(columns={"Value": f"{label_prefixs[0]}"}),
            dfs[1][["County", "Value"]].rename(columns={"Value": f"{label_prefixs[1]}"}),
            on="County",
            how="outer"
        )

        # Melt into long format for plotting
        merged_long = merged.reset_index(drop=True).melt(id_vars="County", var_name="Dataset", value_name="Value")
        
        # Create the comparison boxplot
        boxplot = alt.Chart(merged_long).mark_boxplot().encode(
            x="Value",
            y=alt.Y("County", title=None, axis=alt.Axis(labelAngle=0)),
            color='Dataset',
            tooltip=['County', 'Dataset', 'Value']
        ).configure_boxplot(size=100).properties(width=700, height=400)

        # Display the plot
        st.markdown(f"#### {var_name}")
        with chart_container(merged_long.dropna()):
            st.altair_chart(boxplot)

