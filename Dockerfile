FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

ADD requirements.txt /tmp

RUN set -xe \
 && apt-get update -q \
 && apt-get install -y -q \
        python3-minimal \
        python3-pip \
        uwsgi-plugin-python3

RUN set -xe \
 && pip3 install --upgrade setuptools \
 && pip3 install -r /tmp/requirements.txt

RUN set -xe \
 && apt-get remove -y python3-pip \
 && apt-get autoremove -y \
 && apt-get clean -y \
 && rm -rf /root/.cache \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /app \
 && useradd _uwsgi --no-create-home --user-group

USER _uwsgi

ADD --chown=_uwsgi:_uwsgi flask_postits /app

VOLUME ["/app/db"]

ENTRYPOINT ["/usr/bin/uwsgi", \
            "--master", \
            "--die-on-term", \
            "--plugin", "python3"]
CMD ["--http-socket", "0.0.0.0:8000", \
     "--processes", "4", \
     "--chdir", "/app", \
     "-w", "app:app"]
