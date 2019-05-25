import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from ..aot import SENSOR_DF, query_aot


def register_callbacks(app):
    @app.callback(Output('raw-value-graph', 'figure'), 
                  [Input('select-sensor-meas', 'value')])
    def update_figure(selected_value):
        df = query_aot(sensor_hrf=selected_value, mins_ago=12*60)
        uom = df['uom'].values[0]
        df = df.set_index('timestamp')
        df = (df.groupby('node_vsn')['value']
                .resample('30min')
                .mean()
                .reset_index())


        print(df.head())

        traces = []
        for g_i, g_df in df.groupby('node_vsn'):
            traces.append(go.Scatter(
                x=list(g_df['timestamp']),
                y=list(g_df['value']),
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
                title=f'Raw {selected_value} Data (Last 12 Hours)',
                xaxis={'title': 'Date'},
                yaxis={'title': f'Sensor Reading ({uom})'},
            )
        }

    @app.callback(Output('select-sensor-meas', 'options'), 
                  [Input('select-sensor-cat', 'value')])
    def update_dropdown(selected_value):
        d = (SENSOR_DF.groupby('sensor_type')['sensor_measure']
                      .unique()
                      .to_dict())
        return [{'label': i, 'value': i} for i in d[selected_value]]
