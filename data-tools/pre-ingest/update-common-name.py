from configparser import ConfigParser
import psycopg2
import sys
import csv

dbcfg = ConfigParser()
dbcfg.read('/PATH_TO/cmaq-exposure-api/config/database.ini')

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

with open(file_name) as f:
    print("UPDATE: exposure_list, SET: common_name")
    reader = csv.DictReader(f)
    for row in reader:
        sql = "SELECT * from exposure_list " \
              "WHERE variable = '" + row['variable'] + "';"
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchone()
        if res is not None:
            if row['common_name'] and not (res[4] == row['common_name']):
                sql_update = "UPDATE exposure_list " \
                             "SET common_name = '" + row['common_name'] + "' " \
                             "WHERE variable = '" + row['variable'] + "' ;"
                print('  --' + sql_update)
                cur.execute(sql_update)
                conn.commit()
        cur.close()

conn.close()
