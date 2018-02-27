import datetime
import sys
from configparser import ConfigParser

import numpy as np
import pandas as pd
import psycopg2 as psql
import xarray as xr
import yaml
import io
import csv

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

# fix cvs header and add a "col" column
def fix_csv(csv_stream, col):

    new_csv = io.StringIO()
    writer = csv.writer(new_csv)

    reader = csv.reader((line.replace('\0','') for line in csv_stream), delimiter=',')
    line = 0;

    # fix cvs header
    row = reader.__next__()

    # insert "col" in header
    row.insert(0,"col")

    # change TSTEP to utc_data_time
    row[2] = "utc_date_time"

    # now make all the other vars lowercase
    for r in range(0, len(row)):
        row[r] = row[r].lower()
    hdr = row 
       
    writer.writerow(row)

    # for rest of rows, add a "col" column in the first position
    for row in reader:
        if '\0' in row: continue
        if not row: continue
        row.insert(0,str(col))
        writer.writerow(row)

    # reset stream to top
    new_csv.seek(0)
    return new_csv, hdr

# Main
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


# now go through dataset and get slice for each column
# to save in DB in bulk
total_rows = len(cols) * len(rows) * len(dates)
print("Found " + str(total_rows) + " rows of data to copy into " + table_name + " db table", end='\n', flush=True)

for col in cols.data:

    s_buf = io.StringIO()

    tmp_col_slice = ds.isel(COL=col, LAY=0)
    try:
        col_slice = tmp_col_slice.drop("TFLAG")
    except:
        # doesn't matter - ignore
        col_slice = tmp_col_slice

    # make rows start at 1 instead of 0
    col_slice.coords['ROW'] += 1

    # convert xarray Dataset to Pandas Datatframe
    # so we can use Dataframe to_csv() method
    # and write csv file to a streaming io buffer
    pd_df = col_slice.to_dataframe()
    pd_df.to_csv(s_buf)
    s_buf.seek(0)
    new_csv, hdr = fix_csv(s_buf, col+1)
    hdr_str = ','.join(hdr)

    sql_copy_statement = "COPY {table} ({header}) FROM STDIN WITH CSV HEADER;".format(table = table_name, header=hdr_str)

    cur = conn.cursor()
    cur.copy_expert(sql_copy_statement, new_csv)
    db.commit()

    bulk_row_count = (len(rows) * len(dates))
    processed_rows = bulk_row_count * (col+1)
    print("Saved " + str(processed_rows) + " of " + str(total_rows) + " rows.", end='\n', flush=True)

    s_buf.close()
    new_csv.close()

print("Done!", end='\n', flush=True)
