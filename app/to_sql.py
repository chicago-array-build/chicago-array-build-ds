import tarfile
import pandas as pd

# link is https://s3.amazonaws.com/aot-tarballs/chicago-complete.weekly.2019-04-15-to-2019-04-21.tar
file = 'Downloads/chicago-complete.weekly.2019-04-15-to-2019-04-21.tar'

tf = tarfile.TarFile(file)

# this saves the csv to a folder within the repo
tf.extract(tf.getnames()[-2], path='AoT_test2.csv')

# the path will be the csv within the saved folder from above.
weekly = pd.read_csv('AoT_test2.csv/chicago-complete.weekly.2019-04-15-to-2019-04-21/data.csv.gz')

# reading into pandas. 
weekly['sensor_path'] = weekly.subsystem + '.' + weekly.sensor + '.' + weekly.parameter
observations = weekly[['timestamp', 'node_id', 'sensor_path', 'value_hrf']]

# observations.to_sql(engine=
