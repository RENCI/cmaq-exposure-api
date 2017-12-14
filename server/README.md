# Swagger Enabled Flask Server

## Local Development

### Initial Setup

Applies when there are changes made to the database and a new **models.py** file needs to be generated, otherwise skip to [Local Environment](#localenv).

The **models.py** file is generated using [sqlacodegen](https://pypi.python.org/pypi/sqlacodegen)

Need to add import statement to `sqlacodegen/codegen.py`in order to account for [geoalchemy2](https://geoalchemy-2.readthedocs.io/en/latest/). The `codegen.py` file is part of the `sqlacodegen` package installed by pip.

From the top level of the repository:

```
$ cd server/
$ virtualenv -p /PATH_TO/python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

Assuming `venv` is the name of the virtualenv directory the `codegen.py` files will be at: `/cmaq-exposure-api/server/venv/lib/python3.6/site-packages/sqlacodegen/codegen.py`.

Update it as follows:

```python
from sqlalchemy.types import Boolean, String
import sqlalchemy
from geoalchemy2 import Geometry, Geography # <-- this line
```

From the terminal generate the `models.py` file.

```
$ sqlacodegen --outfile models.py postgres://datatrans:datatrans@POSTGRES_DB_IP:5432/cmaq
```
Where `POSTGRES_DB_IP` is the actual IP of the database.

Update the generated `models.py` file with appropriate imports.

```
from sqlalchemy.dialects.postgresql import TEXT, DOUBLE_PRECISION
```

###  <a name="localenv"></a>Local Environment

From the top level of the repository:

```
$ cd server/
$ virtualenv -p /PATH_TO/python3 venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

**ini/connexion.ini**

Set up the `ini/connexion.ini` file to match your environment. An example file named `ini/connexion.ini.example` has been provided as a template.

```
$ cp ini/connexion.ini.example ini/connexion.ini
```

- If using the docker based database update the `FQDN_OR_IP` to be that of the platform docker is being run from.

	```
	[connexion]
	server =
	debug = True
	port = 5000
	keyfile =
	certfile =
	
	[sys-path]
	exposures = ./exposures
	controllers = ./controllers
	
	[postgres]
	host = FQDN_OR_IP
	port = 5432
	database = cmaq
	username = datatrans
	password = datatrans
	```

Ensure the database is running

- Docker implemented database described in [postgres96/README.md](../postgres96/README.md)

To run the server, please execute the following:

```
python3 app.py
```

and open your browser to here:

```
http://localhost:5000/v1/ui/
```

Your Swagger definition lives here:

```
http://localhost:5000/v1/swagger.json
```

## Docker Development

**TODO**

## Production Deployment

**TODO**