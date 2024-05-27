FROM ubuntu:22.04

RUN apt update
RUN apt install -y python3 python3-pip

COPY ./ /app

CMD [ "python3", "/app/server.py" ]