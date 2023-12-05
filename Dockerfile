FROM python:3.9
ENV STATIC_ROOT="/static"
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --no-input
RUN sphinx-build -b html docs/ /static/doc
CMD python manage.py runserver
