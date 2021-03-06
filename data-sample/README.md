# Data Sample

Sample data is provided for development purposes and should be of the same format as that which is deployed in production.

All scripts herein assume the use of the development [database](../postgres96). These scripts should be used as a guide for establishing similar ingest scripts in the production enviornment.

**Note**: Adapting these scripts for production use is left to the user and will not be discussed here.

## Data

Sample data is provided that is either a copy of, or derived from the production CMAQ data for 2010 and 2011.

- `cmaq_full.sql.gz` - Sample database in `.gz` format. Used when the `--load-cmaq` flag is present in the `start-database.sh` call.
- `exposure_list.csv` - List of exposure variables as found when 2010 and 2011 CMAQ data is loaded. Used by the `data-tools/update-common-name.py` script to populate the `common_name` attribute if present.
- `quality-metrics/`
	- `AMET-MPE-Metrics.csv` - List of quality metric variables and common names used to populate the `quailty_metrics_list` table.
	- `CMAQ_2010_36k_base_O3_1_timeseries.csv` - CMAQ domain level quality metric data for Ozone (O3) during 2010.
	- `CMAQ_2011_12k_O3_1_timeseries.csv` - CMAQ domain level quality metric data for Ozone (O3) during 2011.


## Configuration and initialization

The scripts herein are setup to find their configuration files relative to their position in the repository, adjust as required for your deployment.

**Configuration**

- The file named **database.cfg** defines the configuration to be used for setting up the database. This file will be used as the informational source for the sample data scripts in this directory.

- `config/database.cfg` default values:

	```config
	export POSTGRES_HOST=database
	export POSTGRES_PORT=5432
	export POSTGRES_DATABASE=cmaq
	export POSTGRES_USERNAME=datatrans
	export POSTGRES_PASSWORD=datatrans
	```

**Initialize database**

Initialzation scripts are found in the directory named `data-sample/cmaq-init-database/`

- The script named `init-cmaq-db.sh` is used to initialize the database based on the settings found in `config/database.cfg`.

	```
	Usage: $ ./init-cmaq-db.sh
	```

- Example:

	```
	$ ./init-cmaq-db.sh
	CREATE ROLE
	CREATE DATABASE
	GRANT
	CREATE EXTENSION
	CREATE EXTENSION
	CREATE EXTENSION
	                                  List of databases
	   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
	-----------+----------+----------+-------------+-------------+------------------------
	 cmaq      | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/postgres          +
	           |          |          |             |             | postgres=CTc/postgres +
	           |          |          |             |             | datatrans=CTc/postgres
	 postgres  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
	 template0 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres           +
	           |          |          |             |             | postgres=CTc/postgres
	 template1 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres           +
	           |          |          |             |             | postgres=CTc/postgres
	(4 rows)
	
	                                         List of installed extensions
	       Name       | Version |   Schema   |                             Description
	------------------+---------+------------+---------------------------------------------------------------------
	 ogr_fdw          | 1.0     | public     | foreign-data wrapper for GIS data access
	 plpgsql          | 1.0     | pg_catalog | PL/pgSQL procedural language
	 postgis          | 2.3.4   | public     | PostGIS geometry, geography, and raster spatial types and functions
	 postgis_topology | 2.3.4   | topology   | PostGIS topology spatial types and functions
	(4 rows)
	```

**Initialize Tables**

- The script named `init-cmaq-tables.sh` is used to tables based on the settings found in `config/database.cfg`.

	```
	Usage: $ ./init-cmaq-tables.sh
	```

- Example:

	```
	$ ./init-cmaq-tables.sh
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	 id | col | row | utc_date_time
	----+-----+-----+---------------
	(0 rows)
	
	 id | variable | description | units | common_name | utc_min_date_time | utc_max_date_time | resolution | aggregation | has_quality_metric
	----+----------+-------------+-------+-------------+-------------------+-------------------+------------+-------------+--------------------
	(0 rows)
	
	 id | utc_date_time
	----+---------------
	(0 rows)
	
	 id | variable | description | common_name
	----+----------+-------------+-------------
	(0 rows)
	```
	
**Notes**: 

- Prior to loading sample data user's should review the [pre-ingest](../data-tools) tools for proper database preparation.
- The cmaq-init scripts default to docker use, but also have a `--postgres` flag for using against a regular PostgreSQL installation.

Example:

- Use when logged in as user `postgres` with access to the database.

	```
	-bash-4.2$ whoami
	postgres
	-bash-4.2$ ./init-cmaq-db.sh --postgres
	CREATE ROLE
	CREATE DATABASE
	GRANT
	CREATE EXTENSION
	CREATE EXTENSION
	CREATE EXTENSION
	                                  List of databases
	   Name    |  Owner   | Encoding |   Collate   |    Ctype    |   Access privileges
	-----------+----------+----------+-------------+-------------+------------------------
	 cmaq      | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =Tc/postgres          +
	           |          |          |             |             | postgres=CTc/postgres +
	           |          |          |             |             | datatrans=CTc/postgres
	 postgres  | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
	 template0 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres           +
	           |          |          |             |             | postgres=CTc/postgres
	 template1 | postgres | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/postgres           +
	           |          |          |             |             | postgres=CTc/postgres
	(4 rows)
	
	                                         List of installed extensions
	       Name       | Version |   Schema   |                             Description
	------------------+---------+------------+---------------------------------------------------------------------
	 ogr_fdw          | 1.0     | public     | foreign-data wrapper for GIS data access
	 plpgsql          | 1.0     | pg_catalog | PL/pgSQL procedural language
	 postgis          | 2.3.4   | public     | PostGIS geometry, geography, and raster spatial types and functions
	 postgis_topology | 2.3.4   | topology   | PostGIS topology spatial types and functions
	(4 rows)
	
	-bash-4.2$ ./init-cmaq-tables.sh --postgres
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	CREATE TABLE
	ALTER TABLE
	 id | col | row | utc_date_time
	----+-----+-----+---------------
	(0 rows)
	
	 id | variable | description | units | common_name | utc_min_date_time | utc_max_date_time | resolution | aggregation | has_quality_metric
	----+----------+-------------+-------+-------------+-------------------+-------------------+------------+-------------+--------------------
	(0 rows)
	
	 id | utc_date_time
	----+---------------
	(0 rows)
	
	 id | variable | description | common_name
	----+----------+-------------+-------------
	(0 rows)
	```