#!/usr/bin/env bash

_set_connection_ini() {
    > ini/connexion.ini
    echo "[connexion]" >> ini/connexion.ini
    if [[ -z ${CONNEXION_SERVER} ]]; then
        echo "server = " >> ini/connexion.ini
    else
        echo "server = "${CONNEXION_SERVER} >> ini/connexion.ini
    fi
    echo "debug = "${CONNEXION_DEBUG} >> ini/connexion.ini
    echo "port = "${API_SERVER_PORT} >> ini/connexion.ini
    if [[ -z ${API_SERVER_KEYFILE} ]]; then
        echo "keyfile = " >> ini/connexion.ini
    else
        echo "keyfile = "${API_SERVER_KEYFILE} >> ini/connexion.ini
    fi
    if [[ -z ${API_SERVER_CERTFILE} ]]; then
        echo "certfile = ">> ini/connexion.ini
    else
        echo "certfile = "${API_SERVER_CERTFILE} >> ini/connexion.ini
    fi
    echo "" >> ini/connexion.ini
    echo "[sys-path]" >> ini/connexion.ini
    echo "exposures = "${SYS_PATH_EXPOSURES} >> ini/connexion.ini
    echo "controllers = "${SYS_PATH_CONTROLLERS} >> ini/connexion.ini
    echo "" >> ini/connexion.ini
    echo "[postgres]" >> ini/connexion.ini
    echo "host = "${POSTGRES_HOST} >> ini/connexion.ini
    echo "port = "${POSTGRES_PORT} >> ini/connexion.ini
    echo "database = "${POSTGRES_DATABASE} >> ini/connexion.ini
    echo "username = "${POSTGRES_USERNAME} >> ini/connexion.ini
    echo "password = "${POSTGRES_PASSWORD} >> ini/connexion.ini
}

if [[ "$1" = 'app.py' ]]; then
    # set connexion.ini file
    _set_connection_ini

    # update swagger.yaml file
    if [[ ! -z ${SWAGGER_HOST} ]]; then
        sed -i 's/host.*/host: \"'${SWAGGER_HOST}'\"/g' /cmaq-exposure/swagger/swagger.yaml
    fi

    # update /etc/hosts if POSTGRES_IP is passed in
    if [[ -n $POSTGRES_IP ]]; then
        echo "${POSTGRES_IP} ${POSTGRES_HOST}" >> /etc/hosts
    fi

    # run the app
    python app.py
else
    exec "$@"
fi