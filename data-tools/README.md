# Data Tools

Tools related to data and database maintenance.

**Note**: User specific settings denoted by `/PATH_TO/` in files

1. line 8: `pre-ingest/update-cmaq-tables.py`
2. line 8: `pre-ingest/update-cmaq-tables-dryrun.py`
3. line 7: `pre-ingest/update-common-name.py`
4. line 6: `postgres-functions/generate-aggregation-functions.py`
5. line 7: `post-ingest/update-variable-aggregates.py`

## pre-ingest

Sanity checks to run against the database prior to ingesting new CMAQ data.
Updates to the common name for the CMAQ exposure types.

### Table Column Validation

Prior to running the ingestion scripts the database should be checked for compatibility.

This is done by scanning the CMAQ NetCDF files for the list of variables and checking them against the existing columns of the database. If discrepancies are found then generate the appropriate SQL commands to update the impacted tables.

1. `update-cmaq-tables.py`: 
	- Usage: `$ python update-cmaq-tables.py FILENAME`
	- Validate that columns in the `exposure_data` table match that of the data in `FILENAME`, ADD the missing columns as discovered.
	- Validate that the descriptions in the `exposure_list` table match that of the data in `FILENAME`, INSERT or UPDATE the descriptions row as discovered.
2. `update-cmaq-tables-dryrun.py`:
	- Usage: `$ python update-cmaq-tables-dryrun.py FILENAME`
	- Same features as `update-cmaq-tables.py`, but only prints the findings and does not execute the SQL queries against the database.

**Example**:

**\*** Assumes running python3 environment with the appropriate packages installed as defined in the `requirements.txt` file.

- Also ensure that the `dbcfg.read` call is pointing to the correct directory on your system.

	```
	line 8: dbcfg.read('/PATH_TO/cmaq-exposure-api/config/database.ini')
	```

Initially the database starts as stark tables with no data in them. Reference from the `postgres96/init-cmaq-tables.sh` script.

```
$ ./init-cmaq-tables.sh
CREATE TABLE
ALTER TABLE
CREATE TABLE
ALTER TABLE
 id | col | row | utc_date_time
----+-----+-----+---------------
(0 rows)

 id | variable | description | units | common_name | utc_min_date_time | utc_max_date_time | resolution | aggregation
----+------+-------------+-------+-------------+-------------------+-------------------+------------+-------------
(0 rows)
```

As CMAQ data is staged for ingest, the pre-ingest scripts will modify the table structure and contents to match what is discovered in each file.

```
$ python update-cmaq-tables.py /CMAQ/2011/raw/CCTM_CMAQ_v51_Release_Oct23_NoDust_ed_emis_combine.aconc.01
TFLAG: Already defined
ALD2: Adding columns
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2 FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_avg_24hr FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_max_24hr FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_avg_7day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_max_7day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_avg_14day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS ald2_max_14day FLOAT;
...
PM25_FRM: Adding columns
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_avg_24hr FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_max_24hr FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_avg_7day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_max_7day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_avg_14day FLOAT;
  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS pm25_frm_max_14day FLOAT;
ALD2: Insert definition
  --INSERT INTO exposure_list (variable, description, units, utc_min_date_time, utc_max_date_time, resolution, aggregation) VALUES ('ald2', '1000.0*ALD2[1]', 'ppbV', '2011-01-01 01:00:00', '2011-02-01 01:00:00', 'hour;day;7day;14day', 'max;avg');
...
PM25_FRM: Insert definition
  --INSERT INTO exposure_list (variable, description, units, utc_min_date_time, utc_max_date_time, resolution, aggregation) VALUES ('pm25_frm', 'PM25_TOT[0]-(PM25_NO3_loss[0]+PM25_NH4_loss[0])+0.24*(PM25_SO4[0]+PM25_NH4[0]-PM', 'ug/m3', '2011-01-01 01:00:00', '2011-02-01 01:00:00', 'hour;day;7day;14day', 'max;avg');
```

The database tables will now reflect the updates based on the parameters discovered in the data file.

```
$ docker exec -u postgres database psql -d cmaq -c "select * from exposure_list limit 10;"
 id |   variable    |           description           | units | common_name |  utc_min_date_time  |  utc_max_date_time  |     resolution      | aggregation
----+-----------+---------------------------------+-------+-------------+---------------------+---------------------+---------------------+-------------
  1 | ald2      | 1000.0*ALD2[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  2 | aldx      | 1000.0*ALDX[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  3 | benzene   | 1000.0*BENZENE[1]               | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  4 | co        | 1000.0*CO[1]                    | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  5 | eth       | 1000.0*ETH[1]                   | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  6 | etha      | 1000.0*ETHA[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  7 | form      | 1000.0*FORM[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  8 | h2o2      | 1000.0*H2O2[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
  9 | hno3      | 1000.0*HNO3[1]                  | ppbV  |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
 10 | hno3_ugm3 | 1000.0*(HNO3[1]*2.1756*DENS[3]) | ug/m3 |             | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
(10 rows)
```

The pre-ingest check should be run on each CMAQ source data file prior to it's ingestion.

### Update common_name

The source CMAQ files abbreviate the exposure names and don't contain a common name for the abbreviation. The python script named `update-common-name.py` checks the contents of the database against a file named `exposure_list.csv` from the repository and updates the database accordingly.

The user should update the `common_name` column directly in the `exposure_list.csv` file. If a particular exposure variable has more than one common name, they should be separated by a semicolon `;`

- Example `exposure_list.csv`:

	```
	id,variable,description,units,common_name,utc_min_date_time,utc_max_date_time,resolution,aggregation
	...
	23,o3,1000.0*O3[1],ppbV,Ozone;O3,2010-01-01 00:00:00,2012-01-01 01:00:00,hour;day;7day;14day,max;avg
	...
	```

Usage: `$ python update-common-name.py /PATH_TO/cmaq-exposure-api/data-sample/data/exposure_list.csv`

- Example:

	```
	$ python update-common-name.py /PATH_TO/cmaq-exposure-api/data-sample/data/exposure_list.csv
	UPDATE: exposure_list common_name
	  --UPDATE exposure_list SET common_name = 'Acetaldehyde' WHERE variable = 'ald2' ;
	  --UPDATE exposure_list SET common_name = 'Higher Aldehydes' WHERE variable = 'aldx' ;
	  --UPDATE exposure_list SET common_name = 'Formaldehyde' WHERE variable = 'form' ;
	  --UPDATE exposure_list SET common_name = 'Ozone;O3' WHERE variable = 'o3' ;
	  --UPDATE exposure_list SET common_name = 'Particulate Matter 2.5' WHERE variable = 'pmij' ;
	```

- Results in:

	```
	$ docker exec -u postgres database psql -d cmaq -c "select * from exposure_list where common_name is not null order by variable;"
	 id | variable |    description    | units |      common_name       |  utc_min_date_time  |  utc_max_date_time  |     resolution      | aggregation
	----+------+-------------------+-------+------------------------+---------------------+---------------------+---------------------+-------------
	  1 | ald2 | 1000.0*ALD2[1]    | ppbV  | Acetaldehyde           | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
	  2 | aldx | 1000.0*ALDX[1]    | ppbV  | Higher Aldehydes       | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
	  7 | form | 1000.0*FORM[1]    | ppbV  | Formaldehyde           | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
	 27 | o3   | 1000.0*O3[1]      | ppbV  | Ozone;O3               | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
	 73 | pmij | ATOTI[0]+ATOTJ[0] | ug/m3 | Particulate Matter 2.5 | 2011-01-01 01:00:00 | 2011-02-01 01:00:00 | hour;day;7day;14day | max;avg
	(5 rows)
	```

## ingest

TODO

## postgres-functions

Functions and indexes are to be loaded by the `postgres` user directly on the `cmaq` database from the `psql` prompt.

In the docker development environment, this can be achieved by attaching to the `database` container as user `postgres`:

```
$ docker exec -ti -u postgres database psql -d cmaq
psql (9.6.6)
Type "help" for help.

cmaq=#
```

In production, the user would generally `sudo su - postgres` to become the postgres user on the system, and then issue the `psql` call.

```
$ sudo su - postgres
Last login: Mon Nov 27 15:18:24 EST 2017 on pts/1
-bash-4.2$ psql -d cmaq
psql (9.6.6)
Type "help" for help.

cmaq=#
```

### Indexes

Indexes are defined in the `indexes.sql` file. They should be applied as copy/paste from the `psql` prompt of the `cmaq` database.

```
psql (9.6.6)
Type "help" for help.

cmaq=# -- index over col, row and utc_date_time
cmaq=# DROP INDEX exposure_col_row_date;
ERROR:  index "exposure_col_row_date" does not exist
cmaq=# CREATE UNIQUE INDEX CONCURRENTLY exposure_col_row_date
cmaq-#   ON exposure_data(col, row, utc_date_time);
CREATE INDEX
cmaq=#
cmaq=# -- index over utc_date_time
cmaq=# DROP INDEX exposure_date;
ERROR:  index "exposure_date" does not exist
cmaq=# CREATE INDEX CONCURRENTLY exposure_date
cmaq-#   ON exposure_data(utc_date_time);
CREATE INDEX
```

The indexes should be reapplied any time new rows are added to the database. Updates to existing rows do not require any update to the indexes.

### Functions

Functions are generated based on the data already contained within the database by the `generate-aggregation-functions.py` script. It is important to generate the functions after the data ingest has taken place or they may not be sufficient in scope.

Example:

```
$ cd /PATH_TO/cmaq-exposure-api/data-tools/postgres-functions
$ virtualenv -p /PATH_TO/python3 venv
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
(venv)$ python generate-aggregation-functions.py
```

New files of names `cmaq_variable_aggregates_YYYY.sql` should now exist where `YYYY` is the year of CMAQ data the function corresponds to. The generate function can be in excess of 1000+ lines which is expected.

Just as the indexes were, the entirety of any generated files should be inserted as copy/paste from the `psql` prompt of the `cmaq` database.

On success the user will get a `CREATE FUNCTION` response if all went well. Once completed the functions will appear from a `\df` call.

```
cmaq=# \df cmaq*;
                                                              List of functions
 Schema |             Name              | Result data type |                          Argument data types                           |  Type
--------+-------------------------------+------------------+------------------------------------------------------------------------+--------
 public | cmaq_variable_aggregates_2010 | void             | _date text, _minr integer, _maxr integer, _minc integer, _maxc integer | normal
 public | cmaq_variable_aggregates_2011 | void             | _date text, _minr integer, _maxr integer, _minc integer, _maxc integer | normal
(2 rows)
```


## post-ingest

**NOTE**: PostgreSQL Functions and Indexes must be in place prior to running the post ingest scripts.

The script named `update-variable-aggregates.py` will find all dates with missing aggregate data and attempt to populate them using the functions created by the `generate-aggregation-functions.py` script.

Default behavior is to expect the docker development database, but this can be overridden by using the `--postgres` modifier.

- `$ python update-variable-aggregates.py --postgres`

Example using docker development database:

```
(venv)$ python update-variable-aggregates.py
INFO: Using docker implementation for database
2010-07-01
docker exec -u postgres database psql -d cmaq -c "SELECT * FROM cmaq_variable_aggregates_2010('2010-07-01', 33, 33, 105, 105);"
 cmaq_variable_aggregates_2010
-------------------------------

(1 row)
...
```

Once completed all aggregate data should be populated.