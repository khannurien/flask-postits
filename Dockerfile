FROM python:3.7.3-alpine3.9 as base

FROM base AS build

RUN apk add --update --no-cache \
 g++ gcc libxslt-dev musl-dev linux-headers

RUN mkdir /packages
WORKDIR /packages

ADD requirements.txt /requirements.txt

RUN python3.7 -m pip install -r /requirements.txt -t /packages

FROM base

RUN mkdir -p /app \
 && addgroup _uwsgi \
 && adduser -D --ingroup _uwsgi --no-create-home _uwsgi

USER _uwsgi

ADD --chown=_uwsgi:_uwsgi flask_postits /app
COPY --from=build /packages /app

VOLUME ["/app/db"]

#ENTRYPOINT ["/bin/sh"]
ENTRYPOINT ["python3.7 -c uwsgi", \
            "--master", \
            "--die-on-term"]
CMD ["--http-socket", "0.0.0.0:8000", \
     "--processes", "4", \
     "--chdir /app", \
     "-w", "app:app"]
