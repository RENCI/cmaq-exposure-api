# used for development purposes
# only pulls data from rows/cols that reflect latitude,longitude = 35,-80

import datetime
import sys
from configparser import ConfigParser

import numpy as np
import pandas as pd
import psycopg2 as psql
import xarray as xr
import yaml

settings_file = "./netcdf2psqldb.yml"


class cmaq_db:
    def __init__(self):
        self.conn = None

        # open config file
        fd = open(settings_file)
        self.config = yaml.safe_load(fd)
        fd.close()

        db_ini_file = self.config['exposures-db-ini-file']
        self.table_name = self.config['exposures-db-table-name']

        config = ConfigParser()
        config.read(db_ini_file)

        self.host = config.get('postgres', 'host')
        self.port = config.get('postgres', 'port')
        self.dbname = config.get('postgres', 'database')
        self.user = config.get('postgres', 'username')
        self.password = config.get('postgres', 'password')

    def connect(self):
        self.conn = psql.connect(
            "host=" + self.host + " " +
            "port=" + self.port + " " +
            "user=" + self.user + " " +
            "password=" + self.password + " " +
            "dbname=" + self.dbname)

        return self.conn

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def get_table_name(self):
        return self.table_name


class cmaq_dataset:
    def __init__(self, file_name):
        # This string is and indicator of which variables
        # to process for a given CMAQ data year - it means
        # process all found in the netCDF data file
        # this is set in the yaml config file
        self.all_vars_str = "ALL_OF_THEM"

        self.filename = file_name

        # open config file
        fd = open(settings_file)
        self.config = yaml.safe_load(fd)
        fd.close()

    def get_dataset(self):
        ds = None
        ds = xr.open_dataset(self.filename, decode_coords=True)

        return ds

    # param 'year' is a string
    def get_datavars_by_year(self, year):
        variables = []
        config_year = self.config['cmaq' + year]

        # check to see if we are doing all or
        # a subset of variables
        variables = config_year['data-vars']

        if self.all_vars_str in variables:
            ds = self.get_dataset()
            variables = str(getattr(ds, 'VAR-LIST')).split()

        return variables


try:
    file_name = sys.argv[1]
    year = sys.argv[2]
except Exception:
    print('Usage: python ingest-cmaq-file.py NetCDF_FILENAME YEAR(format YYYY)')
    sys.exit(1)

cmaq_ds = cmaq_dataset(file_name)

# connect to DB and collect DB info
db = cmaq_db()
conn = db.connect()
table_name = db.get_table_name();

print("Reading data file: " + file_name, end='\n', flush=True)

# get data vars we are interested in - or all (set in yaml config)
variables = cmaq_ds.get_datavars_by_year(str(year))

print("Reading data file: " + file_name, end='\n', flush=True)
ds = cmaq_ds.get_dataset()
# make any changes needed in dataset
sdate = str(getattr(ds, 'SDATE'))
# :STIME is normally 10000 in CMAQ 2011 netcdf files
# representing HH:MM:SS
# not sure how else to do this this - but if hour is not zero padded
# cannot use datetime time formatting
# just handle hour based start dates for now
stime = getattr(ds, 'STIME')
hr = int(stime) / 10000
date_str = datetime.datetime.strptime(sdate, '%Y%j')

# add start hour
date_str = date_str + datetime.timedelta(hours=hr)
tstep_len = len(ds.coords['TSTEP'])
ds.coords['TSTEP'] = pd.date_range(date_str, freq='H', periods=tstep_len)

cols = ds.coords['COL']
rows = ds.coords['ROW']
dates = ds.coords['TSTEP']

if str(year) == '2010':
    yr_row = 36
    yr_col = 113
else:
    yr_row = 110
    yr_col = 341

# for every exposure variable in that year
# as configuered in yaml...
for col in cols.data:
    for row in rows.data:
        if row == yr_row and col == yr_col:
            # slice data for a day - includes all variables configured
            tmp_day_slice = ds.isel(COL=col, LAY=0, ROW=row)
            try:
                day_slice = tmp_day_slice.drop("TFLAG")
            except:
                # doesn't matter - ignore
                day_slice = tmp_day_slice

            var_str = ', '.join(variables)
            sql_str = 'INSERT INTO ' + table_name + ' (col, row, utc_date_time, ' + var_str + \
                      ') VALUES (%s, %s, %s, '

            for i in range(len(variables) - 1):
                sql_str += '%s, '
            sql_str += '%s)'

            # Go through each hour in this day slice to insert a row in the DB
            for i in range(tstep_len):
                hour_slice = day_slice.isel(TSTEP=i)

                # convert numpy date type to python native
                ns = 1e-9  # number of seconds in a nanosecond
                dts = datetime.datetime.utcfromtimestamp(dates[i].data.astype(int) * ns)

                sql_values = [np.asscalar(col) + 1, np.asscalar(row) + 1, dts]
                for var in variables:
                    var_value = hour_slice.data_vars[var].values.item(0)
                    sql_values.append(var_value)

                with conn:
                    with conn.cursor() as curs:
                        curs.execute(sql_str, sql_values)
                        db.commit()

db.close()
print("Done!", end='\n', flush=True)
