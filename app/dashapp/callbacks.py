import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from ..aot import SENSOR_DF, query_aot


def register_callbacks(app):
    @app.callback(Output('raw-value-graph', 'figure'), 
                  [Input('select-sensor-meas', 'value')])
    def update_figure(selected_value):
        print(selected_value)
        df = query_aot(sensor_hrf=selected_value)
        traces = []
        for g_i, g_df in df.groupby('node_vsn'):
            data = (pd.Series(g_df['value'], index=g_df['timestamp'])
                      .resample('30min')
                      .mean())
            traces.append(go.Scatter(
                x=list(data.index),
                y=list(data.values),
                text=g_i,
                mode='lines+markers',
                # opacity=0.7,
                # marker={
                #     'size': 15,
                #     'line': {'width': 0.5, 'color': 'white'}
                # },
                name=g_i
            ))

        return {
            'data': traces,
            'layout': go.Layout(
                title='Raw Data (Last 48 Hours)',
                xaxis={'title': 'Date'},
                yaxis={'title': 'Value'},
            )
        }

    @app.callback(Output('select-sensor-meas', 'options'), 
                  [Input('select-sensor-cat', 'value')])
    def update_dropdown(selected_value):
        d = (SENSOR_DF.groupby('sensor_type')['sensor_measure']
                      .unique()
                      .to_dict())
        return [{'label': i, 'value': i} for i in d[selected_value]]
