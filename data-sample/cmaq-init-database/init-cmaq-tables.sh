#!/usr/bin/env bash

CONFIG_DIR=$(dirname $(dirname $(pwd)))/config
source ${CONFIG_DIR}/database.cfg

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
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "${EXPOSURE_DATA}"
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "ALTER TABLE exposure_data OWNER TO ${POSTGRES_USERNAME};"

# create table exposure_list
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "${EXPOSURE_LIST}"
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "ALTER TABLE exposure_list OWNER TO ${POSTGRES_USERNAME};"

# show tables
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "SELECT * FROM exposure_data LIMIT 1;"
docker exec -u postgres ${POSTGRES_HOST} psql ${POSTGRES_DATABASE} -c "SELECT * FROM exposure_list LIMIT 1;"

exit 0;