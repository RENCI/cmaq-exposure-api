FROM centos:7
#FROM centos:6
MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>

ENV LANGUAGE="en_US.UTF-8"
ENV LANG="en_US.UTF-8"
ENV LC_ALL="en_US.UTF-8"

RUN yum install -y \
  https://download.postgresql.org/pub/repos/yum/9.6/redhat/rhel-7-x86_64/pgdg-centos96-9.6-3.noarch.rpm \
  epel-release \
  && yum makecache fast && yum install -y \
  sudo \
  postgresql96 \
  postgresql96-server \
  postgresql96-libs \
  postgresql96-contrib \
  postgresql96-devel \
# armadillo may be causing issues for centos7
#  armadillo-devel \
#  armadillo \
  postgis23_96 \
  postgis23_96-client \
  ogr_fdw96

ADD docker-entrypoint.sh /docker-entrypoint.sh
VOLUME ["/var/lib/pgsql"]

EXPOSE 5432
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["run"]
