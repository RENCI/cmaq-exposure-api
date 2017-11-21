import sys
import importlib
from sqlalchemy import create_engine, exists, and_, or_
from models import ExposureDatum, ExposureList
from flask import jsonify
from configparser import ConfigParser
from controllers import Session

parser = ConfigParser()
parser.read('ini/connexion.ini')
sys.path.append(parser.get('sys-path', 'exposures'))
sys.path.append(parser.get('sys-path', 'controllers'))


def variables_get(search=None) -> str:
    session = Session()
    if search:
        results = session.query(ExposureList).filter(or_(ExposureList.variable.like(str('%' + search + '%')),
                                                         ExposureList.common_name.like(str('%' + search + '%')))).all()
    else:
        results = session.query(ExposureList).all()
    data = jsonify({"cmaq": [dict(variable=o.variable,
                                  description=o.description,
                                  units=o.units,
                                  common_name=o.common_name,
                                  start_date=o.utc_min_date_time,
                                  end_date=o.utc_max_date_time,
                                  resolution=o.resolution.split(';'),
                                  aggregation=o.aggregation.split(';')) for o in results]})
    return data


def values_get(variable, start_date, end_date, lat_lon, resolution = None, aggregation=None, utc_offset=None) -> str:
    session = Session()
    if not session.query(exists().where(ExposureList.variable == variable)).scalar():
        return 'Invalid parameter', 400, {'x-error': 'Invalid parameter: variable'}
    session.close()
    from cmaq import CmaqExposures
    cmaq = CmaqExposures()
    kwargs = locals()
    data = cmaq.get_values(**kwargs)

    return data
