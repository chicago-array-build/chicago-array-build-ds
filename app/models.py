"""SQLAlchemy models and utility functions."""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class Observation(DB.Model):
    # sensor_id = DB.Column(DB.String(15))
    # name = DB.Column(DB.String(15), nullable=False)

    def __repr__(self):
        return f'<AoT Record {self.name}>'
