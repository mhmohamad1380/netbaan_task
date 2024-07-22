FROM python:3.11-slim
ENV DJANGO_SUPERUSER_USERNAME admin
ENV DJANGO_SUPERUSER_PASSWORD admin
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
COPY requirements.txt .

RUN pip3 install -r requirements.txt
COPY . .
CMD python3 manage.py makemigrations users --noinput && \
    while ! python3 manage.py migrate users --noinput ; do sleep 1 ; done && \
    python3 manage.py makemigrations --noinput && \
    while ! python3 manage.py migrate --noinput ; do sleep 1 ; done && \
    python3 manage.py collectstatic --noinput && \
    python3 manage.py createsuperuser --user admin --noinput --email test@test.com --noinput ; \
    gunicorn -b 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=library.settings --workers=4 library.wsgi