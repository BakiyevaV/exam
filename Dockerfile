FROM python:3.11.5-alpine3.18

# Install postgresql-client for pg_isready
# RUN apk update && apk add postgresql-client

# Copy local code to the container image
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Run migrations and start the server
CMD python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000
