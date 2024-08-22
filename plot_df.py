from datetime import datetime
import pandas as pd
import numpy as np
from plotly import graph_objs as go
from plotly import express as px
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
import shap
import matplotlib.pyplot as plt

def plot_beeswarm(shap_values):
    # Step 5: Plot SHAP values
    shap.plots.beeswarm(shap_values)
    plt.gcf()
    plt.show()


def plot_cv_results(cv_results):
    sns.boxplot(cv_results.T)
    plt.show()


def plot_graph(total_pred):
    # Create the plot
    trace_list = []
    col_to_plot = list(total_pred.columns)
    col_to_plot.remove('std')

    for i in col_to_plot:
        trace_list.append(go.Scatter(
            x=total_pred.index,
            y=total_pred[i],
            mode='lines+markers',
            name=i
        ))

    # Create the plot
    # trace_actual = go.Scatter(
    #     x=total_pred.index,
    #     y=total_pred['count'],
    #     mode='lines+markers',
    #     name='Actuals'
    # )

    trace_upper_bound = go.Scatter(
        x=total_pred.index,
        y=total_pred['mean'] + total_pred['std'],
        mode='lines',
        name='Prediction + Std Dev',
        line=dict(width=0),  # Hide the line itself
        showlegend=False
    )

    trace_lower_bound = go.Scatter(
        x=total_pred.index,
        y=total_pred['mean'] - total_pred['std'],
        mode='lines',
        fill='tonexty',  # Fill the area between this trace and the previous trace
        name='Prediction - Std Dev',
        fillcolor='rgba(68, 68, 68, 0.3)',  # Adjust the fill color and opacity
        line=dict(width=0),  # Hide the line itself
        showlegend=False
    )

    trace_list.extend([trace_upper_bound, trace_lower_bound])

    # Create the layout

    layout = go.Layout(
        title='Prediction and Standard Deviation',
        xaxis={'title': 'Index'},
        yaxis={'title': 'Values'},
        hovermode='closest'
    )

    fig = go.Figure(data=trace_list, layout=layout)

    fig.show()
