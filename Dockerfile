FROM python:3.6.4-stretch

# -- Install Pipenv:
RUN set -ex && pip install pipenv --upgrade

RUN apt-get update \
  && apt-get install -yqq \
    # sphinxcontrib-spelling dependency
    libenchant-dev \
    # geo libraries
    binutils libproj-dev gdal-bin libgeos-dev

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN set -ex && pipenv install --system --deploy --dev

COPY setup.py README.rst /app/

COPY eeweather/ /app/eeweather
COPY docs/ /app/docs
COPY scripts/ /app/scripts
COPY tests/ /app/tests

RUN set -ex && pipenv install --system --deploy --skip-lock cartopy jupyter
RUN set -ex && pipenv install --system --deploy --skip-lock -e /app

WORKDIR /app
