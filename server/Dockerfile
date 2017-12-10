FROM python:3
MAINTAINER Michael J. Stealey <michael.j.stealey@gmail.com>

# Set default environment variables
# [connexion/api-server]
ENV CONNEXION_SERVER=''
ENV CONNEXION_DEBUG=True
ENV API_SERVER_HOST=localhost
ENV API_SERVER_PORT=5000
ENV API_SERVER_KEYFILE=''
ENV API_SERVER_CERTFILE=''
# [sys-path]
ENV SYS_PATH_EXPOSURES=/cmaq-exposure/exposures
ENV SYS_PATH_CONTROLLERS=/cmaq-exposure/controllers
# [postgres]
ENV POSTGRES_HOST=database
ENV POSTGRES_PORT=5432
ENV POSTGRES_DATABASE=exposures
ENV POSTGRES_USERNAME=datatrans
ENV POSTGRES_PASSWORD=datatrans
ENV POSTGRES_IP=''
ENV SWAGGER_HOST=localhost:5000

COPY . /cmaq-exposure
WORKDIR /cmaq-exposure

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

ENTRYPOINT ["/cmaq-exposure/docker-entrypoint.sh"]
EXPOSE 5000
CMD ["app.py"]
