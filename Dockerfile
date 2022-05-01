FROM python:3.11.0a7-alpine3.15
WORKDIR /docker_week1
ADD . /docker_week1
RUN pip install -r requirements.txt
CMD ["python","app.py"]
EXPOSE 5000

