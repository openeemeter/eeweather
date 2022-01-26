FROM nikolaik/python-nodejs:python3.6-nodejs12

RUN apt-get update \
  && apt-get install -yqq \
    --allow-change-held-packages \
    # sphinxcontrib-spelling dependency
    libenchant-dev \
    # geo libraries
    binutils libproj-dev gdal-bin libgeos-dev \
    # unzip for rebuilding metadata.db
    unzip \
    # node for mapshaper
    nodejs \
    # for access to metadata.db
    sqlite3 libsqlite3-dev

RUN npm install -g mapshaper

COPY requirements.txt requirements.txt
COPY dev-requirements.txt dev-requirements.txt

RUN set -ex &&  pip install -r requirements.txt
RUN set -ex &&  pip install -r dev-requirements.txt
RUN set -ex && pip install cartopy jupyterlab

ENV PYTHONPATH=/app

COPY setup.py README.rst /app/
COPY eeweather/ /app/eeweather
RUN set -ex && cd /usr/local/lib/ && python /app/setup.py develop

WORKDIR /app
