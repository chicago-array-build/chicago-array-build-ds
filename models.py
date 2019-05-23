
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint


DB = SQLAlchemy()

"""
Schema: https://dbdiagram.io/d/5ce41f0e1f6a891a6a6564ae
Useful Documentation: https://docs.sqlalchemy.org/en/13/orm/tutorial.html
"""

class Node(DB.Model):
    node_id =  DB.Column(DB.String(100), primary_key=True)
    lat = DB.Column(DB.BigInteger)
    lon = DB.Column(DB.BigInteger)
    community_area = DB.Column(DB.String(100))
    description = DB.Column(DB.String(1000))
    def __repr__(self):
        return f'<Node: {self.node_id}>'


class Sensor(DB.Model):
    sensor_path = DB.Column(DB.String(100), primary_key=True)
    node_id = DB.Relationship('Node', backref=DB.backref('sensors', lazy=True))
    sensor_type = DB.Column(DB.String(100))
    hrf_unit = DB.Column(DB.String(100))
    hrf_minval = DB.Column(DB.BigInteger())
    hrf_maxval = DB.Column(DB.BigInteger())
    def __repr__(self):
        return f'<Sensor: {self.sensor_path}>'


class Observation(DB.Model):
    timestamp_utc = DB.Column(DB.BigInteger(100))
    node_id = DB.Relationship('Node', backref=DB.backref('sensors', lazy=True))
    sensor_path = DB.Relationship('Sensor', backref=DB.backref('observations', lazy=True))
    value_hrf = DB.Column(DB.String(100))

    # multi-column primary key
    __table_args__ = (
        UniqueConstraint('timestamp_utc', 'node_id', 'sensor_path', name='id'),
    )

    def __repr__(self):
        return f'<Observation: {self.id}>'
