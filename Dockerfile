FROM python:3.8.7-alpine as base
WORKDIR /app
RUN apk add --no-cache \
    ca-certificates
RUN apk update
#&& \
#    apk upgrade --available

RUN apk add --no-cache build-base
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
COPY requirements.txt .
RUN apk add libffi-dev openssl-dev python3-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM base as release
EXPOSE 7000
WORKDIR /app/code
# CMD python manage.py runserver --settings APIBackendService.settings.development 0.0.0.0:7000
CMD [ \
"gunicorn", \
"--workers=3", \
"--bind", \
"0.0.0.0:7000", \
"APIBackendService.wsgi:application" \
]
