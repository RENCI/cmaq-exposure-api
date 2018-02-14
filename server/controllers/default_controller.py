import sys
from configparser import ConfigParser
from sqlalchemy import exists, or_, func

from controllers import Session
from flask import jsonify
from models import ExposureList, QualityMetricsList

parser = ConfigParser()
parser.read('ini/connexion.ini')
sys.path.append(parser.get('sys-path', 'exposures'))
sys.path.append(parser.get('sys-path', 'controllers'))


def variables_get(search=None) -> str:
    session = Session()
    if search:
        search = search.lower()
        results = session.query(ExposureList).filter(or_(
            func.lower(ExposureList.variable).like(str('%' + search + '%')),
            func.lower(ExposureList.common_name).like(str('%' + search + '%')))).all()
    else:
        results = session.query(ExposureList).all()
    dq_set = {}
    for o in results:
        dq_set[o.variable] = []
        if o.has_quality_metric:
            dq_vars = session.query(QualityMetricsList.variable, QualityMetricsList.common_name).filter(
                getattr(QualityMetricsList, o.variable) == 't').all()
            for var in dq_vars:
                dq_set[o.variable].append({'variable': var[0], 'common_name': var[1]})

    data = jsonify({"cmaq": [dict(variable=o.variable,
                                  description=o.description,
                                  units=o.units,
                                  common_name=o.common_name,
                                  has_quality_metric=o.has_quality_metric,
                                  quality_metric=dq_set[o.variable],
                                  start_date=o.utc_min_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                  end_date=o.utc_max_date_time.strftime("%Y-%m-%d %H:%M:%S"),
                                  resolution=o.resolution.split(';'),
                                  aggregation=o.aggregation.split(';')) for o in results]})
    return data


def values_get(variable, start_date, end_date, lat_lon, resolution=None, aggregation=None, utc_offset=None, include_quality_metrics=None) -> str:
    session = Session()
    variable = "".join(variable.split()).lower()
    lat_lon = "".join(lat_lon.split())
    var_set = variable.split(';')
    for var in var_set:
        if not session.query(exists().where(ExposureList.variable == var)).scalar():
            return 'Invalid parameter', 400, {'x-error': 'Invalid parameter: variable'}
    session.close()
    from cmaq import CmaqExposures
    cmaq = CmaqExposures()
    kwargs = locals()
    data = cmaq.get_values(**kwargs)

    return data
