import datetime
import os
from pathlib import Path

import dash
import pandas as pd
from flask import Flask, jsonify, request
from sqlalchemy import func, text

from .aot_archive import (initialize_nodes, initialize_sensors, 
                          upload_aot_archive_date)
from .config import Config
from .models import DB, Observation
from .plotting import (make_hourly_bar_plot, make_line_plot, make_map,
                       plotly_setup)


def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    DB.init_app(app)
    plotly_setup()
    register_dashapp(app)
    
    @app.shell_context_processor
    def make_shell_context():
        return {'DB': DB, 'Observation': Observation}

    @app.route('/')
    def root():
        return jsonify(message='Nothing here')

    @app.route('/initialize')
    def initialize():
        initialize_nodes()
        initialize_sensors()

        return jsonify(message='Message: added nodes and sensors')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()

        return jsonify(message='Success: reset database')

    @app.route('/update')
    def update():
        """Update database"""
        date = request.args.get('date')
        if not date:
            return jsonify(
                message="Error: must supply date as 'YYYY-MM-DD'")

        upload_aot_archive_date(date)

        return jsonify(
            message=f"Success: added {date}")
    

    @app.route('/plot', methods=['GET'])
    def predict():
        sensor_type = request.args.get('sensor_type')
        measure = request.args.get('measure')
        print(sensor_type, measure)

        if not all([sensor_type, measure]):
            return jsonify(
                message="Error: must supply sensor_type and measure arguments")

        # TODO: time could be a variable
        t = (datetime.datetime.now() - 
             datetime.timedelta(days=7))
        t = t.strftime(r'%m/%d/%Y')

        sql = text(
            "SELECT observation.*, node.lat, node.lon\n"
            "FROM observation\n"
            "INNER JOIN node\n"
            "ON observation.node_id = node.node_id\n"
            "LEFT JOIN sensor\n"
            "ON observation.sensor_path = sensor.sensor_path\n"
            "WHERE (\n"
            f"    timestamp >= '{t}' AND\n"
            f"    sensor_type = '{sensor_type}' AND\n"
            f"    sensor_measure = '{measure}'\n"
            ")"
        )
        result = DB.engine.execute(sql)
        cols = result.keys()
        result = result.fetchall()

        df = pd.DataFrame(columns=cols, data=result)
        df['value_hrf'] = pd.to_numeric(df['value_hrf'])

        map_url = make_map(df)
        raw_url = make_line_plot(df, measure)
        hourly_url = make_hourly_bar_plot(df, measure)

        return  jsonify(
            message="Success",
            map_url=map_url,
            raw_url=raw_url,
            hourly_url=hourly_url,
        )

    return app


def register_dashapp(app):
    from app.dashapp.layout import layout
    from app.dashapp.callbacks import register_callbacks

    external_stylesheets = [('https://stackpath.bootstrapcdn.com/'
                             'bootstrap/4.3.1/css/bootstrap.min.css')]

    app_dash = dash.Dash(
        __name__,
        server=app,
        routes_pathname_prefix='/dashboard/',
        external_stylesheets=external_stylesheets
    )

    app_dash.title = 'Chicago AoT Dashboard'
    app_dash.layout = layout
    register_callbacks(app_dash)
