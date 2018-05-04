from io import BytesIO
import pkg_resources
import re
import tempfile

from eeweather.cache import KeyValueStore


def write_isd_file(bytes_string):
    with pkg_resources.resource_stream('resources', 'ISD.gz') as f:
        bytes_string.write(f.read())


def write_missing_isd_file(bytes_string):
    with pkg_resources.resource_stream('resources', 'ISD-MISSING.gz') as f:
        bytes_string.write(f.read())


def write_gsod_file(bytes_string):
    with pkg_resources.resource_stream('resources', 'GSOD.op.gz') as f:
        bytes_string.write(f.read())


def write_missing_gsod_file(bytes_string):
    with pkg_resources.resource_stream('resources', 'GSOD-MISSING.op.gz') as f:
        bytes_string.write(f.read())


class MockNOAAFTPConnectionProxy():

    def read_file_as_bytes(self, filename):
        bytes_string = BytesIO()

        if re.match('/pub/data/noaa/2007/722874-93134-2007.gz', filename):
            write_isd_file(bytes_string)
        elif re.match('/pub/data/noaa/2006/722874-93134-2006.gz', filename):
            write_missing_isd_file(bytes_string)
        elif re.match('/pub/data/gsod/2007/722874-93134-2007.op.gz', filename):
            write_gsod_file(bytes_string)
        elif re.match('/pub/data/gsod/2006/722874-93134-2006.op.gz', filename):
            write_missing_gsod_file(bytes_string)

        bytes_string.seek(0)
        return bytes_string


class MockKeyValueStoreProxy():

    def __init__(self):
        # create a new test store in a temporary folder
        self.store = KeyValueStore('sqlite:///{}/cache.db'.format(tempfile.mkdtemp()))

    def get_store(self):
        return self.store
