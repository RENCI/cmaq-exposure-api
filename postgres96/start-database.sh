#!/usr/bin/env bash

# Usage: ./init-cmaq-db.sh [--postgres]
#   --postgres: only use when you are invoking as the system's postgres user

DATA_DIR=$(dirname $(pwd))/data-sample/data

if [ "$1" = "--load-cmaq" ]; then
    LOAD_CMAQ=true
else
    LOAD_CMAQ=false
fi

docker-compose build
docker-compose up -d

if $LOAD_CMAQ; then
    sleep 5s
    echo "--load-cmaq:"
    if [[ ! -f $DATA_DIR/cmaq_full.sql  ]]; then
        cd $DATA_DIR
        gunzip -c cmaq_full.sql.gz > cmaq_full.sql
        cd -
    fi
    # Ensure all prior connections to the database are removed prior to dropping the database
    docker exec -u postgres -ti database psql -c "REVOKE CONNECT ON DATABASE postgres FROM public;"
    docker exec -u postgres -ti database psql -c "SELECT pid, pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = current_database() AND pid <> pg_backend_pid();"
    docker cp $DATA_DIR/cmaq_full.sql database:/cmaq_full.sql
    docker exec -u postgres -ti database psql -f /cmaq_full.sql
fi

echo "Database is running - use your local IP address for connection"

exit 0;
