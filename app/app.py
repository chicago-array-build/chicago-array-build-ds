import os
import pandas as pd
from pathlib import Path

import dash
from flask import Flask, jsonify, request
from sqlalchemy import func

from .config import Config
from .models import DB, Observation
from .aot import load_aot_archive_day, clean_aot_archive_obs


def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    DB.init_app(app)
    register_dashapp(app)

    @app.shell_context_processor
    def make_shell_context():
        return {'DB': DB, 'Observation': Observation}

    @app.route('/')
    def root():
        return jsonify(message='Nothing here')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return redirect(url_for('root'))

    @app.route('/update')
    def update():
        """Update database"""
        date = request.args.get('date')
        if not date:
            return jsonify(
                message="Error: must supply date as 'YYYY-MM-DD'")

        df = load_aot_archive_day(date)
        df = clean_aot_archive_obs(df)
        max_id = DB.session.query(func.max(Observation.id)).scalar()

        if not max_id:
            max_id = 0

        df['id'] = list(range(max_id + 1, max_id + len(df) + 1))

        df.to_sql(
            'observation', con=DB.engine, if_exists='append', index=False
        )

        return jsonify(
                message=f"Success: added {date}")
    

    @app.route('/plot', methods=['GET'])
    def predict():
        # TODO
        # gather parameters
        sensor_type = request.args.get('sensor_type')

        # verify minimum parameters
        if not sensor_type:
            return jsonify(
                message="Error: ")

        # generate plot, return plot URL
        
        return jsonify(
            message="success",
            plot_url="",
        )

    return app


def register_dashapp(app):
    from app.dashapp.layout import layout
    from app.dashapp.callbacks import register_callbacks

    external_stylesheets = ['https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css']

    app_dash = dash.Dash(
        __name__,
        server=app,
        routes_pathname_prefix='/dash/',
        external_stylesheets=external_stylesheets
    )

    app_dash.title = 'Chicago AoT Dashboard'
    app_dash.layout = layout
    register_callbacks(app_dash)
