FROM python:3.11.5-alpine3.18
COPY . .
RUN pip install -r requirements.txt && python manage.py makemigrations && python manage.py migrate
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000" ]
