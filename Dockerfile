FROM python:3.10
LABEL maintainer="Dmitry Sokolov xx.sokolov@gmail.com"
LABEL version="2.0"
ARG workdir=/opt/znt

RUN mkdir -p $workdir
WORKDIR $workdir
RUN pip install --upgrade pip
COPY . .
RUN pip install --no-cache-dir --upgrade -r $workdir/.requirements
ENTRYPOINT ["python", "znt.py", "api"]

