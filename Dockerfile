# frontend build
FROM node:18.12

WORKDIR /workdir
COPY package*.json ./
RUN npm install
COPY taskui/ taskui/
RUN npm run build

# pipenv requirements dumper
FROM python:3.10

WORKDIR /workdir
RUN pip install pipenv
COPY Pipfile* ./
RUN pipenv requirements > requirements.txt

# prod
FROM python:3.10-slim

WORKDIR /workdir
COPY --from=1 /workdir/requirements.txt .
RUN pip install -r requirements.txt

COPY config.py cli.py ./
COPY app/ app/
COPY --from=0 /workdir/app/static/js/ app/static/js/
COPY alembic.ini .
COPY alembic/ alembic/
COPY backend/ backend/

CMD gunicorn -w 2 $FLASK_APP:app -b 0.0.0.0:$PORT
