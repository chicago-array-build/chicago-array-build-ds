import os
import pandas as pd
from pathlib import Path

import dash
from flask import Flask, jsonify, request

from .config import Config
from .models import DB


def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    DB.init_app(app)
    register_dashapp(app)

    @app.shell_context_processor
    def make_shell_context():
        return {'DB': DB}

    @app.route('/')
    def root():
        return jsonify(message='Nothing here')

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return redirect(url_for('root'))

    @app.route('/plot', methods=['GET'])
    def predict():
        # gather parameters
        user_id = request.args.get('sensor_type')

        # verify minimum parameters
        if not user_id:
            return jsonify(
                message="Error: must pass user_id, e.g. /predict?user_id=1")

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
