# cmaq-exposure-api

The CMAQ Exposure API is a RESTful data service implemented in [Swagger](https://swagger.io/) using [OpenAPI 2.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md) standards and provides environmental [CMAQ](https://www.cmascenter.org/cmaq/) exposures data based on GeoCodes (latitude,longitude) and dates.

## Development Environment

Preliminary assumptions

- Python 3 is available on the host
- Docker and docker-compose are available on the host

**PostgreSQL 9.6 / PostGIS 2.3**:
 
- Docker-compose based development database
- See [README.md](postgres96/README.md) in `postgres96/`

**Sample Data**:
 
- Initialization scripts for PostgreSQL cmaq database and tables
- Representive CMAQ source data in NetCDF format
- See [README.md](data-sample/README.md) in `data-sample/`

**Data Tools**:

- Pre-ingest checks to validate CMAQ source data against the PostgreSQL database schema
- Ingest scripts for reading the CMAQ source data into the PostgreSQL database
- See [README.md](data-tools/README.md) in `data-tools/`

**Server**

- TODO

**Client**

- TODO

**Swagger Editor**

- TODO

### About CMAQ / CMAS

CMAQ is an active open-source development project of the U.S. EPA that consists of a suite of programs for conducting air quality model simulations. CMAQ is supported and distributed by the [Community Modeling and Analysis System (CMAS)](https://www.cmascenter.org/index.cfm) Center.

CMAQ combines current knowledge in atmospheric science and air quality modeling with multi-processor computing techniques in an open-source framework to deliver fast, technically sound estimates of ozone, particulates, toxics, and acid deposition.

