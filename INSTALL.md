# INSTALL.md

CMAQ Exposure API installation and setup

## Development

Example using CentOS 7 to build a new development environment using CMAQ NetCDF data files.

### Setup and configure

Clone repository

```
git clone https://github.com/RENCI/cmaq-exposure-api.git
cd cmaq-exposure-api/
```

Configuration

- Configure database settings

	```
	cd config/
	cp database.cfg.template database.cfg
	cp database.ini.template database.ini
	```

- Update: `database.cfg` (used by bash scripts)

	```
	export POSTGRES_HOST=database
	export POSTGRES_PORT=5432
	export POSTGRES_DATABASE=cmaq
	export POSTGRES_USERNAME=datatrans
	export POSTGRES_PASSWORD=datatrans
	```

- Update: `database.ini` (used by Python scripts)

	```
	[postgres]
	host = localhost # Change to IP Address of host
	port = 5432
	database = cmaq
	username = datatrans
	password = datatrans
	```

### Database

Start PostgreSQL database

- Blank database

	```
	cd postgres96/
	./start-database.sh
	```

- Pre-populated database (skip to: [Run the api-server]() when completed)

	```
	cd postgres96/
	./start-database.sh --load-cmaq
	```
	

Initialize cmaq database

```
cd data-sample/cmaq-init-database/
./init-cmaq-db.sh
./init-cmaq-tables.sh
```

Run `pre-ingest` scripts

```
cd data-tools/pre-ingest/
virtualenv -p /usr/bin/python3.6 venv
source venv/bin/activate
pip install -r requirements.txt
# RUN CMAQ TABLE UPDATE SCRIPT(S)
python update-common-name.py /PATH_TO/cmaq-exposure-api/data-sample/data/exposure_list.csv
deactivate
```

- Example cmaq table update commands run against real CMAQ data files:

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
# RUN INGEST SCRIPT(S)
deactivate
```

- Example ingest commands run against real CMAQ data files:

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

- Two new .sql files should now exist, 1 for each year of data found
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

- The pre-populated database named `cmaq_full.sql.gz` was generated at this stage.

	```
	docker exec -u postgres database pg_dumpall -c -f /var/lib/pgsql/cmaq_full.sql
	```

### Run the api-server

Create configuration file `ini/connexion.ini` and update the `FQDN_OR_IP ` settings

```
cd server/
cp ini/connexion.ini.template ini/connexion.ini
```

- Example `ini/connexion.ini` file: 

	```
	[connexion]
	server =
	debug = True
	port = 5000
	keyfile =
	certfile =
	
	[sys-path]
	exposures = ./exposures
	controllers = ./controllers
	
	[postgres]
	host = FQDN_OR_IP # Change to IP Address of host running the database
	port = 5432
	database = cmaq
	username = datatrans
	password = datatrans
	```

Update **host** in `swagger/swagger.yaml` to match your environment

- Example:

	```
	...
	host: "cmaq-dev.edc.renci.org" # Update to match HOSTNAME:PORT
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

- Example using iptables

	```
	sudo iptables -A INPUT -p tcp -m state --state NEW -m tcp --dport 5000 -j ACCEPT
	sudo iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited
	sudo iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited
	```


## Production