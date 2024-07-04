FROM python:3.11.5-alpine3.18

# Install postgresql-client for pg_isready
RUN apk update && apk add postgresql-client

COPY . .

RUN pip install -r requirements.txt

#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh

CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]
