import json
import subprocess

import click

from . import (
    get_isd_station_metadata as _get_isd_station_metadata,
    get_isd_file_metadata as _get_isd_file_metadata,
    get_isd_filenames as _get_isd_filenames,
    get_gsod_filenames as _get_gsod_filenames,
)
from .exceptions import UnrecognizedUSAFIDError

from .database import build_metadata_db, inspect_metadata_db


@click.group()
def cli():
    '''Example usage

    See station metadata:

    \b
        $ eeweather inspect_isd_station 722880
        {
          "usaf_id": "722880",
          "wban_ids": "23152,99999",
          "recent_wban_id": "23152",
          "name": "BURBANK-GLENDALE-PASA ARPT",
          "latitude": "+34.201",
          "longitude": "-118.358",
          "elevation": "+0236.2"
        }

    See station file data:

    \b
        $ eeweather inspect_isd_file_years 722880
        {...}

    See station file names for ISD:

    \b
        $ eeweather inspect_isd_filenames 722880 2017
        ftp://ftp.ncdc.noaa.gov/pub/data/noaa/2017/722880-23152-2017.gz

    Or for GSOD:

    \b
        $ eeweather inspect_gsod_filenames 722880 2017
        ftp://ftp.ncdc.noaa.gov/pub/data/gsod/2017/722880-23152-2017.op.gz

    Rebuild metadata db from primary source files:

    \b
        $ eeweather rebuild_db

    Inspect metadata db using sqlite3 CLI:

    \b
        $ eeweather inspect_db


    '''
    pass  # pragma: no cover


@cli.command()
@click.argument('usaf_id')
def inspect_isd_station(usaf_id):
    metadata = _get_isd_station_metadata(usaf_id)
    click.echo(json.dumps(metadata, indent=2))


@cli.command()
@click.argument('usaf_id')
def inspect_isd_file_years(usaf_id):
    metadata = _get_isd_file_metadata(usaf_id)
    click.echo(json.dumps(metadata, indent=2))


@cli.command()
@click.argument('usaf_id')
@click.argument('year')
def inspect_isd_filenames(usaf_id, year):
    filenames = _get_isd_filenames(usaf_id, year, with_host=True)
    for f in filenames:
        click.echo(f)


@cli.command()
@click.argument('usaf_id')
@click.argument('year')
def inspect_gsod_filenames(usaf_id, year):
    filenames = _get_gsod_filenames(usaf_id, year, with_host=True)
    for f in filenames:
        click.echo(f)


@cli.command()
@click.option('--zcta-geometry/--no-zcta-geometry', default=False)
@click.option('--iecc-climate-zone-geometry/--no-iecc-climate-zone-geometry', default=True)
@click.option('--iecc-moisture-regime-geometry/--no-iecc-moisture-regime-geometry', default=True)
@click.option('--ba-climate-zone-geometry/--no-ba-climate-zone-geometry', default=True)
@click.option('--ca-climate-zone-geometry/--no-ca-climate-zone-geometry', default=True)
def rebuild_db(
        zcta_geometry, iecc_climate_zone_geometry, iecc_moisture_regime_geometry,
        ba_climate_zone_geometry, ca_climate_zone_geometry):
    build_metadata_db(  # pragma: no cover
        zcta_geometry, iecc_climate_zone_geometry, iecc_moisture_regime_geometry,
        ba_climate_zone_geometry, ca_climate_zone_geometry)


@cli.command()
def inspect_db():
    inspect_metadata_db()  # pragma: no cover
