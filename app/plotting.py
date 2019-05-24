from os import getenv

import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.plotly as py


def plotly_setup():
    plotly.tools.set_credentials_file(
        username=getenv('PLOTLY_USER'), 
        api_key=getenv('PLOTLY_API_KEY')
    )


def make_map(df):
    df = df.copy()
    df = df.drop_duplicates(['lat', 'lon'])

    mapbox_access_token = getenv('MAPBOX_API_KEY')

    data = [
        go.Scattermapbox(
            lat=df['lat'],
            lon=df['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=9
            ),
        )
    ]

    layout = go.Layout(
        title='Node Locations',
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=41.8753,
                lon=-87.6459
            ),
            pitch=30,
            zoom=10
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    plot_url = py.plot(fig, auto_open=False)

    return plot_url


def make_line_plot(df, measure):
    df = df.copy()

    data = []
    for g_name, g_df in df.groupby('node_id'):
        data.append(
            go.Scatter(
                x=g_df['timestamp'],
                y=g_df['value_hrf'],
                mode = 'lines+markers',
            )
        )

    layout = dict(
        title = f'{measure} Readings Over Time',
        xaxis = dict(title = 'Time'),
        yaxis = dict(title = f'{measure} Reading'),
    )

    fig = dict(data=data, layout=layout)

    plot_url = py.plot(fig, auto_open=False)

    return plot_url


def make_hourly_bar_plot(df, measure):
    df = df.copy()

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.groupby(df['timestamp'].dt.hour)['value_hrf'].mean()

    data = [go.Bar(
        x=df.index,
        y=df.values,
    )]

    layout = dict(
        title = f'{measure} Readings Averaged by Hour',
        xaxis = dict(title = 'Hour'),
        yaxis = dict(title = f'{measure} Reading'),
    )

    fig = go.Figure(data=data, layout=layout)

    plot_url = py.plot(fig, auto_open=False)

    return plot_url

