import re
from pathlib import Path

import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).parents[1] / 'data'


def load_uci():
    """Load data from http://archive.ics.uci.edu/ml/datasets/diabetes"""
    data_path = str(DATA_DIR / 'public' / 'uci')
    dfs = []
    for p in Path(data_path).iterdir():
        match = re.search(r'\d\d$', str(p))
        if match:
            df = pd.read_csv(
                p,
                sep='\t',
                header=None,
                names=['Date', 'Time', 'Code', 'Value'])
            df['person_id'] = int(match[0])
            dfs.append(df)
    df = pd.concat(dfs)

    code_map = {
        33: 'Regular insulin dose',
        34: 'NPH insulin dose',
        35: 'UltraLente insulin dose',
        48: 'Unspecified blood glucose measurement',
        57: 'Unspecified blood glucose measurement',
        58: 'Pre-breakfast blood glucose measurement',
        59: 'Post-breakfast blood glucose measurement',
        60: 'Pre-lunch blood glucose measurement',
        61: 'Post-lunch blood glucose measurement',
        62: 'Pre-supper blood glucose measurement',
        63: 'Post-supper blood glucose measurement',
        64: 'Pre-snack blood glucose measurement',
        65: 'Hypoglycemic symptoms',
        66: 'Typical meal ingestion',
        67: 'More-than-usual meal ingestion',
        68: 'Less-than-usual meal ingestion',
        69: 'Typical exercise activity',
        70: 'More-than-usual exercise activity',
        71: 'Less-than-usual exercise activity',
        72: 'Unspecified special event',
    }

    df['code_cat'] = df['Code'].map(code_map)

    df['date_time'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format="%m-%d-%Y %H:%M",
        errors='coerce')

    df = df.drop(columns=['Date', 'Time'])

    print(f"{sum(df['date_time'].isna())} records failed to convert to date")
    df = df.loc[~df['date_time'].isna()]

    # drop entries entered at 8AM, 12AM, 4PM, 10PM
    mask = (df['date_time'].dt.hour.isin([8, 12, 18, 22]) &
            (df['date_time'].dt.minute == 0))
    df = df.loc[~mask]

    return df


def load_tidepool_dummy():
    """Assumed fake data from https://github.com/tidepool-org
    Could be a useful data structure to emulate"""
    data_path = ('https://raw.githubusercontent.com/tidepool-org/'
                 'data-analytics/master/examples/example-data/'
                 'example-from-j-jellyfish.csv')

    return pd.read_csv(data_path)


def load_so_pump_raw():
    data_path = str(DATA_DIR / 'private' / 'omnipod_pump' /
                    'omnipod_export_2019-04-13.TAB')
    df = pd.read_csv(data_path, sep='\t', encoding='latin1')

    cols = [
        'DATEEVENT', 'TIMESLOT', 'EVENTTYPE', 'VENDOR_EVENT_ID', 'KEY0',
        'KEY1', 'KEY2', 'I0', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7', 'I8',
        'I9', 'D0', 'D1', 'D2', 'D3', 'D4', 'C0', 'C1', 'C2', 'COMMENT'
    ]
    df = df[cols]

    df['DATEEVENT'] = pd.to_datetime(
        pd.to_numeric(df['DATEEVENT']) - 2, origin='1900-01-01',
        unit="D").dt.round('s')

    return df.sort_values('DATEEVENT').reset_index(drop=True)


def load_so_pump():
    """Data pulled by copy & paste from Abbott desktop app"""
    data_path = str(DATA_DIR / 'private' / 'omnipod_pump' /
                    'omnipod_export_2019-04-13.csv')
    df = pd.read_csv(data_path)

    df.loc[df['Time'].isna(), 'Time'] = '12:00 AM'
    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df = df.drop(columns=['Date', 'Time'])

    df[['Value', 'Unit',
        '_']] = (df['Value'].str.replace(r'\(|\)', '').str.split(
            ' ', expand=True))
    df = df.drop(columns=['_'])
    df['Value'] = pd.to_numeric(df['Value'])

    cols = [
        'Datetime', 'Type', 'Value', 'Unit', 'Description', 'Other Info',
        'Comment'
    ]
    df = df[cols]

    # drop daily summaries and pump alarms
    df = df.loc[~df['Type'].isin(['Insulin Summary', 'Pump Alarm'])]

    # fix NaN values for bolus
    mask = (df['Value'].isna() &
            df['Description'].str.lower().str.contains('bolus') == True)
    df.loc[mask, 'Type'] = 'Bolus Insulin'
    df.loc[mask, 'Value'] = (
        df.loc[mask, 'Description'].str.extract(r'([0-9].[0-9][0-9])')[0])

    # fix NaN values for basal
    mask = (df['Value'].isna() &
            ((df['Description'].str.lower().str.contains('basal rate set to')
              ) == True))
    df.loc[mask, 'Type'] = 'Basal Insulin'
    df.loc[mask, 'Value'] = (
        df.loc[mask, 'Description'].str.extract(r'([0-9].[0-9][0-9])')[0])

    df.loc[:, 'Value'] = pd.to_numeric(df['Value'])

    # assign bolus to 1 minute duration
    df.loc[df['Type'] == 'Bolus Insulin', 'dur_mins'] = 1

    # create type: extended bolus insulin
    mask = df['Description'].str.contains('Extended General Bolus') == True
    df.loc[mask, 'Type'] = 'Extended Bolus Insulin'
    df.loc[mask, 'dur_mins'] = (df.loc[mask, 'Description'].str.extract(
        r'([0-9]+ minutes)')[0].str.strip(' minutes').astype(int))

    # remove unused rows and cols
    keep_types = ['Bolus Insulin', 'Basal Insulin', 'Extended Bolus Insulin']
    df = df.loc[df['Type'].isin(keep_types)]
    cols = ['Datetime', 'Type', 'Value', 'dur_mins']
    df = df[cols].sort_values('Datetime')

    # convert basal rates to total insulin administered over a total duration
    # (just like Extended Bolus Insulin)
    mask = (df['Type'] == 'Basal Insulin')
    df.loc[mask, 'until'] = df.loc[mask, 'Datetime'].shift(-1)
    # set most recent basal end time to most recent data in entire DataFrame
    df.loc[mask, 'until'] = df.loc[mask, 'until'].fillna(df['Datetime'].max())

    df.loc[mask, 'dur_mins'] = (df.loc[mask, 'until'].subtract(
        df.loc[mask, 'Datetime']).dt.seconds.divide(60))
    df.loc[mask, 'Value'] = (df.loc[mask, 'Value'].divide(60).multiply(
        df.loc[mask, 'dur_mins']))
    df = df.drop(columns=['until'])
    df = df.loc[df['dur_mins'] > 0]

    df = expand_rows_to_minute_interval(
        df.copy(), row_type='Extended Bolus Insulin')
    df = expand_rows_to_minute_interval(df.copy(), row_type='Basal Insulin')

    df = df.sort_values('Datetime')

    return df


def expand_rows_to_minute_interval(df, row_type):
    expand_dfs = []
    for idx, row in df.loc[df['Type'] == row_type].iterrows():
        expand_df = pd.DataFrame([row] * int(row['dur_mins']))
        expand_df['Datetime'] = pd.date_range(
            start=row['Datetime'], periods=int(row['dur_mins']), freq='min')
        expand_df['Value'] = row['Value'] / row['dur_mins']
        expand_df['dur_mins'] = 1
        expand_dfs.append(expand_df)

    # replace original rows with expanded versions
    df = df.loc[df['Type'] != row_type]
    df = df.append(expand_dfs, ignore_index=True)

    return df


def load_so_cgm(raw=False):
    data_path = str(DATA_DIR / 'private' / 'dexcom_cgm')

    dfs = []
    for p in Path(data_path).iterdir():
        if str(p).endswith('.csv'):
            df = pd.read_csv(p)

            date_nans = df['Timestamp (YYYY-MM-DDThh:mm:ss)'].isna()
            n_date_nans = sum(date_nans)
            if n_date_nans > 9:
                raise Exception(f'More NaN Timestamp values than expected. '
                                f'Expected <= 9, found {n_date_nans}')
            df = df.loc[~date_nans]

            dfs.append(df)

    df = pd.concat(dfs)
    df['Timestamp (YYYY-MM-DDThh:mm:ss)'] = pd.to_datetime(
        df['Timestamp (YYYY-MM-DDThh:mm:ss)'])
    df = df.sort_values('Timestamp (YYYY-MM-DDThh:mm:ss)')

    if raw:
        return df.reset_index(drop=True)
    
    df['Timestamp (YYYY-MM-DDThh:mm:ss)'] = (
        df['Timestamp (YYYY-MM-DDThh:mm:ss)'].astype(np.int64) // 10**9
    )
    df = df[df['Event Type'] == 'EGV']
    df['below_threshold'] = False
    df.loc[df['Glucose Value (mg/dL)'] == 'Low', 'below_threshold'] = True
    df.loc[df['below_threshold'], 'Glucose Value (mg/dL)'] = 39
    df['Glucose Value (mg/dL)'] = df['Glucose Value (mg/dL)'].astype(int)

    rename_dict = {
        'Timestamp (YYYY-MM-DDThh:mm:ss)': 'timestamp',
        'Glucose Value (mg/dL)': 'value',
    }
    df = df.rename(columns=rename_dict).reset_index(drop=True)

    # combine timestamp duplicates (TODO: review these)
    df = df.groupby('timestamp').mean().reset_index()
    df['below_threshold'] = df['below_threshold'].round().astype(int)

    return df[list(rename_dict.values()) + ['below_threshold']]
