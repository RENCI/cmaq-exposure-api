## Database

For the purposes of this project the development database will be run locally using Docker.

PostgreSQL 9.6 + PostGIS 2.3

### Populate Sample Data

See [data-sample/README.md](../data-sample) for more information.


### Start the Database

Assumptions

- You are running on a platform where Docker and docker-compose is installed
- You are using an account that has rights to run Docker

From the `postgres96/` directory:

```
Usage: ./start-database.sh
```

Example:

```
$ ./start-database.sh
Building database
Step 1/11 : FROM centos:7
7: Pulling from library/centos
d9aaf4d82f24: Pull complete
Digest: sha256:4565fe2dd7f4770e825d4bd9c761a81b26e49cc9e3c9631c58cfc3188be9505a
Status: Downloaded newer image for centos:7
 ---> d123f4e55e12
Step 2/11 : MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>
 ---> Running in 71cc74345af8
 ---> 69034e4deeb6
...
Step 11/11 : CMD run
 ---> Running in cd8bff19b8f2
 ---> 1c0d316ed4fa
Removing intermediate container cd8bff19b8f2
Successfully built 1c0d316ed4fa
Successfully tagged postgres96_database:latest
Creating network "postgres96_cmaq_exposure_api" with the default driver
Creating database ...
Creating database ... done
Database is running - use your local IP address for connection
```

### Stop/Remove the Database

Attempts to stop and remove any database related Docker containers. Will also remove all database related Docker images if the `--all` flag is used.

From the `postgres96/` directory:

```
Usage: ./stop-database.sh [--all]
```

Example:

```
$ ./stop-database.sh --all
Stopping database ... done
Going to remove database
Removing database ... done
Untagged: postgres96_database:latest
Deleted: sha256:1c0d316ed4fabea33be3ded3f0635df6332a4188432b85a7087626d334124e2a
Deleted: sha256:0d4c782706d82cf28084ffde20a69e51ce538fe5308c9303c388c7d5e880db63
Deleted: sha256:adb633b2e317ced6cec5f3509efbe3ecc944351fad353efa83a22f98b20caa24
Deleted: sha256:7cf9f4890d76fc103cbefa9cc2d2b376275f8c81033ed37a32380ecfa68e1b3b
Deleted: sha256:cf8221441de6ebcd7669ea31c3d87ee0130972243e87f4792b0dbc36e012aa5b
Deleted: sha256:9a87a8e46188cf1a0db8f9dc9b1206cc37130706afd78b1e4514917ef6266978
Deleted: sha256:9080143a44473bdc00dcf23f72cd1b9784a81901eb309c54b2dc1dc38e2dea9f
Deleted: sha256:155855c71d4d3f51d046bf91e3f7f154f47e3ee92b31b1f4ed482393dce9c9a0
Deleted: sha256:55814e6bd7421e995663a1ffd33bf222efe47811b007969bd63cf472e9ec1c97
Deleted: sha256:e4fc91ba4e9893ba26e92c58b1eb856fe7df788942ada24c7c9bcf9202806b28
Deleted: sha256:6f0597bc32dd40e650160f17ec4e7c225213476e2fd02a8833aaebfe75c385e1
Deleted: sha256:69034e4deeb67558bfe61aa22238ac5956efead8aead9ebb2439b774a634a34b
Untagged: centos:7
Untagged: centos@sha256:4565fe2dd7f4770e825d4bd9c761a81b26e49cc9e3c9631c58cfc3188be9505a
Deleted: sha256:d123f4e55e1200156d9cbcf4421ff6d818576e4f1e29320a408c72f022cfd0b1
Deleted: sha256:cf516324493c00941ac20020801553e87ed24c564fb3f269409ad138945948d4
```
