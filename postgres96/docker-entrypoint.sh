#!/usr/bin/env bash
set -e

_bash_profile () {
    local OUTFILE=/var/lib/pgsql/.bash_profile
    echo "[ -f /etc/profile ] && source /etc/profile" > ${OUTFILE}
    echo "PGDATA=/var/lib/pgsql/9.6/data" >> ${OUTFILE}
    echo "export PGDATA" >> ${OUTFILE}
    echo "# If you want to customize your settings," >> ${OUTFILE}
    echo "# Use the file below. This is not overridden" >> ${OUTFILE}
    echo "# by the RPMS." >> ${OUTFILE}
    echo "[ -f /var/lib/pgsql/.pgsql_profile ] && source /var/lib/pgsql/.pgsql_profile" >> ${OUTFILE}
    chown postgres:postgres /var/lib/pgsql/.bash_profile
}

_psql_profile () {
    local OUTFILE=/var/lib/pgsql/.pgsql_profile
    echo "#!/usr/bin/env bash" > ${OUTFILE}
    echo "export LANGUAGE=\"en_US.UTF-8\"" >> ${OUTFILE}
    echo "export LANG=\"en_US.UTF-8\"" >> ${OUTFILE}
    echo "export LC_ALL=\"en_US.UTF-8\"" >> ${OUTFILE}
    chown postgres:postgres /var/lib/pgsql/.pgsql_profile
}

_postgresql96-setup() {
    sed -i '/PGDATA=`systemctl show -p Environment "${SERVICE_NAME}.service" |/,+6 s/^/#/' /usr/pgsql-9.6/bin/postgresql96-setup
}

_pg_hba_conf() {
    sed -i 's!all             127.0.0.1/32            ident!all             127.0.0.1/32            md5!' /var/lib/pgsql/9.6/data/pg_hba.conf
    sed -i 's!all             ::1/128                 ident!all             ::1/128                 md5!' /var/lib/pgsql/9.6/data/pg_hba.conf
    echo "host  all  all 0.0.0.0/0 md5" >> /var/lib/pgsql/9.6/data/pg_hba.conf
}

_postgresql_conf() {
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/9.6/data/postgresql.conf
#    sed -i "s/#client_encoding = sql_ascii/client_encoding = UTF8/" /var/lib/pgsql/9.6/data/postgresql.conf
}

if [[ "$1" = 'run' ]]; then
    if [ "$(ls -A /var/lib/pgsql/9.6/data)" ]; then
        echo "WARNING: Data directory is not empty!"
    else
        _bash_profile
        _psql_profile
        _postgresql96-setup
        source /var/lib/pgsql/.bash_profile
        /usr/pgsql-9.6/bin/postgresql96-setup initdb
        _pg_hba_conf
        _postgresql_conf
    fi
    runuser -l postgres -c '/usr/pgsql-9.6/bin/postgres -D /var/lib/pgsql/9.6/data -p 5432'
else
    exec "$@"
fi