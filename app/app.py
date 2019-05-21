import os
import pandas as pd
from pathlib import Path

from flask import Flask, jsonify, request

from .config import Config
from .models import DB


def create_app():
    """Create and configure and instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.shell_context_processor
    def make_shell_context():
        return {'DB': DB}

    @app.route('/')
    def root():
        return jsonify(message='Nothing here')

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
            user_id=int(user_id),
            records=df.to_dict('records'),
        )

    return app
