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

EXPOSURE_DATA="CREATE TABLE IF NOT EXISTS exposure_data (
  id                SERIAL UNIQUE PRIMARY KEY,
  col               INT,
  row               INT,
  utc_date_time     TIMESTAMP
);"

EXPOSURE_LIST="CREATE TABLE IF NOT EXISTS exposure_list (
  id                SERIAL UNIQUE PRIMARY KEY,
  type              TEXT,
  description       TEXT,
  units             TEXT,
  common_name       TEXT,
  utc_min_date_time TIMESTAMP,
  utc_max_date_time TIMESTAMP,
  resolution        TEXT,
  aggregation       TEXT
);"

# create table exposure_data
if $USER_POSTGRES; then
    psql ${POSTGRES_DATABASE} -c "${EXPOSURE_DATA}"
    psql ${POSTGRES_DATABASE} -c "ALTER TABLE exposure_data OWNER TO ${POSTGRES_USERNAME};"
else
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "${EXPOSURE_DATA}"
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c \
    "ALTER TABLE exposure_data OWNER TO ${POSTGRES_USERNAME};"
fi

# create table exposure_list
if $USER_POSTGRES; then
    psql ${POSTGRES_DATABASE} -c "${EXPOSURE_LIST}"
    psql ${POSTGRES_DATABASE} -c "ALTER TABLE exposure_list OWNER TO ${POSTGRES_USERNAME};"
else
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "${EXPOSURE_LIST}"
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c \
    "ALTER TABLE exposure_list OWNER TO ${POSTGRES_USERNAME};"
fi

# show tables
if $USER_POSTGRES; then
    psql ${POSTGRES_DATABASE} -c "SELECT * FROM exposure_data LIMIT 1;"
    psql ${POSTGRES_DATABASE} -c "SELECT * FROM exposure_list LIMIT 1;"
else
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "SELECT * FROM exposure_data LIMIT 1;"
    docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c \
    "SELECT * FROM exposure_list LIMIT 1;"
fi

exit 0;