import sys
from configparser import ConfigParser
from datetime import datetime, timedelta
from netCDF4 import Dataset

import psycopg2

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

for key in dskeys:
    sql = "SELECT column_name " \
          "FROM information_schema.columns " \
          "WHERE table_name='exposure_data' " \
          "and column_name='" + key.lower() + "';"
    cur = conn.cursor()
    cur.execute(sql)
    if not cur.fetchall() and key != 'TFLAG':
        print(key + ': Adding columns')
        newcols = (key.lower(),
                   key.lower() + '_avg_24hr',
                   key.lower() + '_max_24hr',
                   key.lower() + '_avg_7day',
                   key.lower() + '_max_7day',
                   key.lower() + '_avg_14day',
                   key.lower() + '_max_14day')
        sql_add = ''
        for row in newcols:
            sql_add = sql_add + "ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS " + row + " FLOAT;"
            print("  -- ALTER TABLE exposure_data ADD COLUMN IF NOT EXISTS " + row + " FLOAT;")
        cur = conn.cursor()
        cur.execute(sql_add)
        conn.commit()
        cur.close()
    else:
        print(key + ': Already defined')

tstep = datetime.strptime(str(getattr(ds, 'TSTEP')).zfill(6), "%H%M%S")
delta = timedelta(hours=tstep.hour, minutes=tstep.minute, seconds=tstep.second)
utc_start_date = datetime.strptime(str(getattr(ds, 'SDATE')) + ' ' +
                                   str(getattr(ds, 'STIME')).zfill(6), "%Y%j %H%M%S")
utc_end_date = utc_start_date + (int(ds.dimensions['TSTEP'].size) * delta)

for key in dskeys:
    sql = "SELECT variable " \
          "FROM exposure_list " \
          "WHERE variable='" + key.lower() + "';"
    cur = conn.cursor()
    cur.execute(sql)
    if not cur.fetchall() and key != 'TFLAG':
        print(key + ': Insert definition')
        sql_add = "INSERT INTO exposure_list " \
                  "(variable, description, units, utc_min_date_time, utc_max_date_time, resolution, aggregation) " \
                  "VALUES ('" + str(ds.variables[key].long_name.lower()).strip() + "', '" + \
                  str(ds.variables[key].var_desc).strip() + "', '" + str(ds.variables[key].units).strip() + \
                  "', '" + str(utc_start_date) + "', '" + str(utc_end_date) + \
                  "', 'hour;day;7day;14day', 'max;avg');"
        print('  --' + sql_add)
        cur = conn.cursor()
        cur.execute(sql_add)
        conn.commit()
        cur.close()
    elif key != 'TFLAG':
        sql_date = "SELECT utc_min_date_time, utc_max_date_time " \
                   "FROM exposure_list " \
                   "WHERE variable='" + key.lower() + "';"
        cur = conn.cursor()
        cur.execute(sql_date)
        sd, ed = cur.fetchone()
        if utc_start_date < sd or utc_end_date > ed:
            print(key + ': Update definition')
            sql_update = ''
            if utc_start_date < sd:
                sql_update = sql_update + "UPDATE exposure_list SET utc_min_date_time = '" + \
                             str(utc_start_date) + "' WHERE variable='" + key.lower() + "';"

            if utc_end_date > ed:
                sql_update = sql_update + "UPDATE exposure_list SET utc_max_date_time = '" + \
                             str(utc_end_date) + "' WHERE variable='" + key.lower() + "';"

            print('  --' + sql_update)
            cur.execute(sql_update)
            conn.commit()
        cur.close()

conn.close()
