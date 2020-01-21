FROM python:3

ENV PYTHONUNBUFFERED 1

#### Install GEOS ####
# Inspired by: https://hub.docker.com/r/cactusbone/postgres-postgis-sfcgal/~/dockerfile/

ENV GEOS http://download.osgeo.org/geos/geos-3.8.0.tar.bz2

ADD $GEOS /install-postgis/

WORKDIR /install-postgis/geos
RUN tar xf /install-postgis/geos-3.8.0.tar.bz2 -C /install-postgis/geos --strip-components=1
RUN cd /install-postgis/geos/ && \
 ./configure --enable-python && \
 make -j $(nproc) && \
 make install && \
 ldconfig && \
 geos-config --cflags && \
 apt-get update && \
 apt-get install -y binutils libproj-dev gdal-bin

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./app.py" ]
