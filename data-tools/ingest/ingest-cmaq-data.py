from netCDF4 import Dataset
from configparser import ConfigParser
from datetime import datetime, timedelta
import psycopg2
import sys

dbcfg = ConfigParser()
dbcfg.read('../../config/database.ini')

try:
    file_name = sys.argv[1]
except Exception as e:
    print('Usage: python update-cmaq-tables.py FILENAME')
    print(e)
    sys.exit(1)

try:
    conn = psycopg2.connect("dbname='" + dbcfg.get('postgres', 'database') +
                            "' user='" + dbcfg.get('postgres', 'username') +
                            "' host='" + dbcfg.get('postgres', 'host') +
                            "' password='" + dbcfg.get('postgres', 'password') +
                            "' port='" + dbcfg.get('postgres', 'port') +
                            "'")
except psycopg2.OperationalError as e:
    print(e)
    sys.exit(1)

try:
    ds = Dataset(file_name, 'r')
except FileNotFoundError as e:
    print(e)
    sys.exit(1)

dskeys = ds.variables.keys()
rows = ds.dimensions['ROW'].size
cols = ds.dimensions['COL'].size
steps = ds.dimensions['TSTEP'].size

tstep = datetime.strptime(str(getattr(ds, 'TSTEP')).zfill(6), "%H%M%S")
delta = timedelta(hours=tstep.hour, minutes=tstep.minute, seconds=tstep.second)
utc_start_date = datetime.strptime(str(getattr(ds, 'SDATE')) + ' ' +
                                   str(getattr(ds, 'STIME')).zfill(6), "%Y%j %H%M%S")
utc_end_date = utc_start_date + (int(ds.dimensions['TSTEP'].size) * delta)

utc_date_time = utc_start_date

# Dimensions in data files
# float VarName(TSTEP, LAY, ROW, COL)
base_sql = "INSERT INTO exposure_data (utc_date_time, row, col, "
for key in dskeys:
    if key != 'TFLAG':
        base_sql += key + ", "
base_sql = base_sql[:-2] + ") VALUES ("

print('Insert data for:')
cur = conn.cursor()
for step in range(0, steps):
    print("  -- " + str(utc_date_time))
    for r in range(0, rows):
        for c in range(0, cols):
            sql = base_sql + "'" + str(utc_date_time) + "'" + ", " + str(r + 1) + ", " + str(c + 1) + ", "
            for key in dskeys:
                if key != 'TFLAG':
                    sql += str(ds.variables[key][step, 0, r, c]) + ", "
            sql = sql[:-2] + ");"
            cur.execute(sql)
            conn.commit()
    utc_date_time += delta

conn.close()
