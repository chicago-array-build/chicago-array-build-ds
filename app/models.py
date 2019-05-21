"""SQLAlchemy models and utility functions.

Schema: https://dbdiagram.io/d/5ce41f0e1f6a891a6a6564ae
"""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

class Observation(DB.Model):
    timestamp_utc = 
    node_id = # Foreign Key
    sensor_path = # Foreign Key
    value_hrf = 

    # multi-column primary key
    __table_args__ = (
        UniqueConstraint('timestamp_utc', 'node_id', 'sensor_path', name='id'),
    )

    def __repr__(self):
        return f'<Observation: {self.id}>'

class Sensor(DB.Model):
    sensor_path = # Primary Key
    node_id = 
    sensor_type = 
    hrf_unit = 
    hrf_minval = 
    hrf_maxval = 

    def __repr__(self):
        return f'<Sensor: {self.sensor_path}>'

class Node(DB.Model):
    node_id = # Primary Key
    lat = 
    lon = 
    community_area = 

    def __repr__(self):
        return f'<Node: {self.node_id}>'
