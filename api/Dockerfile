# api/Dockerfile

FROM python:3.12.4

WORKDIR /app
COPY ./src/ /app/

COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock
RUN pip install pipenv && pipenv install --deploy --system

EXPOSE 8000
CMD ["sh", "entrypoint.sh"]