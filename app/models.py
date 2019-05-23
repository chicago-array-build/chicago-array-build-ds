from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint

DB = SQLAlchemy()


class Node(DB.Model):
    node_id = DB.Column(DB.String(100), primary_key=True)
    vsn = DB.Column(DB.String(100))
    lat = DB.Column(DB.Float)
    lon = DB.Column(DB.Float)
    community_area = DB.Column(DB.String(100))

    def __repr__(self):
        return f'<Node: {self.node_id}>'


class Sensor(DB.Model):
    sensor_path = DB.Column(DB.String(100), primary_key=True)
    sensor_type = DB.Column(DB.String(100)) # Environmental, .etc
    sensor_measure = DB.Column(DB.String(100)) # Temperature, .etc
    hrf_unit = DB.Column(DB.String(100))
    hrf_minval = DB.Column(DB.Float)
    hrf_maxval = DB.Column(DB.Float)

    def __repr__(self):
        return f'<Sensor: {self.sensor_path}>'


class Observation(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    timestamp = DB.Column(DB.DateTime)
    node_id = DB.Column(
        DB.String(100), DB.ForeignKey('node.node_id'), nullable=False)
    sensor_path = DB.Column(
        DB.String(100), DB.ForeignKey('sensor.sensor_path'), nullable=False)
    value_hrf = DB.Column(DB.String(100))

    def __repr__(self):
        return f'<Observation: {self.id}>'