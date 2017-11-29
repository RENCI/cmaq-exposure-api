-- index over col, row and utc_date_time
DROP INDEX exposure_col_row_date;
CREATE UNIQUE INDEX CONCURRENTLY exposure_col_row_date
  ON exposure_data(col, row, utc_date_time);

-- index over utc_date_time
DROP INDEX exposure_date;
CREATE INDEX CONCURRENTLY exposure_date
  ON exposure_data(utc_date_time);