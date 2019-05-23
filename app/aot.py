import datetime
import tarfile
from pathlib import Path

import pandas as pd
import requests
from aot_client import AotClient, F

from bs4 import BeautifulSoup

from .models import DB

SENSOR_DF = pd.read_csv('data/sensor_mapping.csv')


def unpack_response(response, page_limit=1000):
    try:
        pages = []
        for i, page in enumerate(response):
            if i + 1 > page_limit:
                print('Hit page limit.')
                break
            pages.extend(page.data)
    except HTTPError as e:
        print(e)    
    finally:
        return pages


def time_x_mins_ago(minutes:int):
    '''Get formatted time to pass to API filter, relative to current time
    '''
    t = (datetime.datetime.now() - 
         datetime.timedelta(minutes=minutes) + 
         datetime.timedelta(hours=5))  # convert timezone from central to UTC
    t = t.isoformat()
    
    return t[0:19]


def process_observations(obs_df):
    obs_df = obs_df.copy()
    obs_df['timestamp'] = pd.to_datetime(obs_df['timestamp'], utc=True)
    obs_df['timestamp'] = obs_df['timestamp'].dt.tz_convert('US/Central')
    
    # extract lat/lon to columns
    obs_df['coords'] = obs_df['location'].apply(
        lambda x: x['geometry']['coordinates'])
    obs_df[['lon', 'lat']] = pd.DataFrame(
        obs_df['coords'].tolist(), columns=['lon', 'lat'])
    obs_df = obs_df.drop(columns=['coords'])
    
    # fix positive lon values
    mask = obs_df['lon'] > 0
    if sum(mask) > 0:
        print(f'fixed {sum(mask)} rows with positive lon value')
        obs_df.loc[mask, 'lon'] = obs_df.loc[mask, 'lon'] * -1

    # remove lat/lon values at 0
    mask = (obs_df['lon'] != 0) & (obs_df['lat'] != 0)
    if len(obs_df) - sum(mask) > 0:
        print(f'removed {len(obs_df) - sum(mask)} rows with lat/lon at 0')
        obs_df = obs_df.loc[mask]

    # remove lat values less than 40 degrees
    mask = (obs_df['lat'] > 40)
    if len(obs_df) - sum(mask) > 0:
        print(f'removed {len(obs_df) - sum(mask)} '
              'rows with lat/lon outside Chicago region')
        obs_df = obs_df.loc[mask]
    
    return obs_df


def query_aot(sensor_hrf, size_per_page=100000, page_limit=1, mins_ago=12*60):
    sensor = SENSOR_DF.loc[SENSOR_DF['sensor_measure']==sensor_hrf, 
                           'sensor_path'].values[0]

    client = AotClient()

    f = F('size', str(size_per_page))
    f &= ('sensor', sensor)
    f &= ('timestamp', 'ge', time_x_mins_ago(mins_ago))

    response = client.list_observations(filters=f)
    pages = unpack_response(response, page_limit=page_limit)
    obs_df = pd.DataFrame(pages)
    obs_df = process_observations(obs_df)
    
    return obs_df


def load_aot_archive_day(day: str):
    """Pass day as 'YYYY-MM-DD' string"""
    # load tar file from url
    url = f'https://s3.amazonaws.com/aot-tarballs/chicago-complete.daily.{day}.tar'
    r = requests.get(url)
    temp_dir = Path('data/ignore')
    write_path = temp_dir / 'data.tar'

    # write locally - TODO: do this in memory
    with open(write_path, 'wb') as f:  
        f.write(r.content)

    # read the local tar file and extract observations csv
    with tarfile.TarFile(write_path) as t:
        target_file = f'chicago-complete.daily.{day}/data.csv.gz'
        t.extract(target_file, path=temp_dir)

    # load observations csv
    df = pd.read_csv(temp_dir / target_file, compression='gzip')

    # delete local files
    write_path.unlink()
    (temp_dir / target_file).unlink()
    (temp_dir / target_file).parent.rmdir()

    return df


def clean_aot_archive_obs(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # TODO: not sure if in UTC or Central already
    # df['timestamp'] = df['timestamp'].dt.tz_convert('US/Central')

    df['sensor_path'] = df['subsystem'] + '.' + df['sensor'] + '.' + df['parameter']
    df = df[['timestamp', 'node_id', 'sensor_path', 'value_hrf']]

    df['value_hrf'] = pd.to_numeric(df['value_hrf'], errors='coerce')

    df = df.set_index('timestamp')

    df = df.loc[df['value_hrf'].notna()]

    df = (df.groupby(['node_id', 'sensor_path'])
            .resample('30min')
            .mean()
            .reset_index())

    return df


def get_sensors():
    '''
    Returns a DataFrame with information on sensors. 
    '''
    r = requests.get('https://aot-file-browser.plenar.io/'
                     'data-sets/chicago-complete')
    soup = BeautifulSoup(r.text, 'lxml')
    sensors = pd.read_html(str(soup.findAll(class_='table')[3]))[0]

    sensors['sensor_path'] = (
        sensors.subsystem + '.' + 
        sensors.sensor + '.' + 
        sensors.parameter)
    
    return sensors


def initialize_sensors():
    df1 = get_sensors()

    df2 = pd.read_csv('data/sensor_mapping.csv')
    df2 = df2[['sensor_measure', 'sensor_path', 'sensor_type']]

    df3 = pd.merge(df1, df2.dropna(subset=['sensor_measure']), 
                   on='sensor_path')
    
    df3 = df3[['sensor_path', 'sensor_type', 'sensor_measure', 
               'hrf_unit', 'hrf_minval', 'hrf_maxval']]
    
    df3.to_sql(
        'sensor', con=DB.engine, if_exists='append', index=False
    )


def get_nodes():
    '''Returns a DataFrame with information on nodes.'''
    df = pd.read_csv('data/nodes.csv')
    df['vsn'] = df['vsn'].str.zfill(3)
    
    return df


def initialize_nodes():
    nodes = get_nodes()
    
    nodes.to_sql(
        'node', con=DB.engine, if_exists='append', index=False
    )
