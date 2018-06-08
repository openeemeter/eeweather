import json
from click.testing import CliRunner


from eeweather.cli import (
    cli,
    inspect_isd_station,
    inspect_isd_file_years,
    inspect_isd_filenames,
    inspect_gsod_filenames,
)


def test_eeweather_cli():
    runner = CliRunner()

    result = runner.invoke(cli)
    assert result.exit_code == 0
    assert len(result.output) > 100


def test_inspect_isd_station():
    runner = CliRunner()

    result = runner.invoke(inspect_isd_station, ['722880'])
    assert result.exit_code == 0
    assert json.loads(result.output) == {
        'ba_climate_zone': 'Hot-Dry',
        'ca_climate_zone': 'CA_09',
        'elevation': '+0236.2',
        'icao_code': 'KBUR',
        'iecc_climate_zone': '3',
        'iecc_moisture_regime': 'B',
        'latitude': '+34.201',
        'longitude': '-118.358',
        'name': 'BURBANK-GLENDALE-PASA ARPT',
        'quality': 'high',
        'recent_wban_id': '23152',
        'state': 'CA',
        'usaf_id': '722880',
        'wban_ids': '23152,99999'
    }


def test_inspect_isd_station_unrecognized():
    runner = CliRunner()
    result = runner.invoke(inspect_isd_station, ['INVALID'])
    assert result.exit_code == -1


def test_inspect_isd_file_years():
    runner = CliRunner()

    result = runner.invoke(inspect_isd_file_years, ['722880'])
    assert result.exit_code == 0
    assert json.loads(result.output) == [
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2006'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2007'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2008'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2009'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2010'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2011'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2012'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2013'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2014'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2015'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2016'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2017'},
        {'usaf_id': '722880', 'wban_id': '23152', 'year': '2018'}
    ]


def test_inspect_isd_file_years_unrecognized():
    runner = CliRunner()
    result = runner.invoke(inspect_isd_file_years, ['INVALID'])
    assert result.exit_code == -1


def test_inspect_isd_filenames():
    runner = CliRunner()

    result = runner.invoke(inspect_isd_filenames, ['722880', '2017'])
    assert result.exit_code == 0
    assert result.output == (
        'ftp://ftp.ncdc.noaa.gov/pub/data/noaa/2017/722880-23152-2017.gz\n'
    )


def test_inspect_isd_filenames_unrecognized():
    runner = CliRunner()
    result = runner.invoke(inspect_isd_filenames, ['INVALID', '2017'])
    assert result.exit_code == -1


def test_inspect_gsod_filenames():
    runner = CliRunner()

    result = runner.invoke(inspect_gsod_filenames, ['722880', '2017'])
    assert result.exit_code == 0
    assert result.output == (
        'ftp://ftp.ncdc.noaa.gov/pub/data/gsod/2017/722880-23152-2017.op.gz\n'
    )


def test_inspect_gsod_filenames_unrecognized():
    runner = CliRunner()
    result = runner.invoke(inspect_gsod_filenames, ['INVALID', '2017'])
    assert result.exit_code == -1
