import ee
import pandas as pd
import matplotlib.pyplot as plt
ee.Authenticate()
ee.Initialize()


def get_data(type='aerosol',
             location=(-2.589274, 51.455032),
             start_date='2020-01-01',
             end_date='2020-01-31',
             radius=None,
             scale=None):
  """ 
  Get data from Sentinel-5P for a given location and time period.
  param: type: either aerosol, ozone, sulphur dioxide, nitrogen dioxide, carbon monoxide
  param: centre: lat long tuple of centre of area
  param: start_date: start date of data, format YYYY-MM-DD
  param: end_date: end date of data, format YYYY-MM-DD
  param: radius: radius of area in km
  param: scale: scale of data in metres
  return: pandas dataframe of data
  """

  database = {'aerosol': ['COPERNICUS/S5P/OFFL/L3_AER_AI', 'absorbing_aerosol_index'],
              'nitrogen dioxide': ['COPERNICUS/S5P/NRTI/L3_NO2', 'tropospheric_NO2_column_number_density'],
              'ozone': ['COPERNICUS/S5P/NRTI/L3_O3', 'O3_column_number_density'],
              'sulphur dioxide': ['COPERNICUS/S5P/NRTI/L3_SO2', 'SO2_column_number_density'],
              'carbon monoxide': ['COPERNICUS/S5P/NRTI/L3_CO', 'CO_column_number_density']}

  collection = ee.ImageCollection(database[type][0]) \
      .select(database[type][1]) \
      .filterDate(start_date, end_date)

  if radius is None:
    if isinstance(location, list):
      roi = ee.Geometry.MultiPoint(location)
  else:
    if not isinstance(location, (tuple, list)):
      raise ValueError('location must be a tuple or list')
    radius *= 1000
    poi = ee.Geometry.Point(location)
    roi = poi.buffer(radius)

  data = collection.getRegion(roi, scale).getInfo()

  df = pd.DataFrame(data)
  df.columns = data[0]
  df = df[1:]

  data_column = database[type][1]

  df['time'] = pd.to_datetime(df['time'], unit='ms')
  df['longitude'] = pd.to_numeric(df['longitude'], downcast='float')
  df['latitude'] = pd.to_numeric(df['latitude'], downcast='float')
  df[data_column] = pd.to_numeric(df[data_column], downcast='float')
  # df['day'] = df['time'].dt.day
  df.drop('id', axis=1, inplace=True)
  # drop rows where data column is nan
  df = df.dropna(subset=[data_column])
  df['lat_long'] = list(zip(df.latitude, df.longitude))
  df['lat_long'] = df['lat_long'].apply(lambda x: tuple(round(i, 3) for i in x))
  df.time = pd.to_datetime(df.time, utc=True)
  return df

if __name__ == '__main__':
    df = get_data()
    print(df.head())
    df.plot(x='time', y='absorbing_aerosol_index')
    plt.show()