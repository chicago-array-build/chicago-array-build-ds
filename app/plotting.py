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
    plot_url = py.plot(fig, filename='Multiple Mapbox', auto_open=False)

    return plot_url


def make_line_plot(df):
    pass


def make_houlry_bar_plot(df):
    pass
