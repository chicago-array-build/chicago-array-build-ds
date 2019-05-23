
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_sensors(): #  Returns a DataFrame with information on sensors. 
    '''
    Returns a DataFrame with information on sensors. 
    Current columns = 
                    ['ontology', 'subsystem', 'sensor', 'parameter', 'hrf_unit',
                     'hrf_minval', 'hrf_maxval', 'datasheet']
    '''
    r = requests.get('https://aot-file-browser.plenar.io/data-sets/chicago-complete')
    soup = BeautifulSoup(r.text, 'lxml')
    sensors = pd.read_html(str(soup.findAll(class_='table')[3]))[0]

    sensors['sensor_path'] = (
        sensors.subsystem + '.' + 
        sensors.sensor + '.' + 
        sensors.parameter)
    
    return sensors

def initialize_sensors():
    
    df1 = get_sensors()
    # this path needs to be updated.
    df2 = pd.read_csv('Downloads/sensor_mapping.csv')[['sensor_measure', 'sensor_path', 'sensor_type']]
    
    df3 = pd.merge(df1, df2.dropna(subset=['sensor_measure']), on='sensor_path')
    
    df3 = df3[['sensor_path', 'sensor_type', 'sensor_measure', 'hrf_unit', 'hrf_minval', 'hrf_maxval']]
    
    df3.to_sql(
        'sensor', con=DB.engine, if_exists='append', index=False
    )


def initialize_nodes(): # Returns a DataFrame with information on nodes. 
    '''
    Returns a DataFrame with information on nodes. 
    Current columns = 
                    ['node_id', 'project_id', 'vsn', 'address', 'lat', 'lon', 'description',
                    'start_timestamp', 'end_timestamp', 'Unnamed: 9']
    '''
    r = requests.get('https://aot-file-browser.plenar.io/data-sets/chicago-complete')
    soup = BeautifulSoup(r.text, 'lxml')
    nodes = pd.read_html(str(soup.findAll(class_='table')[2]))[0]
    
    nodes.to_sql(
        'nodes', con=DB.engine, if_exists='append', index=False
    )

