#!/usr/bin/env bash

# Usage: ./init-cmaq-db.sh [--postgres]
#   --postgres: only use when you are invoking as the system's postgres user

CONFIG_DIR=$(dirname $(dirname $(pwd)))/config
source ${CONFIG_DIR}/database.cfg

if [ "$1" = "--postgres" ]; then
    USER_POSTGRES=true
else
    USER_POSTGRES=false
fi

# Create ${POSTGRES_USERNAME} user if it does not already exist
if $USER_POSTGRES; then
    if [[ -z $(psql postgres -tAc \
    "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USERNAME}'") ]]; then
        psql -c "CREATE USER "${POSTGRES_USERNAME}" WITH PASSWORD '"${POSTGRES_PASSWORD}"';";
    else
        echo "User ${POSTGRES_USERNAME} already exists";
    fi
else
    if [[ -z $(docker exec -u postgres ${POSTGRES_HOST} psql postgres -tAc \
    "SELECT 1 FROM pg_roles WHERE rolname='${POSTGRES_USERNAME}'") ]]; then
        docker exec -u postgres ${POSTGRES_HOST} psql -c \
        "CREATE USER "${POSTGRES_USERNAME}" WITH PASSWORD '"${POSTGRES_PASSWORD}"';";
    else
        echo "User ${POSTGRES_USERNAME} already exists";
    fi
fi
# Create ${POSTGRES_DATABASE} database if it does not already exist
if $USER_POSTGRES; then
    if [[ -z $(psql postgres -tAc \
    "SELECT 1 from pg_database WHERE datname='${POSTGRES_DATABASE}'") ]]; then
        psql -c "CREATE DATABASE "${POSTGRES_DATABASE}";";
    else
        echo "Database ${POSTGRES_DATABASE} already exists";
    fi
else
    if [[ -z $(docker exec -u postgres ${POSTGRES_HOST} psql postgres -tAc \
    "SELECT 1 from pg_database WHERE datname='${POSTGRES_DATABASE}'") ]]; then
        docker exec -u postgres ${POSTGRES_HOST} psql -c "CREATE DATABASE "${POSTGRES_DATABASE}";";
    else
        echo "Database ${POSTGRES_DATABASE} already exists";
    fi
fi

# Grant all privileges on ${POSTGRES_DATABASE} to ${POSTGRES_USERNAME} if not already applied
if $USER_POSTGRES; then
    psql -c 'GRANT ALL PRIVILEGES ON DATABASE "'${POSTGRES_DATABASE}'" TO '${POSTGRES_USERNAME}';'
else
    docker exec -u postgres ${POSTGRES_HOST} psql -c \
    'GRANT ALL PRIVILEGES ON DATABASE "'${POSTGRES_DATABASE}'" TO '${POSTGRES_USERNAME}';'
fi

# Create extension postgis, postgis_topology and ogr_fdw
# $ docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c '\dx'
#                                          List of installed extensions
#        Name       | Version |   Schema   |                             Description
# ------------------+---------+------------+---------------------------------------------------------------------
#  ogr_fdw          | 1.0     | public     | foreign-data wrapper for GIS data access
#  plpgsql          | 1.0     | pg_catalog | PL/pgSQL procedural language
#  postgis          | 2.3.3   | public     | PostGIS geometry, geography, and raster spatial types and functions
#  postgis_topology | 2.3.3   | topology   | PostGIS topology spatial types and functions
# (4 rows)

if $USER_POSTGRES; then
    if [[ -z $(psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='postgis'") ]]; then
        psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION postgis;";
    else
        echo "Extension postgis already exists";
    fi
else
    if [[ -z $(docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='postgis'") ]]; then
        docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION postgis;";
    else
        echo "Extension postgis already exists";
    fi
fi

if $USER_POSTGRES; then
    if [[ -z $(psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='postgis_topology'") ]]; then
        psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION postgis_topology;";
    else
        echo "Extension postgis_topology already exists";
    fi
else
    if [[ -z $(docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='postgis_topology'") ]]; then
        docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION postgis_topology;";
    else
        echo "Extension postgis_topology already exists";
    fi
fi

if $USER_POSTGRES; then
    if [[ -z $(psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='ogr_fdw'") ]]; then
        psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION ogr_fdw;";
    else
        echo "Extension ogr_fdw already exists";
    fi
else
    if [[ -z $(docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -tAc \
    "SELECT 1 from pg_extension WHERE extname='ogr_fdw'") ]]; then
        docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "CREATE EXTENSION ogr_fdw;";
    else
        echo "Extension ogr_fdw already exists";
    fi
fi

if $USER_POSTGRES; then
    psql -c '\l'
    psql ${POSTGRES_DATABASE} -c '\dx'
else
    docker exec -u postgres ${POSTGRES_HOST} psql -c '\l'
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c '\dx'
fi

exit 0;
