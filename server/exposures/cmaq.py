import sys
from configparser import ConfigParser
from datetime import datetime, timedelta
from sqlalchemy import extract

import pytz
from controllers import Session
from exposures.cmaq_utils import latlon2rowcol
from flask import jsonify
from models import ExposureDatum, ExposureList, QualityMetricsList, QualityMetricsDatum

parser = ConfigParser()
parser.read('ini/connexion.ini')
sys.path.append(parser.get('sys-path', 'exposures'))
sys.path.append(parser.get('sys-path', 'controllers'))


class CmaqExposures(object):
    def is_valid_date_range(self, **kwargs):
        session = Session()
        var_set = kwargs.get('variable').split(';')
        for var in var_set:
            min_date = session.query(ExposureList.utc_min_date_time).filter(
                ExposureList.variable == var).one()
            max_date = session.query(ExposureList.utc_max_date_time).filter(
                ExposureList.variable == var).one()
            session.close()
            if min_date[0].date() > datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d").date():
                return False
            elif max_date[0].date() < datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d").date():
                return False
            elif datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d").date() > \
                    datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d").date():
                return False

        return True

    def is_valid_lat_lon(self, **kwargs):
        # lat: 0 to +/- 90, lon: 0 to +/- 180 as lat,lon
        import re
        lat_lon = kwargs.get('lat_lon')
        for item in lat_lon.split(';'):
            if re.match(r'^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$',
                        item) is None:
                return False
        return True

    def is_valid_resolution(self, **kwargs):
        res_set = set()
        session = Session()
        var_set = kwargs.get('variable').split(';')
        for var in var_set:
            res = session.query(ExposureList.resolution).filter(
                ExposureList.variable == var).one()
            session.close()
            for item in res:
                res_set.update(item.split(';'))
            if kwargs.get('resolution') not in res_set:
                return False

        return True

    def is_valid_aggregation(self, **kwargs):
        agg_set = set()
        session = Session()
        var_set = kwargs.get('variable').split(';')
        for var in var_set:
            agg = session.query(ExposureList.aggregation).filter(
                ExposureList.variable == var).one()
            session.close()
            for item in agg:
                agg_set.update(item.split(';'))
            if kwargs.get('aggregation') not in agg_set:
                return False

        return True

    def is_valid_utc_offset(self, **kwargs):
        off_set = {'utc', 'eastern', 'central', 'mountain', 'pacific'}
        if kwargs.get('utc_offset') in off_set:
            return True
        else:
            return False

    def validate_parameters(self, **kwargs):
        if not self.is_valid_date_range(**kwargs):
            return False, ('Invalid parameter', 400, {'x-error': 'Invalid parameter: start_date, end_date'})
        elif not self.is_valid_lat_lon(**kwargs):
            return False, ('Invalid parameter', 400, {'x-error': 'Invalid parameter: lat_lon'})
        elif not self.is_valid_resolution(**kwargs):
            return False, ('Invalid parameter', 400, {'x-error': 'Invalid parameter: resolution'})
        elif not self.is_valid_aggregation(**kwargs):
            return False, ('Invalid parameter', 400, {'x-error': 'Invalid parameter: aggregation'})
        elif not self.is_valid_utc_offset(**kwargs):
            return False, ('Invalid parameter', 400, {'x-error': 'Invalid parameter: utc_offset'})
        else:
            return True, ''

    def get_values(self, **kwargs):
        # variable, start_date, end_date, lat_lon, resolution = None, aggregation = None, utc_offset = None
        # 'UTC', 'US/Central', 'US/Eastern','US/Mountain', 'US/Pacific'
        tzone_dict = {'utc': 'UTC',
                      'eastern': 'US/Eastern',
                      'central': 'US/Central',
                      'mountain': 'US/Mountain',
                      'pacific': 'US/Pacific'}
        # validate input from user
        is_valid, message = self.validate_parameters(**kwargs)
        if not is_valid:
            return message
        # create data object
        data = {}
        data['values'] = []
        # set UTC offset as time zone parameter for query
        dt = datetime.now()
        utc_offset = int(str(pytz.timezone(tzone_dict.get(kwargs.get('utc_offset'))).localize(dt)
                             - pytz.utc.localize(dt)).split(':')[0])
        # datetime objects for query and output adjustment
        start_time = datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d")
        end_time = datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d") + timedelta(hours=23)
        if start_time.year == end_time.year:
            year_set = [(start_time, end_time)]
        else:
            s_time = start_time
            e_time = end_time
            yr_range = range(s_time.year, e_time.year + 1, 1)
            year_set = []
            for yr in yr_range:
                if datetime(yr, 1, 1, 0, 0) <= s_time:
                    start_time = s_time
                else:
                    start_time = datetime(yr, 1, 1, 0, 0)
                if datetime(yr, 12, 31, 23, 0) >= e_time:
                    end_time = e_time
                else:
                    end_time = datetime(yr, 12, 31, 23, 0)
                year_set += [(start_time, end_time)]
        # retrieve query result for each lat,lon pair and add to data object
        lat_lon_set = kwargs.get('lat_lon').split(';')
        var_set = kwargs.get('variable').split(';')
        for lat_lon in lat_lon_set:
            coords = lat_lon.split(',')
            for var in var_set:
                # determine exposure type to query
                cmaq_output = []
                for years in year_set:
                    start_time = years[0]
                    end_time = years[1]
                    row, col = latlon2rowcol(coords[0], coords[1], str(start_time.year))
                    # set resolution and aggregate to query
                    exposure = var
                    if kwargs.get('resolution') == 'day':
                        exposure += '_' + kwargs.get('aggregation') + '_24hr'
                    elif kwargs.get('resolution') == '7day':
                        exposure += '_' + kwargs.get('aggregation') + '_7day'
                    elif kwargs.get('resolution') == '14day':
                        exposure += '_' + kwargs.get('aggregation') + '_14day'
                    session = Session()

                    if kwargs.get('include_quality_metrics') == True:
                        has_quality_metric = session.query(ExposureList.has_quality_metric).filter(
                            ExposureList.variable == var).scalar()
                        if has_quality_metric:
                            dq_vars = [r.variable for r in session.query(QualityMetricsList.variable). \
                                filter(getattr(QualityMetricsList, var) == 't').all()]
                            ret_vars = []
                            for r in dq_vars:
                                ret_vars.append(var + '_' + r)
                    else:
                        has_quality_metric = False

                    if kwargs.get('resolution') == 'hour':
                        # hourly resolution of data - return all hours for date range
                        if has_quality_metric:
                            query = session.query(ExposureDatum.id,
                                              ExposureDatum.utc_date_time,
                                              getattr(ExposureDatum, exposure), 
                                              *ret_vars). \
                                outerjoin(QualityMetricsDatum, ExposureDatum.utc_date_time==QualityMetricsDatum.utc_date_time). \
                                filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.row == row). \
                                filter(ExposureDatum.col == col)
                        else:
                            query = session.query(ExposureDatum.id,
                                              ExposureDatum.utc_date_time,
                                              getattr(ExposureDatum, exposure)). \
                                filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.row == row). \
                                filter(ExposureDatum.col == col)
                    else:
                        # daily resolution of data - return only matched hours for date range
                        if has_quality_metric:
                            query = session.query(ExposureDatum.id,
                                              ExposureDatum.utc_date_time,
                                              getattr(ExposureDatum, exposure),
                                              *ret_vars). \
                                outerjoin(QualityMetricsDatum, ExposureDatum.utc_date_time==QualityMetricsDatum.utc_date_time). \
                                filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.row == row). \
                                filter(ExposureDatum.col == col). \
                                filter(extract('hour', ExposureDatum.utc_date_time) == utc_offset)
                        else:
                            query = session.query(ExposureDatum.id,
                                              ExposureDatum.utc_date_time,
                                              getattr(ExposureDatum, exposure)). \
                                filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)). \
                                filter(ExposureDatum.row == row). \
                                filter(ExposureDatum.col == col). \
                                filter(extract('hour', ExposureDatum.utc_date_time) == utc_offset)

                    # add query output to data object in JSON structured format
                    quality_metric_values=[]
                    for query_return_values in query:
                        if has_quality_metric and len(query_return_values) > 3 :
                            keys = dq_vars
                            values = query_return_values[3:]
                            quality_metric = dict(zip(keys, values))
                            cmaq_output.append({'date_time': query_return_values[1].strftime("%Y-%m-%d %H:%M:%S"),
                                                'value': float(query_return_values[2]),
                                                'quality_metric': quality_metric})
                        else:
                            cmaq_output.append({'date_time': query_return_values[1].strftime("%Y-%m-%d %H:%M:%S"),
                                                'value': float(query_return_values[2])})
                    session.close()
                data['values'].append({'variable': var,
                                       'lat_lon': lat_lon,
                                       'cmaq_output': cmaq_output})
        return jsonify(data)
