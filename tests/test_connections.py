#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

   Copyright 2018 Open Energy Efficiency, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

from eeweather.connections import CSVRequestProxy
import requests

from unittest.mock import Mock

def mock_get(url):
    get_result = Mock(status_code=200)

    get_result.request.url = url

    get_result.text = {
        'bogus://example.com/a': 'response-a',
        'bogus://example.com/b': 'response-b'
    }[url]

    return get_result


def test_csv_request_proxy_with_different_urls(mocker):
    proxy = CSVRequestProxy()

    mocker.patch.object(requests, 'get', side_effect=mock_get)

    assert proxy.get_text('bogus://example.com/a') == 'response-a'
    assert proxy.get_text('bogus://example.com/b') == 'response-b'
