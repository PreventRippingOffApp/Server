FROM python:3

ENV PYTHONUNBUFFERED 1

#### Install GEOS ####
# Inspired by: https://hub.docker.com/r/cactusbone/postgres-postgis-sfcgal/~/dockerfile/

ENV GEOS http://download.osgeo.org/geos/geos-3.8.0.tar.bz2

WORKDIR /install-postgis/
RUN wget $GEOS

WORKDIR /install-postgis/geos
RUN tar xf /install-postgis/geos-3.8.0.tar.bz2 -C /install-postgis/geos --strip-components=1
RUN cd /install-postgis/geos/ && \
 ./configure --enable-python && \
 make -j $(nproc) && \
 make install && \
 ldconfig && \
 geos-config --cflags && \
 apt-get update && \
 apt-get install -y binutils libproj-dev gdal-bin unzip

WORKDIR /usr/src/app
RUN wget https://www.esrij.com/cgi-bin/wp/wp-content/uploads/2017/01/japan_ver81.zip && \
mkdir -p instance/shp_japan/ && \
unzip -d ./instance/shp_japan/ japan_ver81.zip

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


CMD [ "python", "./app.py" ]
