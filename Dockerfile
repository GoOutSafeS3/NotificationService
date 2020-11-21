FROM python:3.7-alpine3.11

WORKDIR /app
EXPOSE 8080

COPY requirements.txt ./
RUN ["pip", "install", "-r", "requirements.txt"]
COPY __init__.py app.py database.py swagger.yml ./

CMD python app.py