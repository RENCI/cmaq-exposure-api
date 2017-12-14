# cmaq-exposure-api

The CMAQ Exposure API is a RESTful data service implemented in [Swagger](https://swagger.io/) using [OpenAPI 2.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md) standards and provides environmental [CMAQ](https://www.cmascenter.org/cmaq/) exposures data based on GeoCodes (latitude, longitude) and dates.

## TL;DR

```
cd cmaq-exposure-api
./run-cmaq-api.sh
```
Open [http://localhost:5000/v1/ui/#/default](http://localhost:5000/v1/ui/#/default) in your browser when the script completes.

## Development Environment

**Preliminary assumptions**

- Docker and docker-compose are available on the host
	- Generally executed using a `bash` script that performs `docker` or `docker-compose` calls

- Python 3 is available on the host
	- Generally executed using `virtualenv` in the manner:

		```
		$ virtualenv -p /PATH_TO/python3 venv
		$ source venv/bin/activate
		(venv)$ pip install -r requirements.txt
		(venv)$ python SOMETHING.py [/PATH_TO/SOME_FILE]
		```

### Repository structure

The repository has been broken into multiple sections based on the infrastructure, application or task being addressed. Each section is briefly described here with a more detailed overview as a `README.md` file at each primary directory level.
		
**PostgreSQL 9.6 / PostGIS 2.3**:
 
- Docker-compose based development database
- See [README.md](postgres96/README.md) in `postgres96/`

**Sample Data**:
 
- Initialization scripts for PostgreSQL cmaq database and tables
- Representive CMAQ data in SQL format
- See [README.md](data-sample/README.md) in `data-sample/`

**Data Tools**:

- `pre-ingest`: checks to validate CMAQ source data against the PostgreSQL database schema
- `ingest`: scripts for reading the CMAQ source data into the PostgreSQL database
- `postgres-functions`: indexes and function generation tools
- `post-ingest`: scripts for updating the aggregate values of newly ingested data
- See [README.md](data-tools/README.md) in `data-tools/`

**Server**

- Python3/Flask based API server
- Docker implementation of the API server
- See [README.md](server/README.md) in `server/`

**Client**

- TODO

**Swagger Editor**

- TODO


See [INSTALL.md](INSTALL.md) for full details.

### About CMAQ / CMAS

CMAQ is an active open-source development project of the U.S. EPA that consists of a suite of programs for conducting air quality model simulations. CMAQ is supported and distributed by the [Community Modeling and Analysis System (CMAS)](https://www.cmascenter.org/index.cfm) Center.

CMAQ combines current knowledge in atmospheric science and air quality modeling with multi-processor computing techniques in an open-source framework to deliver fast, technically sound estimates of ozone, particulates, toxics, and acid deposition.

