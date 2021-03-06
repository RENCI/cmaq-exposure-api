#!/usr/bin/env python3

from configparser import ConfigParser
from gevent import monkey

import connexion
from flask_cors import CORS

monkey.patch_all()

if __name__ == '__main__':
    parser = ConfigParser()
    parser.read('ini/connexion.ini')
    if not parser.get('connexion', 'server'):
        app = connexion.App(__name__, specification_dir='./swagger/')
    else:
        app = connexion.App(__name__, specification_dir='./swagger/', server=parser.get('connexion', 'server'))
    app.add_api('swagger.yaml', arguments={'title': 'CMAQ Exposure API'})
    if not parser.get('connexion', 'certfile') or not parser.get('connexion', 'keyfile'):
        app.run(port=int(parser.get('connexion', 'port')),
                debug=parser.get('connexion', 'debug'))
    else:
        CORS(app.app)
        app.run(port=int(parser.get('connexion', 'port')),
                debug=parser.get('connexion', 'debug'),
                keyfile=parser.get('connexion', 'keyfile'),
                certfile=parser.get('connexion', 'certfile')
                )
