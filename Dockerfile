FROM python:3.7.3-alpine3.9 as base

FROM base AS build

RUN apk add --update --no-cache \
 g++ gcc libxslt-dev

RUN mkdir /packages
WORKDIR /packages

ADD requirements.txt /requirements.txt

RUN python3.7 -m pip install -r /requirements.txt -t /packages

FROM base

RUN apk add --update --no-cache \
 uwsgi uwsgi-python3

RUN mkdir -p /app \
 && addgroup _uwsgi \
 && adduser -D --ingroup _uwsgi --no-create-home _uwsgi

USER _uwsgi

ADD --chown=_uwsgi:_uwsgi flask_postits /app
COPY --chown=_uwsgi:_uwsgi --from=build /packages /app

VOLUME ["/app/db"]

ENTRYPOINT ["uwsgi", \
            "--master", \
            "--die-on-term", \
            "--plugin", "python3"]
CMD ["--http-socket", "0.0.0.0:8000", \
     "--processes", "4", \
     "--chdir", "/app", \
     "-w", "app:app"]
