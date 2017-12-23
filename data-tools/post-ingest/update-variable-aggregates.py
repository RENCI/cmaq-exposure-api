import subprocess
import sys
from configparser import ConfigParser

import psycopg2

dbcfg = ConfigParser()
dbcfg.read('../../config/database.ini')

try:
    if sys.argv[1] == '--postgres':
        flag = True
except Exception as e:
    print('INFO: Using docker implementation for database')
    flag = False
    pass

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

# get minimum year from dataset
sql = "SELECT MIN(EXTRACT(YEAR FROM utc_min_date_time)) FROM exposure_list;"
cur = conn.cursor()
cur.execute(sql)
min_yr = int(cur.fetchone()[0])

# get maximum year from dataset
sql = "SELECT MAX(EXTRACT(YEAR FROM utc_max_date_time)) FROM exposure_list;"
cur.execute(sql)
max_yr = int(cur.fetchone()[0])

# generate variable dictionary for each year in dataset
yr_dict = {}
for yr in range(min_yr, max_yr + 1, 1):
    yr_dict[yr] = []
    sql = "SELECT variable FROM exposure_list " \
          "WHERE '" + str(yr) + "' >= EXTRACT(YEAR FROM utc_min_date_time) AND " \
                                "'" + str(yr) + "' <= EXTRACT(YEAR FROM utc_max_date_time) ORDER BY variable;"
    cur.execute(sql)
    for rec in cur:
        yr_dict[yr] += rec

# find all days without aggregate values for variables in that year - use _avg_24hr as test
for yr in yr_dict:
    big_or = '('
    for var in yr_dict[yr]:
        big_or += var + '_avg_24hr is null or '
    sql = "SELECT DISTINCT (utc_date_time::date) FROM exposure_data " \
          "WHERE EXTRACT(YEAR FROM utc_date_time) = '" + str(yr) + \
          "' AND " + big_or[:-4] + ") ORDER BY utc_date_time;"
    cur.execute(sql)
    res = cur.fetchall()
    # get min_row, max_row, min_col, max_col for given year
    sql = "SELECT MIN(row) FROM exposure_data where EXTRACT(YEAR FROM utc_date_time) = '" + str(yr) + "';"
    cur.execute(sql)
    min_row = int(cur.fetchone()[0])
    sql = "SELECT MAX(row) FROM exposure_data where EXTRACT(YEAR FROM utc_date_time) = '" + str(yr) + "';"
    cur.execute(sql)
    max_row = int(cur.fetchone()[0])
    sql = "SELECT MIN(col) FROM exposure_data where EXTRACT(YEAR FROM utc_date_time) = '" + str(yr) + "';"
    cur.execute(sql)
    min_col = int(cur.fetchone()[0])
    sql = "SELECT MAX(col) FROM exposure_data where EXTRACT(YEAR FROM utc_date_time) = '" + str(yr) + "';"
    cur.execute(sql)
    max_col = int(cur.fetchone()[0])
    # calculate variable aggregates for each date that has missing data
    for dt in res:
        print(dt[0].strftime("%Y-%m-%d") + ':')
        if flag:
            # run on system
            syscall = "$ psql -d cmaq -c \"SELECT * FROM cmaq_variable_aggregates_" \
                      + str(yr) + "('" + dt[0].strftime("%Y-%m-%d") + "', " + str(min_row) + ", " + str(max_row) \
                      + ", " + str(min_col) + ", " + str(max_col) + ");\""
            print(syscall)
            subprocess.run(["psql", "-d", "cmaq", "-c",
                            "SELECT * FROM cmaq_variable_aggregates_" + str(yr) + "('" + dt[0].strftime(
                                "%Y-%m-%d") + "', " + str(min_row) + ", " + str(max_row)
                            + ", " + str(min_col) + ", " + str(max_col) + ");"])
        else:
            # run in docker development database
            syscall = "$ docker exec -u postgres database psql -d cmaq -c \"SELECT * FROM cmaq_variable_aggregates_" \
                      + str(yr) + "('" + dt[0].strftime("%Y-%m-%d") + "', " + str(min_row) + ", " + str(max_row) \
                      + ", " + str(min_col) + ", " + str(max_col) + ");\""
            print(syscall)
            subprocess.run(["docker", "exec", "-u", "postgres", "database", "psql", "-d", "cmaq", "-c",
                            "SELECT * FROM cmaq_variable_aggregates_" + str(yr) + "('" + dt[0].strftime(
                                "%Y-%m-%d") + "', " + str(min_row) + ", " + str(max_row)
                            + ", " + str(min_col) + ", " + str(max_col) + ");"])
