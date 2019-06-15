FROM kennethreitz/pipenv as pipenv

ADD . /app
WORKDIR /app

RUN pipenv install --dev \
 && pipenv lock -r > requirements.txt \
 && pipenv run python setup.py bdist_wheel

FROM ubuntu:bionic

ARG DEBIAN_FRONTEND=noninteractive

COPY --from=pipenv /app/dist/*.whl .

RUN set -xe \
 && apt-get update -q \
 && apt-get install -y -q \
        python3-minimal \
        python3-wheel \
        python3-pip \
        uwsgi-plugin-python3 \
 && python3 -m pip install *.whl \
 && apt-get remove -y python3-pip python3-wheel \
 && apt-get autoremove -y \
 && apt-get clean -y \
 && rm -f *.whl \
 && rm -rf /root/.cache \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir -p /app \
 && useradd _uwsgi --no-create-home --user-group

USER _uwsgi

ADD --chown=_uwsgi:_uwsgi static /app/static
ADD --chown=_uwsgi:_uwsgi db /app/db

VOLUME ["/app/db"]

ENTRYPOINT ["/usr/bin/uwsgi", \
            "--master", \
            "--die-on-term", \
            "--plugin", "python3"]
CMD ["--http-socket", "0.0.0.0:8000", \
     "--processes", "4", \
     "--chdir", "/app", \
     "--check-static", "static", \
     "--module", "flask_postits.app:app"]
