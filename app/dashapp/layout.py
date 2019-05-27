import dash_core_components as dcc
import dash_html_components as html


layout = html.Div(children=[
    html.H1(
        children='Chicago Array of Things Dashboard', 
        style={
            'textAlign': 'center'
        }
    ),

    html.H5(
        children="An interactive dashboard to explore our city's data",
        style={
            'textAlign': 'center'
        }
    ),

    dcc.Dropdown(
        id='select-sensor-cat',
        placeholder="Select a Sensor Category",
        options=[
            {'label': 'Environmental', 'value': 'Environmental'},
            {'label': 'Air Quality', 'value': 'Air Quality'},
            {'label': 'Image Processing', 'value': 'Image Processing'}
        ],
        searchable=False,
    ),

    dcc.Dropdown(
        id='select-sensor-meas',
        placeholder="Select a Sensor Measure",
        searchable=False,
    ),

    dcc.Graph(id='raw-value-graph'),

], style={'width': 800})