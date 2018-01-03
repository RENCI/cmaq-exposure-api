from configparser import ConfigParser
import psycopg2
import sys

dbcfg = ConfigParser()
dbcfg.read('../../config/database.ini')

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

sql = "SELECT MIN(EXTRACT(YEAR FROM utc_min_date_time)) FROM exposure_list;"
cur = conn.cursor()
cur.execute(sql)
min_yr = int(cur.fetchone()[0])

sql = "SELECT MAX(EXTRACT(YEAR FROM utc_max_date_time)) FROM exposure_list;"
cur.execute(sql)
max_yr = int(cur.fetchone()[0])

body_1 = "\tIN _date TEXT,\n" \
         "\tIN _minr INT,\n" \
         "\tIN _maxr INT,\n" \
         "\tIN _minc INT,\n" \
         "\tIN _maxc INT\n" \
         ")\n" \
         "RETURNS VOID\n" \
         "AS $$\n" \
         "\tDECLARE start_date TIMESTAMP;\n" \
         "\tDECLARE end_date TIMESTAMP;\n" \
         "\tDECLARE min_row INT;\n" \
         "\tDECLARE max_row INT;\n" \
         "\tDECLARE min_col INT;\n" \
         "\tDECLARE max_col INT;\n" \
         "BEGIN\n" \
         "\tstart_date := format('%s 00:00:00', _date);\n" \
         "\tend_date := format('%s 23:00:00', _date);\n" \
         "\tmin_row := _minr;\n" \
         "\tmax_row := _maxr;\n" \
         "\tmin_col := _minc;\n" \
         "\tmax_col := _maxc;\n" \
         "\tFOR r IN min_row..max_row LOOP\n" \
         "\t\tFOR c IN min_col..max_col LOOP\n" \
         "\t\t\tUPDATE exposure_data\n" \
         "\t\t\tSET\n"

body_4 = "\t\t\t\tFROM exposure_data cd\n" \
         "\t\t\t\tWHERE cd.row = r AND cd.col = c\n" \
         "\t\t\t\t\tAND cd.utc_date_time >= start_date\n" \
         "\t\t\t\t\tAND cd.utc_date_time <= end_date\n" \
         "\t\t\t\t) AS subquery\n" \
         "\t\t\tWHERE exposure_data.utc_date_time=subquery.utc_date_time\n" \
         "\t\t\t\tAND exposure_data.row=r\n" \
         "\t\t\t\tAND exposure_data.col=c\n" \
         "\t\t\t\tAND exposure_data.utc_date_time >= start_date\n" \
         "\t\t\t\tAND exposure_data.utc_date_time <= end_date;\n" \
         "\t\tEND LOOP;\n" \
         "\tEND LOOP;\n" \
         "END; $$\n" \
         "LANGUAGE plpgsql;"

var_suffix = ['_avg_24hr', '_max_24hr', '_avg_7day', '_max_7day', '_avg_14day', '_max_14day']

yr_dict = {}
for yr in range(min_yr, max_yr + 1, 1):
    yr_dict[yr] = []
    sql = "SELECT variable FROM exposure_list " \
          "WHERE '" + str(yr) + "' >= EXTRACT(YEAR FROM utc_min_date_time) AND " \
          "'" + str(yr) + "' <= EXTRACT(YEAR FROM utc_max_date_time) ORDER BY variable;"
    cur.execute(sql)
    for rec in cur:
        yr_dict[yr] += rec

    f = open('cmaq_variable_aggregates_' + str(yr) + '.sql', 'w')
    f.write("-- drop prior function if it exists\n" \
            "DROP FUNCTION IF EXISTS cmaq_variable_aggregates_" + str(yr) + "(TEXT);\n" \
            "\n" \
            "-- populate aggregates over give date\n" \
            "CREATE OR REPLACE FUNCTION cmaq_variable_aggregates_" + str(yr) + " (\n")
    f.write(body_1)
    body_2 = ''
    for var in yr_dict[yr]:
        for suf in var_suffix:
            body_2 += '\t\t\t\t' + var + suf + '=subquery.' + var + suf + ',\n'
    f.write(body_2[:-2] + '\n')
    f.write("\t\t\tFROM (\n" \
            "\t\t\t\tSELECT cd.utc_date_time,\n")
    body_3 = ''
    for var in yr_dict[yr]:
        body_3 += "\t\t\t\t\tavg(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_avg_24hr,\n" \
                  "\t\t\t\t\tmax(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_max_24hr,\n" \
                  "\t\t\t\t\tavg(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 167 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_avg_7day,\n" \
                  "\t\t\t\t\tmax(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 167 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_max_7day,\n" \
                  "\t\t\t\t\tavg(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 335 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_avg_14day,\n" \
                  "\t\t\t\t\tmax(cd." + var + ")\n" \
                  "\t\t\t\t\t\tOVER (ORDER BY cd.utc_date_time ROWS BETWEEN 335 PRECEDING AND CURRENT ROW) " \
                  "AS " + var + "_max_14day,\n" \

    f.write(body_3[:-2] + '\n')
    f.write(body_4)
    f.close()