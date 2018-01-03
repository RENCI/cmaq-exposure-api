import csv
import sys
from configparser import ConfigParser

import psycopg2

dbcfg = ConfigParser()
dbcfg.read('../../config/database.ini')

try:
    file_name = sys.argv[1]
except Exception as e:
    print('Usage: python update-quality-metrics-tables.py FILENAME')
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

# generate columns quality_metrics_list and populate rows
with open(file_name) as f:
    reader = csv.DictReader(f)
    for row in reader:
        sql = "SELECT * FROM quality_metrics_list WHERE variable = '" + str(row['VARNAME']).lower() + "';"
        cur = conn.cursor()
        cur.execute(sql)
        if not cur.fetchall():
            print('Adding row for quality_metrics_list::variable: ' + str(row['VARNAME']).lower())
            sql_stmt = "INSERT INTO quality_metrics_list " \
                       "(VARIABLE, common_name) " \
                       "VALUES ('" + str(row['VARNAME']).lower() + "', '" \
                       + str(row['COMMON NAME']).lower() + "');"
            print(' -- ' + sql_stmt)
            cur.execute(sql_stmt)
            conn.commit()
        cur.close()

sql = "SELECT variable FROM exposure_list;"
cur = conn.cursor()
cur.execute(sql)
variables = cur.fetchall()
dq_vars = []
for var in variables:
    dq_vars.append(str(var[0]))
    # if exposure_list doesn't have the has_quality_metric column, add it and default to FALSE
    sql = "SELECT column_name " \
          "FROM information_schema.columns " \
          "WHERE table_name='quality_metrics_list' " \
          "and column_name='" + str(var[0]) + "';"
    cur = conn.cursor()
    cur.execute(sql)
    if not cur.fetchall():
        print('Adding column: ' + str(var[0]))
        sql_add = "ALTER TABLE quality_metrics_list " \
                  "ADD COLUMN IF NOT EXISTS " + str(var[0]) + " BOOLEAN DEFAULT FALSE;"
        print('  -- ' + sql_add)
        cur = conn.cursor()
        cur.execute(sql_add)
        conn.commit()
        cur.close()
    else:
        print(str(var[0]) + ': Already defined')

# generate columns for quality_metrics_data based on email from Sarav
# NOT full set due to 1600 column limit in PostgreSQL
# Ref: http://nerderati.com/2017/01/03/postgresql-tables-can-have-at-most-1600-columns/
dq_vars = ['O3',
           'AALJ',
           'ACAJ',
           'ACAK',
           'AECIJ',
           'AFEJ',
           'AKJ',
           'AKK',
           'ALD2',
           'AMGJ',
           'AMGK',
           'AMNJ',
           'ANAIJ',
           'ANAK',
           'ANCOMIJ',
           'ANH4IJ',
           'ANO3IJ',
           'AOCIJ',
           'AOMIJ',
           'ASIJ',
           'ATIJ',
           'AUNCSPEC1IJ',
           'AUNSPEC2IJ',
           'ASO4IJ',
           'ASOILJ',
           'BENZENE',
           'CO',
           'ETH',
           'ETHA',
           'FORM',
           'HNO3',
           'ISOP',
           'NH3',
           'NO',
           'NO2',
           'NOY',
           'PM10',
           'PM25_EC',
           'PM25_FRM',
           'PM25_NA',
           'PM25_NH4',
           'PM25_NO3',
           'PM25_OC',
           'PM25_SO4',
           'PM25_TOT',
           'PMIJ',
           'PMIJ_FRM',
           'RH',
           'SFC_TEMP',
           'SO2',
           'TOL',
           'TNO3',
           'XYL']

sql = "SELECT variable FROM quality_metrics_list;"
cur = conn.cursor()
cur.execute(sql)
variables = cur.fetchall()
dq_metrics = []
for var in variables:
    dq_metrics.append(str(var[0]))

for var in dq_vars:
    for metric in dq_metrics:
        col_name = var.lower() + '_' + metric
        sql = "SELECT column_name " \
              "FROM information_schema.columns " \
              "WHERE table_name='quality_metrics_data' " \
              "and column_name='" + col_name + "';"
        cur = conn.cursor()
        cur.execute(sql)
        if not cur.fetchall():
            print('Adding column: ' + col_name)
            sql_add = "ALTER TABLE quality_metrics_data ADD COLUMN IF NOT EXISTS " + col_name + " FLOAT;"
            print('  -- ' + sql_add)
            cur = conn.cursor()
            cur.execute(sql_add)
            conn.commit()
            cur.close()
        else:
            print(col_name + ': Already defined')

conn.close()
