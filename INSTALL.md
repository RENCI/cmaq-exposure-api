# INSTALL.md

CMAQ Exposure API installation and setup

## Development

Provided example using CentOS 7

Clone repository

```
git clone https://github.com/RENCI/cmaq-exposure-api.git
cd cmaq-exposure-api/
```

Configure database settings

```
cd config/
cp database.cfg.template database.cfg
cp database.ini.template database.ini
```

Update: `database.cfg` (used by bash scripts)

```
export POSTGRES_HOST=database
export POSTGRES_PORT=5432
export POSTGRES_DATABASE=cmaq
export POSTGRES_USERNAME=datatrans
export POSTGRES_PASSWORD=datatrans
```

Update: `database.ini` (used by Python scripts)

```
[postgres]
host = localhost # Change to IP Address of host
port = 5432
database = cmaq
username = datatrans
password = datatrans
```

Start PostgreSQL database

```
cd postgres96/
./start-database.sh
```

Initialize cmaq database

```
cd data-sample/cmaq-init-database/
./init-cmaq-db.sh
./init-cmaq-tables.sh
```

### Populate cmaq database

**Use pre-generared**

```
docker exec -u postgres database pg_dumpall -c -f /var/lib/pgsql/cmaq_base.sql
```

**From scratch**

Run `pre-ingest` scripts

```
cd data-tools/pre-ingest/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
python update-cmaq-tables.py /PATH_TO/CMAQ_DATAFILE
...
python update-common-name.py /PATH_TO/cmaq-exposure-api/data-sample/data/exposure_list.csv
deactivate
```

commands run:

```
DATA_DIR=/projects/datatrans/CMAQ/2010/raw
while read line; do python update-cmaq-tables.py $DATA_DIR/$line; done < <(ls $DATA_DIR | grep 201012)
python update-cmaq-tables.py /projects/datatrans/CMAQ/2011/raw/CCTM_CMAQ_v51_Release_Oct23_NoDust_ed_emis_combine.aconc.01
```

Run `ingest` scripts

```
cd data-tools/ingest/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

commands run:

```
DATA_DIR=/projects/datatrans/CMAQ/2010/raw/
while read line; do python ingest-cmaq-file-develop.py $DATA_DIR/$line 2010; done < <(ls $DATA_DIR | grep 201012)
python ingest-cmaq-file-develop.py /projects/datatrans/CMAQ/2011/raw/CCTM_CMAQ_v51_Release_Oct23_NoDust_ed_emis_combine.aconc.01 2011
```

Create `postgres-functions`

```
cd data-tools/postgres-functions/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
python generate-aggregation-functions.py
```

Two new .sql files should now exist

- `cmaq_variable_aggregates_2010.sql`
- `cmaq_variable_aggregates_2011.sql`

copy/paste the contents of these files as well as `indexes.sql` into the cmaq database

```
docker exec -ti -u postgres database psql -d cmaq
cmaq=# ... # copy/paste contents of indexes.sql,
           # cmaq_variable_aggregates_2010.sql, and 
           # cmaq_variable_aggregates_2011.sql
cmaq=# \q
deactivate
```

Run `post-ingest` scripts

```
cd data-tools/post-ingest/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
python update-variable-aggregates.py
deactivate
```

The pre-populated database named `cmaq_full.sql.gz` was generated at this stage.

```
docker exec -u postgres database pg_dumpall -c -f /var/lib/pgsql/cmaq_full.sql
```

Run the api-server

Create configuration file `ini/connexion.ini` and update settings

```
cd server/
cp ini/connexion.ini.template ini/connexion.ini
```

```
[connexion]
server =
debug = True
port = 5000
keyfile =
certfile =

[sys-path]
exposures = /PATH_TO/cmaq-exposure-api/server/exposures.    # set full path
controllers = /PATH_TO/cmaq-exposure-api/server/controllers # set full path

[postgres]
host = FQDN_OR_IP # Change to IP Address of host
port = 5432
database = cmaq
username = datatrans
password = datatrans
```

Update **host** in `swagger/swagger.yaml` to match your environment

```
...
host: "cmaq-dev.edc.renci.org" # Update to match URL:PORT
...
```

Run `app.py`

```
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

May require ports be opened for viewing the UI, in this case, port 5000.

Example using iptables

```
sudo iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 5000 -j ACCEPT
sudo iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
sudo iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited
```


## Production