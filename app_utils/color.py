"""
Open Research Community Accelorator
Vermont Data App

Color Utility Functions
"""

# Basic Libraries
import streamlit as st
import pandas as pd
import numpy as np
import io

# Color Mapping 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase
import matplotlib.cm as cm



def get_text_color(key):
    from streamlit_theme import st_theme
    theme_dict = st_theme(key=f"theme_{key}")
    if theme_dict is not None:
        theme = theme_dict["base"]
    else:
        theme = "light"  # or your fallback default
    text_color = "white" if theme == "dark" else "black"

    return text_color


def get_colornorm_stats(df, cutoff_scalar):
    ## Simple helper func for DRY
    mean = df['Value'].mean()
    std = df['Value'].std()
    vmin = df['Value'].min()
    vmax = df['Value'].max()
    cutoff = mean + cutoff_scalar * std
    
    return vmin, vmax, cutoff


class TopHoldNorm(mcolors.Normalize):
    """
    Holds out the top x of the color norm for outliers, so they're in the same cmap but just the top `outlier_fraction` of it. 
    """
    def __init__(self, vmin, vmax, cutoff, outlier_fraction=0.1, clip=False):
        super().__init__(vmin, vmax, clip)
        self.cutoff = cutoff
        self.outlier_fraction = outlier_fraction
        self.vmin = vmin
        self.vmax = vmax

    def __call__(self, value, clip=None):
        value = np.array(value)
        result = np.zeros_like(value, dtype=np.float64)

        norm_main_max = 1 - self.outlier_fraction

        # Normalize main range [vmin, cutoff] to [0, norm_main_max]
        mask_main = value <= self.cutoff
        result[mask_main] = (value[mask_main] - self.vmin) / (self.cutoff - self.vmin) * norm_main_max

        # Normalize outliers [cutoff, vmax] to [norm_main_max, 1]
        mask_outlier = value > self.cutoff
        result[mask_outlier] = norm_main_max + (value[mask_outlier] - self.cutoff) / (self.vmax - self.cutoff) * self.outlier_fraction

        return np.clip(result, 0, 1)


def render_colorbar(cmap, norm, vmin, vmax, cutoff, style, label="Scale"):
    fig, ax = plt.subplots(figsize=(5, 0.4))
   
    cb = ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')
    ticks=np.linspace(vmin, cutoff, 5)
    cb.set_label(label)

    if style=="Holdout":
        ticks = ticks[:-1]
        ticks = np.append(ticks, vmax)
    elif style == "Yellow":
        cb.set_label("Scale (Outliers in Yellow)")
    elif style == "Jenk's Natural Breaks":
        cb.set_label("Jenk's")

    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{t:.0f}" for t in ticks])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    
    st.image(buf, use_container_width=True)


def map_outlier_yellow(x, cmap, norm, cutoff):
        if x > cutoff:
            return [255, 255, 0, 180]  # Yellow RGBA
        rgba = cmap(norm(x))
        return [int(c * 255) for c in rgba[:3]] + [180]


def jenks_color_map(df, n_classes, color):
    import jenkspy
    import numpy as np
    import matplotlib.cm as cm
    import matplotlib.colors as colors

    # Handle empty or invalid data
    values = df['Value'].dropna()
    if values.empty:
        df['color_groups'] = np.nan
        st.warning("The variable you are trying to map is an invalid measure. Please select another variable.")
        return {}

    # Get Jenks breaks and remove duplicates
    raw_breaks = jenkspy.jenks_breaks(values, n_classes=n_classes)
    unique_breaks = sorted(set(raw_breaks))

    # Adjust labels to match number of valid bins
    actual_classes = len(unique_breaks) - 1
    group_labels = [f'group_{i+1}' for i in range(actual_classes)]

    # Assign value groups
    df['color_groups'] = pd.cut(
        df['Value'],
        bins=unique_breaks,
        labels=group_labels,
        include_lowest=True
    )

    # Build color map
    cmap = cm.get_cmap(color)
    color_vals = np.linspace(0.1, 0.9, actual_classes)
    jenks_colors = [colors.to_hex(cmap(val)) for val in color_vals]

    # Map to RGBA using your helper function (assumes it exists)
    jenks_cmap_dict = {label: hex_to_rgb255(hex_color)
                       for label, hex_color in zip(group_labels, jenks_colors)}

    return jenks_cmap_dict


def hex_to_rgb255(hex_color):
    import matplotlib.colors as colors
    rgb = colors.to_rgb(hex_color)
    return [int(255 * c) for c in rgb] + [180]


def generate_geojson_colormap(df, column):
    unique_keys = df[column].unique()
    cmap = cm.get_cmap('tab20', len(unique_keys))
    return {
        key: [int(255 * c) for c in cmap(i)[:3]] + [180]  # RGBA
        for i, key in enumerate(unique_keys)
    }


def geojson_add_fill_colors(filtered_geojson, df, column, color_map=None):
    color_map = color_map if color_map else generate_geojson_colormap(df, column)
    for feature in filtered_geojson["features"]:
        district_type = feature["properties"].get(column)
        feature["properties"]["fill_color"] = color_map.get(district_type, [150, 150, 150, 180]) ## default grey
    return filtered_geojson, color_map


def render_rgba_colormap_legend(color_map, title="Legend"):
    """
    Function to render a colormap. Note that this shows everything in the cmap, not just what's being used.
    """
    st.markdown(f"### {title}")
    for label, rgba in color_map.items():
        rgb_str = f"rgb({rgba[0]}, {rgba[1]}, {rgba[2]})"
        
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; margin-bottom: 4px;'>
                <div style='width: 16px; height: 16px; background-color: {rgb_str}; margin-right: 8px; border: 1px solid #aaa;'></div>
                <div>{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def rgba_to_hex(rgba):
    return '#{:02x}{:02x}{:02x}{:02x}'.format(*rgba)

def tab20_rgba(alpha=180):
    cmap = cm.get_cmap('tab20', 20)
    return [
        [int(255 * r), int(255 * g), int(255 * b), alpha]
        for r, g, b, _ in [cmap(i) for i in range(20)]
    ]


def add_fill_colors(df, column, cmap='tab20', alpha=180):
    """
    Add RGBA fill colors to a DataFrame based on a categorical column.

    Args:
        df (pd.DataFrame): The filtered DataFrame to modify.
        column (str): The column to base the color mapping on.
        cmap (str or Colormap): Matplotlib colormap name or object.
        alpha (int): Alpha value (0–255) to append.

    Returns:
        pd.DataFrame: A copy with a 'fill_color' column (RGBA lists).
    """
    df = df.copy()
    unique_keys = sorted(df[column].dropna().unique())
    cmap_obj = cm.get_cmap(cmap, len(unique_keys)) if isinstance(cmap, str) else cmap

    color_map = {
        key: [int(255 * c) for c in cmap_obj(i)[:3]] + [alpha]
        for i, key in enumerate(unique_keys)
    }

    df['rgba_color'] = df[column].map(lambda k: color_map.get(k, [150, 150, 150, alpha]))
    df['hex_color'] = df['rgba_color'].apply(lambda k : rgba_to_hex(k))

    return df
