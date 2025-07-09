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
        ticks = np.append(ticks, vmax)
    elif style == "Yellow":
        cb.set_label("Scale (Outliers in Yellow)")
    elif style == "Jenk's Natural Breaks":
        cb.set_label("Jenk's")

    cb.set_ticks(ticks)
    cb.set_ticklabels([f"{t:.2g}" for t in ticks])

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    plt.close(fig)
    
    st.image(buf, width=450)


def map_outlier_yellow(x, cmap, norm, cutoff):
        if x > cutoff:
            return [255, 255, 0, 180]  # Yellow RGBA
        rgba = cmap(norm(x))
        return [int(c * 255) for c in rgba[:3]] + [180]


def jenks_color_map(df, n_classes, color):
    import jenkspy
    import matplotlib.cm as cm
    from matplotlib import colormaps
    import matplotlib.colors as colors

    if df['Value'].dropna().empty:
        df['color_groups'] = np.nan
        st.warning("The variable you are trying to map is not a valid measure. Please select another variable.")
        return {}

    # Define breaks with "n" classifications and define a "groups" to the dataframe
    breaks = jenkspy.jenks_breaks(df['Value'].dropna(), n_classes=n_classes)            
    group_labels = [f'group_{i+1}' for i in range(n_classes)]
    df['color_groups'] = pd.cut(df['Value'], bins=breaks, labels=group_labels, include_lowest=True)

    # Define a red colormap based on the number of groups selected
    cmap = cm.get_cmap(color)
    color_vals = np.linspace(0.1, 0.9, n_classes)
    jenks_colors = [colors.to_hex(cmap(val)) for val in color_vals]

    # Map RGB colors to each defined category
    jenks_cmap_dict = {str(group): hex_to_rgb255(color) for group, color in zip(group_labels, jenks_colors)}
    
    return jenks_cmap_dict


def hex_to_rgb255(hex_color):
    import matplotlib.colors as colors
    rgb = colors.to_rgb(hex_color)
    return [int(255 * c) for c in rgb] + [180]


