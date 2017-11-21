import sys
from datetime import datetime, timedelta
import pytz
from sqlalchemy import extract
from configparser import ConfigParser
from flask import jsonify
from models import ExposureDatum, ExposureList
from controllers import Session
from exposures.cmaq_utils import latlon2rowcol

parser = ConfigParser()
parser.read('ini/connexion.ini')
sys.path.append(parser.get('sys-path', 'exposures'))
sys.path.append(parser.get('sys-path', 'controllers'))


class CmaqExposures(object):

    def is_valid_date_range(self, **kwargs):
        session = Session()
        min_date = session.query(ExposureList.utc_min_date_time).filter(
            ExposureList.variable == kwargs.get('variable')).one()
        max_date = session.query(ExposureList.utc_max_date_time).filter(
            ExposureList.variable == kwargs.get('variable')).one()
        session.close()
        if min_date[0].date() > datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d").date():
            return False
        elif max_date[0].date() < datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d").date():
            return False
        elif datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d").date() > \
                datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d").date():
            return False
        else:
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
        res = session.query(ExposureList.resolution).filter(
            ExposureList.variable == kwargs.get('variable')).one()
        session.close()
        for item in res:
            res_set.update(item.split(';'))
        if kwargs.get('resolution') in res_set:
            return True
        else:
            return False

    def is_valid_aggregation(self, **kwargs):
        agg_set = set()
        session = Session()
        agg = session.query(ExposureList.aggregation).filter(
            ExposureList.variable == kwargs.get('variable')).one()
        session.close()
        for item in agg:
            agg_set.update(item.split(';'))
        if kwargs.get('aggregation') in agg_set:
            return True
        else:
            return False

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
        # determine exposure type to query
        exposure = kwargs.get('variable')
        # set resolution and aggregate to query
        if kwargs.get('resolution') == 'day':
            exposure += '_' + kwargs.get('aggregation') + '_24hr'
        elif kwargs.get('resolution') == '7day':
            exposure += '_' + kwargs.get('aggregation') + '_7day'
        elif kwargs.get('resolution') == '14day':
            exposure += '_' + kwargs.get('aggregation') + '_14day'
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
        # retrieve query result for each lat,lon pair and add to data object
        lat_lon_set = kwargs.get('lat_lon').split(';')
        for lat_lon in lat_lon_set:
            coords = lat_lon.split(',')
            row, col = latlon2rowcol(coords[0], coords[1], str(start_time.year))
            session = Session()
            if kwargs.get('resolution') == 'hour':
                # hourly resolution of data - return all hours for date range
                query = session.query(ExposureDatum.id,
                                      ExposureDatum.utc_date_time,
                                      getattr(ExposureDatum, exposure)). \
                    filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)). \
                    filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)). \
                    filter(ExposureDatum.row == row). \
                    filter(ExposureDatum.col == col)
            else:
                # daily resolution of data - return only matched hours for date range
                query = session.query(ExposureDatum.id,
                                      ExposureDatum.utc_date_time,
                                      getattr(ExposureDatum, exposure)).\
                    filter(ExposureDatum.utc_date_time >= start_time + timedelta(hours=utc_offset)).\
                    filter(ExposureDatum.utc_date_time <= end_time + timedelta(hours=utc_offset)).\
                    filter(ExposureDatum.row == row).\
                    filter(ExposureDatum.col == col).\
                    filter(extract('hour', ExposureDatum.utc_date_time) == utc_offset)
            session.close()
            # add query output to data object in JSON structured format
            for cmaq_id, cmaq_date_time, cmaq_exp in query:
                # print(cmaq_id, cmaq_date_time, cmaq_exp)
                data['values'].append({'date_time': cmaq_date_time,
                                       'lat_lon': lat_lon,
                                       'value': str(cmaq_exp)})
        return jsonify(data)
