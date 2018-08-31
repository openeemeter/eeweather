# Updates for eeweather

Information about version updates and instructions for upgrading where
needed.

## Development

* Update internal database (2018-08-31).

## 0.3.7

* Allow using non-normalized dates, (i.e., dates with non-zero minutes or
  seconds that do not fall exactly on an hour or a day boundary) to access
  `station.load_isd_hourly_temp_data`, `station.load_isd_daily_temp_data`,
  and `station.load_gsod_daily_temp_data`.

## 0.3.6

* Bug fix in ISDStation initialization with handling of null fields.

## 0.3.5

* Added the `rank` parameter in the data field for a station distance EEWeatherWarning.

## 0.3.4

* Created an EEWeatherWarning object to capture distance warnings.

## 0.3.3

* Update internal database (2018-08-03).

## 0.3.2

* Bug fix in `select_stations`.
