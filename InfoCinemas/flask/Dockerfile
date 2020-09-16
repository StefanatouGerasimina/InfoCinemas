FROM ubuntu:18.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask pymongo
RUN mkdir /app
COPY . /app
EXPOSE 9000
WORKDIR /app
ENTRYPOINT ["python3","-u","main.py"]