"""
Open Research Community Accelorator
Vermont Data App

Plotting Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from app_utils.analysis import get_column_type, get_skew
from streamlit_extras.metric_cards import style_metric_cards 


def safe_altair_plot(plot, data_type,chart_col=False):
    if chart_col:
        try:
            chart_col.altair_chart(plot)
        except:
            chart_col.warning(f"Not enough {data_type} available for the selected geography.")

    else:
        try:
            st.altair_chart(plot)
        except:
            st.warning(f"Not enough {data_type} data available for the selected geography.")


def donut_chart(source, colorColumnName, height=300, width=300, innerRadius=90, fontSize=40, titleFontSize=14, fillColor="mediumseagreen", title="Donut Chart", 
                stat=0, text_color="grey", inverse=False):
    
    if inverse:
        range=["whitesmoke", fillColor]
        source = source.sort_values(by=colorColumnName, ascending=False)
    else:
        range=[fillColor, "whitesmoke"]
        source = source.sort_values(by="Value", ascending=True)
    
    donut = alt.Chart(source).mark_arc(innerRadius=innerRadius).encode(
        theta=alt.Theta("Value:Q"),
        color=alt.Color(f"{colorColumnName}:N", scale=alt.Scale(
            range=range), legend=None),
        tooltip=[f"{colorColumnName}:N", alt.Tooltip("Value:Q", title="Percentage", format=".1%")]
        ).properties(height=height, width=width)

    center_label = alt.Chart(pd.DataFrame({'text': [f"{stat:.1%}"]})
                             ).mark_text(fontSize=fontSize, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    donut_chart = alt.layer(donut, center_label).properties(
        title=title).configure_title(fontSize=titleFontSize, anchor="middle")
    
    return donut_chart


def bar_chart(source, title_geo, XcolumnName, YcolumnName, xType=":N", yType=":Q", YtooltipFormat=",.0f", yFormat=",.0f", XlabelAngle=-50, 
                     fillColor="mediumseagreen", height=400, width=400, barWidth=60, title="Bar Chart", titleFontSize=17, distribution=True,
                     labelFontSize=10.5):
    
    tooltip_list = [XcolumnName, alt.Tooltip(YcolumnName, format=YtooltipFormat)]
    
    if distribution:
        source[f"% of {YcolumnName}"] = source[YcolumnName] / source[YcolumnName].sum()
        tooltip_list.append(alt.Tooltip(f"% of {YcolumnName}", format=".1%"))

    bar_chart = alt.Chart(source).mark_bar().encode(
        x=alt.X(XcolumnName + xType, sort=source[XcolumnName].tolist(),
                    axis=alt.Axis(labelAngle=XlabelAngle, labelFont="Helvetica Neue", labelFontWeight='normal', labelFontSize=labelFontSize, titleFont="Helvetica Neue")),
        y=alt.Y(YcolumnName + yType, axis=alt.Axis(labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue", format=yFormat)),
        tooltip=tooltip_list).configure_mark(color=fillColor, width=barWidth
        ).properties(height=height, width=width, title=alt.Title(f"{title} | {title_geo}", anchor='middle', fontSize=titleFontSize)).interactive()
    
    return bar_chart
    

def single_column_plot(df, selected_column):
    """
    Create a single column plot based on the data type of the selected column.
    The plot type is determined by the data type of the column.

    @param df: A pandas DataFrame object.
    @param selected_column: The name of the column in the DataFrame (string).
    @return: The Altair plot objects associated with the data type of the column.
    """
    from statsmodels.stats.weightstats import DescrStatsW

    # Define the plotting source as the one selected column without missing values
    source = df[[selected_column]].dropna()
    # Get the column type
    column_type = get_column_type(df, selected_column)
    
    # If the column is categorical (object type)
    if column_type == 'object':
        # Create a sorted BAR CHART using Altair (descending)
        bar_title = alt.TitleParams(f"Bar Chart of {selected_column}", anchor='middle', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        bar_chart = alt.Chart(source, title=bar_title).mark_bar().encode(
            x=alt.X(f"{selected_column}:N", sort='-y'),
            y='count()',
            tooltip=['count()']
        ).configure_mark(
            color = "tomato"
        ).properties(
            width=600,
            height=400
        )
        # Disply the chart
        st.altair_chart(bar_chart, use_container_width=True)
        
        # Return the bar chart
        return bar_chart

    # If the column is numeric
    elif column_type in ['int64', 'float64']:
        # Ensure the data type is numeric
        df[selected_column] = pd.to_numeric(df[selected_column], errors='coerce')
        # Redefine the plotting source
        source = df[[selected_column]].dropna()

        # Define the 95% confidence interval bounds
        d = DescrStatsW(source[selected_column])
        ci_low, ci_high = d.tconfint_mean()
        CI = (ci_low, ci_high)

        # Calculate descriptive statistics
        var_mean = source[selected_column].mean()
        var_med = source[selected_column].median()
        var_std_dev = source[selected_column].std()
        
        skew = get_skew(source, selected_column)

        if abs(skew) > 1:
            skew_warning = ("NOTE: This Distribution is **Slightly Skewed**. " +
                            "It is best to look at the **Median** instead of **Mean** in this case!")
            st.warning(skew_warning)
        
        
        # Display variable descriptive statistics
        column1, column2 = st.columns(2) 
        column3, column4 = st.columns(2)
        column1.metric(label="**Mean**", value = f"{var_mean:,.2f}", help="The *average* of the sample.")
        column2.metric(label="**Median**", value = f"{var_med:,.2f}", help="The *middle value* of the sample.")
        column3.metric(label="**Standard Deviation**", value = f"{var_std_dev:,.3f}", 
                       help="The average amount that each observation differs from the sample mean. " \
                       "Standard deviation also measures the overall spread of the sample for a given variable.")
        column4.metric(label="**95% Confidence Interval**", value = f"[{ci_low:,.1f}  -  {ci_high:,.1f}]",
                       help="The range of values in which we are 95% confident the variable's population " \
                       "mean falls into. In other words, if we repeatedly sampled this population, our " \
                       "sample means would fall within this interval 95% of the time.")

        style_metric_cards(
            background_color="whitesmoke",
            border_left_color="mediumseagreen",
            border_size_px=0.5
        )
        
        # Slider for number of bins in the histogram
        bin_slider = st.slider(
            "**Select the Level of Detail**", 
            min_value=2, 
            max_value=min(len(np.unique(source[selected_column])) // 2, 100), 
            value=30,
            help="Controls how many bars appear in the histogram. Higher = more detail.",
            key=f"bin_slider_{selected_column}"
        )

        # Histogram
        hist_title = alt.TitleParams(f"Histogram Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        histogram = alt.Chart(source, title=hist_title).mark_bar().encode(
            x=alt.X(f"{selected_column}:Q", bin=alt.Bin(maxbins=bin_slider), title=selected_column),
            y=alt.Y('count():Q', title='Count'),
            tooltip=[alt.Tooltip('count()', title='Count')]
        ).properties(height=450)

        # Density Plot
        dens_title = alt.TitleParams(f"Density Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        density = alt.Chart(source, title=dens_title).transform_density(
            f"{selected_column}",
            as_=[f"{selected_column}", "density"],
            extent=[source[selected_column].min(), source[selected_column].max()]
        ).mark_area(color='tomato').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column),
            y=alt.Y('density:Q', title='Density')
        ).interactive()

        # Boxplot
        box_title = alt.TitleParams(f"Boxplot Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        boxplot = alt.Chart(source, title=box_title).mark_boxplot(color='dodgerblue').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column)
        ).configure_mark().configure_boxplot(size=160
        ).properties(width=400, height=400)

        # Display the histogram
        st.altair_chart(histogram, use_container_width=True)
                
        # Display the density plot
        st.altair_chart(density, use_container_width=True)
        
        # Display the box plot below
        st.altair_chart(boxplot, use_container_width=True)

        # Return the plots and confidence interval
        return histogram, boxplot, CI, density

    # If the column is datetime
    elif pd.api.types.is_datetime64_any_dtype(df[selected_column]):
        # Clean the datetime column
        source[selected_column] = pd.to_datetime(source[selected_column])
        
        # Let user pick the numeric column to plot
        numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != selected_column]
        
        # If there are no numeric columns to plot over time
        if not numeric_cols:
            st.warning("No numeric columns available to plot against time.")
            return
        
        # Define the variable to plot over time
        y_column = st.selectbox("Select a column to plot over time:", numeric_cols)

        # Create the LINE CHART
        line_title = alt.TitleParams(f"Plot of {y_column} Over Time", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        chart = alt.Chart(df, title=line_title).mark_line().encode(
            x=alt.X(f"{selected_column}:T", title="Time"),
            y=alt.Y(f"{y_column}:Q", title=y_column),
            color = alt.value("dodgerblue"),
        )

        # Create the LOESS curve to add to the time series plot 
        time_chart = chart + chart.transform_loess(
            f"{selected_column}", f"{y_column}", bandwidth=0.2
        ).mark_line().encode(color = alt.value("tomato"))
        
        # Display the chart
        st.altair_chart(time_chart, use_container_width=True)
        
        # Return the time series chart
        return time_chart

    # If the column is boolean
    elif column_type == 'bool':
        # Create a pie chart using Altair
        pie_title = alt.TitleParams("Pie Chart of {selected_column}", anchor='middle', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        pie_chart = alt.Chart(source, title=pie_title).mark_arc().encode(
            theta='count()',
            color=alt.Color(f"{selected_column}:N"),
            tooltip=[alt.Tooltip(f"{selected_column}:N", title="Category"),
                     alt.Tooltip(f"count()", title="Count")]
        )
        # Display the chart
        st.altair_chart(pie_chart, use_container_width=True)
        
        # Return the pie chart
        return pie_chart

    # If the column data type is not recognized (int, float, object, datetime, bool)
    else:
        st.write(f"Cannot visualize {selected_column}.")


def numeric_numeric_plots(df, col1, col2):
    """
    Create a scatterplot with regression line and heatmap 
    if two numeric variables are selected. Add a group by option
    for the scatterplots and use color as the grouping variable.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column (string).
    @param col2: The name of the second numeric column (string).
    @return: Altair scatterplot, scatterplot with lines, residual plot, and heatmap (Chart type).
    """
    from sklearn.linear_model import LinearRegression


    # Define the plotting source
    source = df[[col1, col2]].dropna()

    # Select only categorical columns (including boolean type)
    categorical_columns = df.select_dtypes(include=["object", "category", "bool"])
    
    # Create a list to store categorical column names
    categorical_column_names = []
    for col in categorical_columns.columns:
        if df[col].nunique(dropna=True) <= 6:
            categorical_column_names.append(col)

    # Create a select box for the group-by variable for the scatterplot
    grp_by = st.selectbox(
        f"OPTIONAL: Select a variable to summarize by", 
        ["None"] + sorted(categorical_column_names), 
        index=0,
        key=f"num-num-grp_by_{categorical_column_names}"
    )

    # If they select a group-by variable
    if grp_by != "None":
        # Create a new plotting source including the grp-by column
        source = df[[col1, col2, grp_by]].dropna()
        # Define the point colors as a factor of the variable
        color = alt.Color(f"{grp_by}:N", title=grp_by)
    else:
        # Just use the default point color of "mediumseagreen"
        color = alt.value("mediumseagreen")

    # SCATTERPLOT
    scatter_title = alt.TitleParams(f"Scatterplot of {col1} v.s. {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    scatterplot = alt.Chart(source, title=scatter_title).mark_square(
        opacity = 0.7
    ).encode(
        x = alt.X(f"{col1}:Q", title=col1).scale(zero=False),
        y = alt.Y(f"{col2}:Q", title=col2).scale(zero=False),
        color = color,
        tooltip=[col1, col2] + ([grp_by] if grp_by != "None" else [])
    )

    # REGRESSION LINE
    regression_line = scatterplot.transform_regression(
        f"{col1}", f"{col2}"
    ).mark_line().encode(
        color=alt.value("cornflowerblue"),
        size=alt.value(1.5)
    )

    # LOESS LINE
    loess_line = scatterplot.transform_loess(
        f"{col1}", f"{col2}"
    ).mark_line().encode(
        color=alt.value("tomato"),
        size=alt.value(1.5)
    )

    scatterplot_with_lines = scatterplot + regression_line + loess_line

    # RESIDUAL PLOT

    # Define the X and y columns for calculating metrics
    X = source[[col1]]
    y = source[col2]

    model = LinearRegression().fit(X, y)

    y_pred = model.predict(X)
    residuals = y  - y_pred

    # Add predictions and residuals to the DataFrame
    resid_df = pd.DataFrame({
        f'Predicted {col2}' : y_pred,
        'Prediction Error' : residuals
    })
    
    resids_title = alt.TitleParams(f"Residual Plot of {col2} Predictions", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    resids = alt.Chart(resid_df, title=resids_title).mark_square(color = "tomato").encode(
        x = alt.X(f'Predicted {col2}', title = 'Predicted'),
        y = alt.Y('Prediction Error', title = 'Residual'),
        tooltip=[f'Predicted {col2}', 'Prediction Error']).interactive()

    # Optional horizontal zero line
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color = 'black').encode(y='y')

    resid_plot = resids + zero_line

    # Create bins for the x and y axes
    col1_bins = np.linspace(df[col1].min(), df[col1].max(), 21).round().astype(int)
    col2_bins = np.linspace(df[col2].min(), df[col2].max(), 21).round().astype(int)

    # Ensure bins are unique and do not overlap
    col1_bins_unique = np.unique(col1_bins)
    col2_bins_unique = np.unique(col2_bins)
    col1_intervals = len(col1_bins_unique) - 1
    col2_intervals = len(col2_bins_unique) - 1

    # Create evenly-spaced labels for the bins
    col1_labels = range(1, col1_intervals + 1)
    col2_labels = range(1, col2_intervals + 1)

    # Create bins for the x axis
    df['x_bin'] = pd.cut(
        df[col1], 
        bins=col1_bins_unique, 
        labels=col1_labels, 
        include_lowest=True
    )
    # Create bins for the y axis
    df['y_bin'] = pd.cut(
        df[col2], 
        bins=col2_bins_unique, 
        labels=col2_labels, 
        include_lowest=True
    )

    # Save for changing the bin order
    x_order = df['x_bin'].cat.categories
    y_order = df['y_bin'].cat.categories

    # Convert bins to strings
    df['x_bin'] = df['x_bin'].astype(str)
    df['y_bin'] = df['y_bin'].astype(str)

    # Altair heatmap
    heatmap_title = alt.TitleParams(f"Heatmap Distribution of {col1} v.s. {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    heatmap = alt.Chart(df, title=heatmap_title).mark_rect().encode(
        x=alt.X('x_bin:O', sort=[str(c) for c in x_order], title=col1),
        y=alt.Y('y_bin:O', sort=[str(c) for c in reversed(y_order)], title=col2),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange'), title="Count"),
        tooltip=['count():Q']
    ).properties(
        width=500,
        height=400
    ).configure_view(
        strokeWidth=0
    )

    # Return all computed metrics and plots
    return scatterplot, scatterplot_with_lines, resid_plot, heatmap


def regression_metric_cards(df, col1, col2):
    """
    Calculates and displays regression metrics to a page. Metrics include
    sample size, correlation, R-squared, model strength, MAE, and p-value 
    (F statistic).

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column (string).
    @param col2: The name of the second numeric column (string).
    """

    from sklearn.linear_model import LinearRegression
    from sklearn.feature_selection import f_regression
    from sklearn.metrics import mean_absolute_error

    # Define the regression dataframe with the two columns of interest
    source = df[[col1, col2]].dropna()
    
    # Define the X and y columns for calculating metrics
    X = source[[col1]]
    y = source[col2]

    ## SAMPLE SIZE
    sample_size = len(source)

    ## CORRELATION
    corr_df = source[[col1, col2]].corr(min_periods=10, numeric_only=True)
    correlation = corr_df.loc[col1, col2]

    ## MODEL STRENGTH (Based on the correlation value)
    model_str = "No Relationship"
    if abs(correlation) < 0.1:
        model_str = "Weak"
    elif abs(correlation) < 0.3:
        model_str = "Mod -"
    elif abs(correlation) < 0.6:
        model_str = "Mod +"
    elif abs(correlation) <= 1:
        model_str = "Strong"

    # R-SQUARED
    r_squared = correlation ** 2

    ## MEAN ABSOLUTE ERROR (MAE)
    # Define a simple linear model
    model = LinearRegression().fit(X, y)
    # Obtain the predicted y values
    y_pred = model.predict(X)
    # Calculate the MAE using the observations and predictions
    mae = mean_absolute_error(y, y_pred)

    ## OVERALL MODEL P-VALUE
    _, p = f_regression(X, y)
    p_value = round(p[0], 4)
    # If the rounded p-value is still zero, display it as less than 0.0001
    display_value = f"{p_value:.4f}" if p_value > 0 else "p < 0.0001"

    
    st.subheader("Linear Regression Model Metrics")
    # Set up formatting columns for display (2 rows of 3)
    column3, column4, column5 = st.columns(3)
    column6, column7, column8 = st.columns(3)
    
    # Use metric cards to display each metric
    column3.metric(label="**Sample Size (N)**", value = f"{sample_size}", 
                   help="This is the number of observations in the sample. Typically, " \
                   "a larger sample size leads to more accurate results.")
    column4.metric(label="**Correlation (R)**", value=f"{correlation:.2f}", 
                   help="This value shows the strength and direction of the relationship between " \
                   "two variables. +1 indicates a perfect positive correlation, 0 indicates no " \
                   "correlation, and -1 indicates a perfect negative correlation.")
    column5.metric(label="**Model Strength**", value = f"{model_str}", 
                   help="Based on the correlation, we've determined to general stength of the relationship here.\n\n" \
                   "**Note**: Model strength is highly contextual and required further investigation.")    
    column6.metric(label="**R-Squared**", value = f"{r_squared * 100:.0f}%", 
                   help="This value shows the percent of variation seen in one variable that can be " \
                   "attributed to the other.")    
    column7.metric(label="**Mean Absolute Error**", value = f"{mae:,.2f}", 
                   help="On average, this is the margin that the linear model's predictions differ " \
                   "from the actual observations.")
    column8.metric(label="**Model Significance**", value = display_value, 
                   help="Generally, this value helps determine if there is any relationship between the two " \
                   "variables being investigated. If p < 0.05, we conclude that it is likely that there " \
                   "is some sort of relationship (at a 5% significance level).")

    # Metric card customizations
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="cornflowerblue",
        box_shadow=True,
        border_size_px=0.5
    )


def display_numeric_numeric_plots(df, col1, col2, scatterplot, scatterplot_with_lines, resid_plot, heatmap):
    """
    Display a scatterplot, regression line, heatmap, and correlation coefficient
    if two numeric variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column.
    @param col2: The name of the second numeric column.
    @param scatterplot: Altair scatterplot (Chart type).
    @param scatterplot_with_lines: Altair scatterplot with loess and linreg lines (Chart type).
    @param resid_plot: Altair residual plot (Chart type).
    @param heatmap: Altair heatmap (Chart type).
    """  
    # Define the plotting source
    source = df[[col1, col2]].dropna()
    
    # Set title for scatterplots
    st.subheader(f"Scatterplots", help="HELLO!")
    # Formatting plot output with two columns
    column1, column2 = st.columns(2)  
    # First, show the scatterplot
    with column1:
        st.altair_chart(scatterplot.interactive(), use_container_width=True)  
    # Next to it, show the regression line on top of the scatterplot
    with column2:
        st.altair_chart((scatterplot_with_lines).interactive(), use_container_width=True)

    # Display Regression Metrics
    regression_metric_cards(df, col1, col2)

    with st.container():
        st.subheader("Residuals")
        st.altair_chart(resid_plot, use_container_width=True)

    # Below the regression metrics, display the table and the heatmap
    with st.container():
        # Define the space ratio for the table and heatmap
        col_table, col_heatmap = st.columns([1, 3])

        # Display the table
        with col_table:
            st.subheader("Table")
            st.dataframe(
                data=source.style.format("{:.2f}"),
                hide_index=True,
                column_order=(col1, col2),
                use_container_width=True
            )
        # Display the heatmap
        with col_heatmap:
            st.subheader("Heatmap")
            st.altair_chart(heatmap, use_container_width=True)


def numeric_categorical_plots(df, col1, col2):
    """
    Create a boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first column (string).
    @param col2: The name of the second column (string).
    @return: Boxplot (Chart), Confidence Interval Plot (Chart), numeric column name, and categorical column name.
    """
    # Get the needed columns from the DataFrame and drop missing values
    source = df[[col1, col2]].dropna()

    # Define the data types of the first selected column
    col1_type = get_column_type(df, col1)

    # If the first column is numeric and the second is categorical
    if col1_type in ['int64', 'float64']:
        # Define the numeric and non-numeric columns
        numeric_col = col1
        non_numeric_col = col2
            
        # MULTI BOXPLOT
        mbox_title1 = alt.TitleParams(f"Boxplot Distributions of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        multi_box = alt.Chart(source, title=mbox_title1).mark_boxplot(size=40).encode(
            x = alt.X(f"{col2}:N", sort='-y', title=col2),
            y = alt.Y(f"{col1}:Q", title=col1),
            color = alt.Color(f"{col2}:N", title=col2, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col2}:N", f"{col1}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_title1 = alt.TitleParams(f"95% Confidence Intervals of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        error_bars = alt.Chart(source, title=error_title1).mark_errorbar(extent='ci').encode(
            alt.X(f"{col1}").scale(zero=False),
            alt.Y(f"{col2}:O", sort='-x', title=col2)
        )

        # Calculate the mean of col1 for each category in col2
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X(f"{col1}:Q", aggregate='mean'),
            y = alt.Y(f"{col2}:O", sort='-x', title=col2)

        )

        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points

        # Return both plots
        return multi_box, confint_plot, numeric_col, non_numeric_col

    # If the first column is categorical and the second is numeric
    else:
        # Define the numeric and non-numeric columns
        numeric_col = col2
        non_numeric_col = col1
        
        # MULTI BOXPLOT
        mbox_title2 = alt.TitleParams(f"Boxplot Distributions of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        multi_box = alt.Chart(source, title=mbox_title2).mark_boxplot(size=40).encode(
            x = alt.X(f"{col1}:N", sort='-y', title=col1),
            y = alt.Y(f"{col2}:Q", title=col2),
            color = alt.Color(f"{col1}:N", title=col1, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col1}:N", f"{col2}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_title2 = alt.TitleParams(f"95% Confidence Intervals of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        error_bars = alt.Chart(source, title=error_title2).mark_errorbar(extent='ci').encode(
            alt.X(f"{col2}").scale(zero=False),
            alt.Y(f"{col1}:O", sort='-x', title=col1)
        )

        # Calculate the mean of col2 for each category in col1
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X(f'{col2}:Q', aggregate='mean'),
            y = alt.Y(f"{col1}:O", sort='-x', title=col1)
        )
        
        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points
        
        # Return both plots
        return multi_box, confint_plot, numeric_col, non_numeric_col


def display_numeric_categorical_plots(df, numeric_col, non_numeric_col, multi_box, confint_plot):
    """
    Display the boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.

    @param df: A pandas DataFrame object.
    @param numeric_col: The name of the numeric column.
    @param non_numeric_col: The name of the categorical column.
    @param multi_box: Altair boxplot grouped by category (Chart type).
    @param confint_plot: Altair chart showing mean with confidence interval bars (Chart type).
    """
    # Display the boxplot
    st.subheader("Boxplots")
    st.altair_chart(multi_box, use_container_width=True)
    # Display the confidence interval plot
    st.subheader("Confidence Intervals")
    st.altair_chart(confint_plot, use_container_width=True)


def categorical_categorical_plots(df, col1, col2):
    """
    Create a crosstab with raw counts and percentages for two categorical variables 
    if two categorical variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first categorical column (string).
    @param col2: The name of the second categorical column (string).
    @return: Frequency table, format dictionary, Altair heatmap, stacked bar chart, and 100% stacked bar chart.
    """
    # Define the plotting source
    source = df[[col1, col2]].dropna()

    # Crosstab with raw counts
    freq_table = pd.crosstab(source[col1], source[col2])

    # Turn to percentages aggregated by col1
    freq_table = freq_table.div(freq_table.sum(axis=1), axis=0) * 100

    # Table formatting
    freq_table.index.name = col1
    freq_table.columns.name = col2
    freq_table = freq_table.reset_index()
    freq_table = freq_table.rename_axis(None, axis=1)

    # Format percentage columns to only one decimal place
    format_dict = {col: "{:.1f}%" for col in freq_table.columns if pd.api.types.is_numeric_dtype(freq_table[col])}

    # HEATMAP
    heat_title = alt.TitleParams(f"Heatmap Table of {col1} and {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    heatmap = alt.Chart(source, title=heat_title).mark_rect().encode(
        x=f'{col2}:O',
        y=f'{col1}:O',
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange')),
        tooltip=[f'{col1}:O', f'{col2}:O', 'count():Q']
    )
        
    # STACKED BAR CHARTS
    stacked_title = alt.TitleParams(f"Stacked Bar Chart of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    stacked_bar = alt.Chart(source, title=stacked_title).mark_bar().encode(
        y=alt.Y(f"{col1}:N", title=col1),
        x=alt.X('count():Q', title='Count'),
        color=alt.Color(f"{col2}:N", title=col2),
        tooltip=[f"{col1}:O", f"{col2}:O", 'count():Q']
    )
    
    # Putting the frequecy table into a long format for plotting in the 100% stacked bar chart
    stacked_df_100 = freq_table.melt(id_vars=col1, var_name='Category', value_name='Percentage')

    # Altair 100% horizontal stacked bar chart
    stacked_100_title = alt.TitleParams(f"Percentage Distribution of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    stacked_bar_100_pct = alt.Chart(stacked_df_100, title=stacked_100_title).mark_bar().encode(
        y=alt.Y(f'{col1}:O', title=None),
        x=alt.X('Percentage:Q', stack='normalize', title=f'{col2} Distribution'),
        color=alt.Color('Category:N'),
        tooltip=[alt.Tooltip(col1), alt.Tooltip('Category'), alt.Tooltip('Percentage:Q')]
    )

    # Return all tables and plots
    return freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct


def display_categorical_categorical_plots(df, col1, col2, freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct):
    """
    Display the crosstab, heatmap, and stacked bar charts 
    if two categorical variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first categorical column.
    @param col2: The name of the second categorical column.
    @param freq_table: Crosstab table showing frequency counts (DataFrame or displayable object).
    @param format_dict: A dictionary used to format the frequency table display.
    @param heatmap: Altair heatmap of joint frequencies (Chart type).
    @param stacked_bar: Altair stacked bar chart showing counts (Chart type).
    @param stacked_bar_100_pct: Altair 100% stacked bar chart showing proportions (Chart type).
    """
    
    # If the number of unique values of the two columns are reasonable for plotting
    if ((df[col1].nunique() > 2 and df[col2].nunique() > 2) and 
        (df[col1].nunique() <= 12 and df[col2].nunique() <= 12)):
        column1, column2 = st.columns(2)
        # Display the frequency table
        with column1:
            st.subheader(f"Frequency Table of {col1} and {col2}")
            st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)
        # Display the heatmap
        with column2:
            st.altair_chart(heatmap, use_container_width=True)
    
    # If the number of unique values is NOT reasonable for plotting
    else:
        # Just display the frequency table
        st.subheader(f"Frequency Table of {col1} and {col2}")
        st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)

    # Display the stacked bar chart
    st.altair_chart(stacked_bar, use_container_width=True)
    # Display the 100% stacked bar chart next to the other chart
    st.altair_chart(stacked_bar_100_pct, use_container_width=True)


def two_column_plot(df, col1, col2):
    """
    Create a series of two-variable plots based on the data types of each selected column.

    @param df: A pandas DataFrame object.
    @param col1: The first column to plot.
    @param col2: The second column to plot.
    @return: Respective combination of plots based on datatypes.
    """
    # Create a copy of the original dataset
    df = df.copy()
    # Define boolean variables as "object" type for plotting purposes
    df[df.select_dtypes(include='bool').columns] = df.select_dtypes(include='bool').astype('object')
    
    # Define the data types of both selected columns
    col1_type = get_column_type(df, col1)
    col2_type = get_column_type(df, col2)

    # If the selected columns are the same, no plots will be generated
    if col1 == col2:
        st.warning("Please select two different columns to visualize.")
        return None

    # If two NUMERIC variables are selected
    if pd.api.types.is_numeric_dtype(col1_type) and pd.api.types.is_numeric_dtype(col2_type): 
        # Define all the needed plots
        scatterplot, scatterplot_with_lines, resid_plot, heatmap = numeric_numeric_plots(df, col1, col2)
        # Display all plots
        display_numeric_numeric_plots(df, col1, col2, scatterplot, scatterplot_with_lines, resid_plot, heatmap)
        # Return all plots
        return scatterplot, scatterplot_with_lines, heatmap

    # If NUMERIC and CATEGORICAL variables are selected
    elif ((col1_type in ['int64', 'float64'] and (col2_type == 'object' or col2_type.name == 'category')) 
    or ((col1_type == 'object' or col1_type.name == 'category') and col2_type in ['int64', 'float64'])):

        # Create the boxplot and confidence interval plots
        multi_box, confint_plot, numeric_col, non_numeric_col = numeric_categorical_plots(df, col1, col2)
        # Display the plots
        display_numeric_categorical_plots(df, numeric_col, non_numeric_col, multi_box, confint_plot)
        # Return the plots
        return multi_box, confint_plot
        
    # If two CATEGORICAL variables are selected
    elif ((col1_type in ['object', 'bool'] or col1_type.name == 'category') and 
      (col2_type in ['object', 'bool'] or col2_type.name == 'category')):
        
        # Create the crosstab and heatmap
        freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct = categorical_categorical_plots(df, col1, col2)
        # Display the plots
        display_categorical_categorical_plots(df, col1, col2, freq_table=freq_table, format_dict=format_dict, 
                                               heatmap=heatmap, stacked_bar=stacked_bar, 
                                               stacked_bar_100_pct=stacked_bar_100_pct)
        # Return the plots
        return freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct

    # If combination of datatypes are not recognized
    else:
        st.write(f"Cannot visualize {col1} and {col2} together YET")
        return None


def group_by_plot(df, num_op, num_var, grp_by):
    """
    Groups data by a categorical variable and summarizes a numeric variable using a selected operation.
    Displays a corresponding bar chart and summary table.

    @param df: A pandas DataFrame object.
    @param num_op: The aggregation operation to apply ("Total", "Average", "Median", "Count", "Unique Count", or "Standard Deviation").
    @param num_var: The name of the numeric column to aggregate.
    @param grp_by: The name of the categorical column to group by.
    @return: A tuple containing the grouped DataFrame and the Altair bar chart.
    """
    # Create a new simple DataFrame with the two columns of interest
    df_simple = df[[grp_by, num_var]]

    # Group by the "grp_by" variable using the SELECTED OPERATION
    if num_op == "Total":
        df_grouped = df_simple.groupby(by = [grp_by]).sum()
        prefix = "Total "
    elif num_op == "Average":
        df_grouped = df_simple.groupby(by = [grp_by]).mean()
        prefix = "Average "
    elif num_op == "Median":
        df_grouped = df_simple.groupby(by = [grp_by]).median()
        prefix = "Median "
    elif num_op == "Count":
        df_grouped = df_simple.groupby(by = [grp_by]).count()
        prefix = "Count of "
    elif num_op == "Unique Count":
        df_grouped = df_simple.groupby(by = [grp_by]).nunique()
        prefix = "Unique Count of "
    elif num_op == "Standard Deviation":
        df_grouped = df_simple.groupby(by = [grp_by]).std()
        prefix = "Standard Deviation of "

    # Reset the DataFrame index for plotting
    df_grouped = df_grouped.reset_index()
    
    # Rename the existing column to reflect the applied operation
    num_var_name = f"{prefix}{num_var}"
    df_grouped.rename(columns={num_var: num_var_name}, inplace=True)

    # Use a select box to sort the plot (Defualt, Ascending, or Descending)
    sort_option = st.selectbox(
        label = "Select a sort option",
        options=["None", "Ascending", "Descending"],
        index=0,
        key=f"{num_op}_{num_var}_{grp_by}"
    )
    
    # Change the sort variable based on the sorting selection
    if sort_option == "Ascending":
        sort = 'y'
    elif sort_option == "Descending":
        sort = '-y' 
    else:
        sort = list(df_grouped[grp_by])
    
    # BAR CHART
    grouped_chart = alt.Chart(df_grouped, title=f"{num_var_name} by {grp_by}").mark_bar().encode(
        x=alt.X(f'{grp_by}:N', sort=sort),
        y=alt.Y(f'{num_var_name}:Q')
    )

    # Display the plot
    st.altair_chart(grouped_chart, use_container_width=True)

    # Display the summarized table
    st.subheader("Summarized Table")
    st.dataframe(df_grouped)

    # Return the aggregated DataFrame and the corresponsing bar chart
    return df_grouped, grouped_chart


def sort_select():
    # Use a select box to sort the plot (Defualt, Ascending, or Descending)
    c1, _, _ = st.columns(3)
    
    sort_option = c1.selectbox(
        label = "Sort option",
        options=["None", "Ascending", "Descending"],
        index=0)
    
    # Change the sort variable based on the sorting selection
    if sort_option == "Ascending":
        sort = 'y'
    elif sort_option == "Descending":
        sort = '-y'
    else:
        sort = None

    return sort 


def plot_container(df, altiar_chart):
    """
    Display a tabbed container housing a chart and a table with an Excel/csv download option.
    """
    import io
    from datetime import datetime
    # Create a tabbed container 
    with st.container():
        tab1, tab2 = st.tabs(["Visualize", "Table"])

        with tab1:
            # Display the Altair chart
            st.altair_chart(altiar_chart, use_container_width=True)
        with tab2:
            # Display the DataFrame table
            st.dataframe(df, hide_index=True, use_container_width=True)

            # Excel download option
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            
            c1, c2, _ = st.columns([1, 1, 12])
            
            # Download Buttons
            c1.download_button(
                label="Excel",
                data=(lambda buf=io.BytesIO(): (df.to_excel(buf, index=False, engine="openpyxl"), buf.seek(0), buf)[2])(),
                file_name=f"table_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_excel_{timestamp}")
            
            c2.download_button(
                label="CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name=f"table_{timestamp}.csv",
                key=f"download_csv_{timestamp}"
            )
                
